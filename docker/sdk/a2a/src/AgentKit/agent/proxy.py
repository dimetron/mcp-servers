"""A2A Proxy Agent Module

This module provides a proxy agent that forwards requests to an A2A (Agent-to-Agent) server.
It acts as a bridge between the ADK framework and external A2A services.
"""

import logging
from typing import AsyncGenerator, Optional
import uuid

from a2a.client import A2AClient
from a2a.types import (
    AgentCard,
    Message,
    MessageSendParams,
    Part,
    Role,
    SendMessageRequest,
    SendStreamingMessageRequest,
    TextPart,
)
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.genai import types
import httpx

from .agent_id import make_agent_id

logger = logging.getLogger(__name__)


class A2AProxyAgent(BaseAgent):
    """Non-LLM agent that proxies calls to an A2A server"""

    # Declare fields as class attributes for Pydantic model
    a2a_url: str
    output_key: str
    httpx_client: Optional[httpx.AsyncClient] = None
    client: Optional[A2AClient] = None

    def __init__(self, a2a_url: str):
        name = make_agent_id(a2a_url)
        super().__init__(name=name, a2a_url=a2a_url, output_key=a2a_url)  # type: ignore

    async def _initialize_client(self):
        """Initialize A2A client by fetching agent card"""
        if self.client is None:
            self.httpx_client = httpx.AsyncClient()

            # Fetch agent card first (optional but recommended)
            try:
                response = await self.httpx_client.get(
                    f"{self.a2a_url}/.well-known/agent.json"
                )
                agent_card_data = response.json()
                agent_card = AgentCard(**agent_card_data)
                agent_card.url = self.a2a_url

                # Create client with agent card
                self.client = A2AClient(
                    httpx_client=self.httpx_client,
                    agent_card=agent_card,
                )
            except Exception:
                # Fallback to URL-only initialization
                self.client = A2AClient(
                    httpx_client=self.httpx_client, url=self.a2a_url
                )

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """Agent execution: forwards directly to A2A"""

        # Initialize client if needed
        await self._initialize_client()

        if self.client is None:
            raise RuntimeError("client did not properly initialize")

        # Get content to send
        content_to_send: str = ""
        if ctx.user_content and ctx.user_content.parts:
            content_to_send = ctx.user_content.parts[0].text or ""
        else:
            content_to_send = self._get_input_from_state(ctx)
        try:
            # Try streaming first, fallback to non-streaming if needed
            streaming_request = SendStreamingMessageRequest(
                id=str(uuid.uuid4()), params=make_message_send_params(content_to_send)
            )

            # Collect streaming response
            final_result = ""
            try:
                stream_response = self.client.send_message_streaming(streaming_request)

                async for chunk in stream_response:
                    chunk_content = ""

                    # Extract content from A2A streaming response
                    if (
                        (root := getattr(chunk, "root", None))
                        and (result := getattr(root, "result", None))
                        and (artifact := getattr(result, "artifact", None))
                    ):
                        if parts := getattr(artifact, "parts", None):
                            for part in parts:
                                if (root := getattr(part, "root", None)) and (
                                    text := getattr(root, "text", None)
                                ):
                                    chunk_content = str(text)
                                    break
                                elif text := getattr(part, "text", None):
                                    chunk_content = str(text)
                                    break
                    elif result := getattr(chunk, "result", None):
                        if content := getattr(result, "content", None):
                            chunk_content = str(content)
                        elif message := getattr(result, "message", None):
                            if content := getattr(message, "content", None):
                                chunk_content = str(content)
                        elif text := getattr(result, "text", None):
                            chunk_content = str(text)
                    elif content := getattr(chunk, "content", None):
                        chunk_content = str(content)
                    elif text := getattr(chunk, "text", None):
                        chunk_content = str(text)

                    if chunk_content:
                        final_result += chunk_content

            except Exception as e:
                logger.warning("Streaming failed, falling back to non-streaming: %s", e)
                # Fallback to non-streaming if streaming fails
                request = SendMessageRequest(
                    id=str(uuid.uuid4()),
                    params=make_message_send_params(content_to_send),
                )
                response = await self.client.send_message(request)

                # Handle non-streaming response
                if result := getattr(response, "result", None):
                    if content := getattr(result, "content", None):
                        final_result = content
                    elif message := getattr(result, "message", None):
                        if content := getattr(message, "content", None):
                            final_result = content
                    else:
                        final_result = str(result)
                else:
                    final_result = str(response)

            # Save to state
            if self.output_key:
                ctx.session.state[self.output_key] = final_result

            # Return result
            yield Event(
                author=self.name,
                content=types.Content(
                    role="model", parts=[types.Part(text=final_result)]
                ),
                actions=EventActions(
                    state_delta={self.output_key: final_result}
                    if self.output_key
                    else {}
                ),
                turn_complete=True,
            )

        except Exception as e:
            yield Event(
                author=self.name,
                content=types.Content(
                    role="model",
                    parts=[types.Part(text=f"Error calling A2A agent: {str(e)}")],
                ),
                error_message=str(e),
                turn_complete=True,
            )

    async def _run_live_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """Live (audio/video) mode is not supported for A2A proxy agents"""
        yield Event(
            author=self.name,
            content=types.Content(
                role="model",
                parts=[
                    types.Part(
                        text="A2A proxy agents do not support live audio/video mode"
                    )
                ],
            ),
            error_message="Live mode not supported",
            turn_complete=True,
        )

    def _get_input_from_state(self, ctx: InvocationContext) -> str:
        """Retrieves input from state for non-first agents in sequence"""
        state = ctx.session.state

        # Look for output from previous agent
        for key in reversed(list(state.keys())):
            if key.endswith("_result") or key.endswith("_output"):
                return state[key]

        # Fallback: take original user message
        if ctx.session.events:
            for event in ctx.session.events:
                if not event.content or event.content.role != "user":
                    continue
                if parts := event.content.parts:
                    for p in parts:
                        if text := p.text:
                            return text

        return "No input found"

    async def cleanup(self):
        """Clean up the httpx client"""
        if self.httpx_client:
            await self.httpx_client.aclose()


def make_message_send_params(text: str) -> MessageSendParams:
    # Create the message payload based on the A2A example and your curl test
    message_id = str(uuid.uuid4())
    part = Part(root=TextPart(text=text))
    message = Message(role=Role.user, messageId=message_id, parts=[part])
    return MessageSendParams(message=message)
