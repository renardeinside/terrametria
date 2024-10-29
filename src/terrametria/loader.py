from pyspark.sql import SparkSession
from terrametria.config import Config
import requests
from pathlib import Path
import pandas as pd
import numpy as np
import json
import pyspark.sql.functions as F
from terrametria.logging import logger
from pyspark.sql import DataFrame


class Loader:
    NUTS_URL = "https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_01M_2024_3035.geojson"
    DENSITY_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/DEMO_R_D3DENS?format=JSON&lang=EN&time=2022"
    COUNTRIES_URL = "https://gisco-services.ec.europa.eu/distribution/v2/countries/geojson/CNTR_RG_01M_2024_3035.geojson"

    def __init__(self, config: Config = Config()):
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

    def get_density_df(self) -> DataFrame:
        density_data = json.loads(self.density_path.read_text())
        density = pd.Series(density_data["value"], name="density")
        density.index = density.index.astype(np.int64)

        indexes = pd.Series(
            {
                v: k
                for k, v in density_data["dimension"]["geo"]["category"][
                    "index"
                ].items()
            },
            name="label",
        )
        labels = pd.Series(
            density_data["dimension"]["geo"]["category"]["label"], name="long_label"
        )

        density_df = self.spark.createDataFrame(
            density.to_frame()
            .join(indexes, how="inner")
            .join(labels, how="inner", on="label")
            .reset_index()
            .rename(columns={"index": "area_id", "label": "nuts_id"})
        )
        return density_df

    def get_nuts_df(self) -> DataFrame:
        nuts3_raw_df = self.spark.read.format("json").load(str(self.nuts_path))

        nuts3_df = nuts3_raw_df.select(
            F.explode(F.col("features")).alias("data")
        ).select(
            F.col("data.properties.NUTS_ID").alias("nuts_id"),
            F.col("data.properties.CNTR_CODE").alias("cntr_id"),
            F.col("data.geometry"),
            F.col("data.properties"),
        )
        return nuts3_df

    def get_countries_df(self) -> DataFrame:
        countries_df = (
            self.spark.read.format("json")
            .load(str(self.countries_path))
            .select(F.explode(F.col("features")).alias("data"))
            .select(
                F.col("data.properties.CNTR_ID").alias("cntr_id"),
                F.col("data.properties.CNTR_NAME").alias("cntr_name_nat"),
                F.col("data.properties.NAME_ENGL").alias("cntr_name_engl"),
            )
            .distinct()
        )
        return countries_df

    def get_full_df(self) -> DataFrame:
        density_df = self.get_density_df()
        nuts_df = self.get_nuts_df()
        countries_df = self.get_countries_df()

        mapped_df = density_df.join(nuts_df, on="nuts_id", how="inner").join(
            countries_df, on="cntr_id", how="inner"
        )
        return mapped_df

    def run(self):
        self._prepare_catalog()

        self.load_file(url=self.COUNTRIES_URL, output_path=self.countries_path)
        self.load_file(url=self.NUTS_URL, output_path=self.nuts_path)
        self.load_file(url=self.DENSITY_URL, output_path=self.density_path)

        full_df = self.get_full_df()
        full_df.write.format("delta").mode("overwrite").save(
            f"{self.config.catalog}.{self.config.schema}.population_density"
        )
        logger.info("Loaded population density data")
