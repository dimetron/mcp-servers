import os

root_agent = None

if config := os.getenv("AGENT_CONFIG"):
    from .agent import Agent

    root_agent = Agent.from_yaml_filename(config).build_agent()
