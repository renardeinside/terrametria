from pyspark.sql import SparkSession
from terrametria.config import Config
import requests
from pathlib import Path
import pandas as pd
import pyspark.sql.functions as F
from terrametria.logger import logger
from pyspark.sql import DataFrame, Column
import geopandas as gpd


class Loader:
    NUTS_URL = "https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_01M_2024_3035.geojson"
    DENSITY_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/DEMO_R_D3DENS?format=JSON&lang=EN&time=2022"
    COUNTRIES_URL = "https://gisco-services.ec.europa.eu/distribution/v2/countries/geojson/CNTR_RG_01M_2024_3035.geojson"

    def __init__(self, config: Config):
        self.config = config
        self.spark = SparkSession.builder.getOrCreate()

    @property
    def volume_path(self) -> Path:
        return (
            Path("/Volumes/")
            / self.config.catalog
            / self.config.schema
            / self.config.volume
        )

    @property
    def nuts_path(self) -> Path:
        return self.volume_path / "nuts.geojson"

    @property
    def density_path(self) -> Path:
        return self.volume_path / "density.json"

    @property
    def countries_path(self) -> Path:
        return self.volume_path / "countries.geojson"

    @property
    def output_path(self) -> Path:
        return self.volume_path / "enriched_density.geojson"

    @staticmethod
    def load_file(url: str, output_path: Path, chunk_size: int = 1024 * 1024):
        logger.info(f"Downloading {url} to {output_path}")
        response = requests.get(url)
        with output_path.open("wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                f.write(chunk)
        logger.info(f"Downloaded {url} to {output_path}")

    def _prepare_catalog(self):
        self.spark.sql(f"CREATE CATALOG IF NOT EXISTS {self.config.catalog}")
        self.spark.sql(
            f"CREATE SCHEMA IF NOT EXISTS {self.config.catalog}.{self.config.schema}"
        )
        self.spark.sql(
            f"CREATE VOLUME IF NOT EXISTS {self.config.catalog}.{self.config.schema}.{self.config.volume}"
        )

    @staticmethod
    def convert_and_explode(
        column: str, map_schema: str, key_alias: str, value_alias: str
    ) -> Column:
        map_conversion = F.from_json(F.to_json(F.col(column)), map_schema)
        return F.explode(map_conversion).alias(key_alias, value_alias)

    def get_density_df(self) -> pd.DataFrame:
        density_base = self.spark.read.format("json").load(self.density_path.as_posix())

        density = density_base.select(
            self.convert_and_explode("value", "map<string, double>", "index", "density")
        )

        indexes = density_base.select(
            self.convert_and_explode(
                "dimension.geo.category.index",
                "map<string, bigint>",
                "nats_id",
                "index",
            )
        )

        labels = density_base.select(
            self.convert_and_explode(
                "dimension.geo.category.label",
                "map<string, string>",
                "nats_id",
                "long_label",
            )
        )

        return (
            density.join(indexes, on="index", how="inner")
            .join(labels, on="nats_id", how="inner")
            .toPandas()
        )

    def get_nuts_df(self) -> gpd.GeoDataFrame:
        nuts = gpd.read_file(self.nuts_path)
        nuts.columns = [c.lower() for c in nuts.columns]
        return nuts

    def get_countries_df(self) -> gpd.GeoDataFrame:
        countries = gpd.read_file(self.countries_path)
        countries.columns = [c.lower() for c in countries.columns]
        countries = countries[
            ["cntr_id", "name_engl", "cntr_name"]
        ]  # only keep the columns we need
        countries.rename(columns={"cntr_id": "cntr_code"}, inplace=True)
        return countries

    def get_full_df(self) -> gpd.GeoDataFrame:
        nuts = self.get_nuts_df()
        density = self.get_density_df()
        countries = self.get_countries_df()

        return nuts.merge(density, on="nuts_id").merge(countries, on="cntr_code")

    def run(self):
        logger.info("Preparing population density data")
        self._prepare_catalog()

        self.load_file(url=self.COUNTRIES_URL, output_path=self.countries_path)
        self.load_file(url=self.NUTS_URL, output_path=self.nuts_path)
        self.load_file(url=self.DENSITY_URL, output_path=self.density_path)

        full_df = self.get_full_df()
        full_df.to_file(self.output_path, driver="GeoJSON")
        logger.info("Finished preparing population density data")
