from input_client.config import load_config
from input_client.server import InputServer


def main() -> None:
    cfg = load_config()
    server = InputServer(config=cfg)
    server.start()


if __name__ == "__main__":
    main()
