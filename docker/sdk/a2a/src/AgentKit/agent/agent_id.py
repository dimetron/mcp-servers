import re


def make_agent_id(name: str) -> str:
    return re.sub(r"\W+", "_", name)
