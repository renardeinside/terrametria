from __future__ import annotations
from dataclasses import dataclass
import sys

from terrametria.logger import logger
import os
from databricks.sdk.core import Config as DatabricksConfig


@dataclass
class EndpointConfig:
    host: str
    http_path: str
    client_id: str
    client_secret: str

    def to_databricks_config(self) -> DatabricksConfig:
        return DatabricksConfig(
            client_id=self.client_id,
            client_secret=self.client_secret,
            host=f"https://{self.host}",
        )


@dataclass
class Config:
    catalog: str
    schema: str
    volume: str
    density_table: str = "population_density"
    endpoint: EndpointConfig | None = None

    @staticmethod
    def from_args() -> Config:
        args = sys.argv[1:]
        logger.info(f"Arguments: {args}")
        catalog = args[0] if len(args) > 0 else "main"
        schema = args[1] if len(args) > 1 else "terrametria"
        volume = args[2] if len(args) > 2 else "raw"
        return Config(catalog, schema, volume)

    @staticmethod
    def from_env() -> Config:
        catalog = os.getenv("TERRAMETRIA_CATALOG", "main")
        schema = os.getenv("TERRAMETRIA_SCHEMA", "terrametria")
        volume = os.getenv("TERRAMETRIA_VOLUME", "raw")

        endpoint_cfg = EndpointConfig(
            host=os.environ["DATABRICKS_HOST"],
            http_path=os.environ["DATABRICKS_HTTP_PATH"],
            client_id=os.environ["DATABRICKS_CLIENT_ID"],
            client_secret=os.environ["DATABRICKS_CLIENT_SECRET"],
        )
        return Config(
            catalog=catalog,
            schema=schema,
            volume=volume,
            endpoint=endpoint_cfg,
        )
