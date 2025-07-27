from .server import serve


def main():
    """MCP Time Server - Time and timezone conversion functionality for MCP"""
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(
        description="give a model the ability to handle time queries and timezone conversions"
    )
    parser.add_argument("--${DOCKER_REGISTRY_TAG}-timezone", type=str, help="Override ${DOCKER_REGISTRY_TAG} timezone")

    args = parser.parse_args()
    asyncio.run(serve(args.${DOCKER_REGISTRY_TAG}_timezone))


if __name__ == "__main__":
    main()
