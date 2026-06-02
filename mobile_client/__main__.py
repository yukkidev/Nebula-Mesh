from mobile_client.config import load_config
from mobile_client.server import MobileInputServer


def main() -> None:
    cfg = load_config()
    server = MobileInputServer(config=cfg)
    server.start()


if __name__ == "__main__":
    main()
