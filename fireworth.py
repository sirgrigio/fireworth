from fire import Fire
from pathlib import Path

class Fireworth:

    def __init__(
        self,
        directory: Path = Path.home().joinpath('.fireworth')
    ):
        self.directory = directory

    def balancesheet():
        pass


if __name__ == '__main__':
    Fire(Fireworth)
