from terrametria.config import Config
from terrametria.loader import Loader


def loader():
    config = Config.from_args()
    loader = Loader(config=config)
    loader.run()
