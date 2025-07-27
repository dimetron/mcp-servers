import logging
from pathlib import Path
import sys
import warnings

import click
import dotenv
import uvicorn

sys.path.append(str(Path(__file__).parent / "src"))

from AgentKit.agent import Agent

root_agent = None

# Suppress Pydantic serialization warnings from LiteLLMAdd commentMore actions
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic.main")
logging.getLogger("google.adk").setLevel(logging.INFO)
logging.getLogger("LiteLLM").setLevel(logging.WARNING)  # Much less verbose
logging.getLogger("litellm").setLevel(logging.WARNING)  # Also reduce this
logging.getLogger("httpx").setLevel(logging.WARNING)  # Reduce HTTP logs
logging.getLogger("httpcore").setLevel(logging.WARNING)  # Reduce HTTP core logs


@click.command()
@click.argument(
    "config_file", envvar="AGENT_CONFIG", type=click.Path(exists=True, dir_okay=False)
)
@click.option("--host", type=str, default="0.0.0.0")
@click.option("--port", type=int, default=9001)
def main(config_file: str, host: str, port: int) -> None:
    logging.basicConfig(level=logging.INFO)
    dotenv.load_dotenv()
    agent = Agent.from_yaml_filename(config_file)
    print("Hello", agent)
    app = agent.app(port)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
