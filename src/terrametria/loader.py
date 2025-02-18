import pyproj
from pyspark.sql import SparkSession
from terrametria.config import Config
import requests
from pathlib import Path
import pandas as pd
import pyspark.sql.functions as F
from terrametria.logger import logger
from pyspark.sql import DataFrame, Column
import geopandas as gpd
import zipfile
import io


class Loader:
    # link to the CSV-formatted population density data for Germany
    SOURCE_URL = "https://data.humdata.org/dataset/7d08e2b0-b43b-43fd-a6a6-a308f222cdb2/resource/77a44470-f80a-44be-9bb2-3e904dbbe9b1/download/population_deu_2019-07-01.csv.zip"

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

    @staticmethod
    def load_file_and_unzip(url: str, output_path: Path):
        response = requests.get(url)
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall(output_path)

    def _prepare_catalog(self):
        # self.spark.sql(f"CREATE CATALOG IF NOT EXISTS {self.config.catalog}")
        # self.spark.sql(
        #     f"CREATE SCHEMA IF NOT EXISTS {self.config.catalog}.{self.config.schema}"
        # )
        self.spark.sql(
            f"CREATE VOLUME IF NOT EXISTS {self.config.catalog}.{self.config.schema}.{self.config.volume}"
        )

    def run(self):
        logger.info("Preparing population density data")
        self._prepare_catalog()

        store_path = self.volume_path / "population"

        self.load_file_and_unzip(self.SOURCE_URL, store_path)

        src = (
            self.spark.read.format("csv")
            .option("inferSchema", True)
            .option("header", True)
            .load(store_path.as_posix())
            .withColumnRenamed("Lat", "lat")
            .withColumnRenamed("Lon", "lon")
            .withColumnRenamed("Population", "population")
        )
        src.write.format("delta").mode("overwrite").saveAsTable(
            self.config.full_table_name
        )
        logger.info("Finished preparing population density data")
