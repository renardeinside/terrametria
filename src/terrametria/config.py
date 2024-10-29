from __future__ import annotations
from dataclasses import dataclass
import sys

from terrametria import logger


@dataclass
class Config:
    catalog: str = "main"
    schema: str = "terrametria"
    volume: str = "raw"

    @staticmethod
    def from_args() -> Config:
        args = sys.argv[1:]
        logger.info(f"Arguments: {args}")
        catalog = args[0] if len(args) > 0 else "main"
        schema = args[1] if len(args) > 1 else "terrametria"
        volume = args[2] if len(args) > 2 else "raw"
        return Config(catalog, schema, volume)
