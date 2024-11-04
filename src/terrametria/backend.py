from importlib.resources import files
from pathlib import Path
from typing import Annotated, Generator
from fastapi import Depends, FastAPI
from databricks import sql
from databricks.sql.client import Connection
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from terrametria.config import Config
import pyarrow as pa
import io
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from terrametria.logger import logger
from databricks.sdk.core import oauth_service_principal

STATIC_ASSETS_PATH = Path(str(files("terrametria"))) / Path("static")
DOTENV_FILE = Path(__file__).parent.parent.parent / Path(".env")


def config() -> Config:
    logger.info("Loading configuration")
    if DOTENV_FILE.exists():
        logger.info(f"Loading configuration from {DOTENV_FILE}")
        load_dotenv(DOTENV_FILE)
    else:
        logger.info(f"Loading configuration from environment variables")
    return Config.from_env()


def connection(
    config: Annotated[Config, Depends(config)],
) -> Generator[Connection, None, None]:
    logger.info(
        f"Connecting to Databricks SQL at {config.endpoint.host}{config.endpoint.http_path}"
    )

    def credential_provider():
        return oauth_service_principal(config.endpoint.to_databricks_config())

    with sql.connect(
        server_hostname=config.endpoint.host,
        http_path=config.endpoint.http_path,
        credentials_provider=credential_provider,
        use_cloud_fetch=True,
    ) as connection:
        logger.info("Connected to Databricks SQL")
        yield connection

    logger.info("Disconnected from Databricks SQL")


def density_data_stream(
    connection: Annotated[Connection, Depends(connection)],
    config: Annotated[Config, Depends(config)],
) -> Generator[bytes, None, None]:
    logger.info(
        f"Fetching density data from {config.catalog}.{config.schema}.{config.density_table}"
    )
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT * FROM {config.catalog}.{config.schema}.{config.density_table} where cntr_id = 'DE'" 
        )
        table: pa.Table = cursor.fetchall_arrow()

        logger.info(f"Streaming density data")

        def stream_arrow_data():
            sink = io.BytesIO()
            writer = pa.ipc.new_stream(sink, table.schema)
            writer.write_table(table)
            sink.seek(0)

            while chunk := sink.read(1024 * 1024):  # 1MB
                yield chunk

            logger.info(f"Streaming completed")

        return stream_arrow_data()


app = FastAPI()
ui_app = StaticFiles(directory=STATIC_ASSETS_PATH, html=True)
api_app = FastAPI(dependencies=[Depends(config)])

origins = [
    "http://localhost:6006",
    "http://0.0.0.0:6006",
    "http://localhost:5173",
    "http://0.0.0.0:5173",
]

# Make sure CORS is applied to both app and api_app
api_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/api", api_app)
app.mount("/", ui_app)


@app.exception_handler(404)
async def client_side_routing(_, __):
    return FileResponse(STATIC_ASSETS_PATH / "index.html")


@api_app.get("/density")
def get_density(
    density_data_stream: Generator[bytes, None, None] = Depends(density_data_stream)
):
    return StreamingResponse(
        density_data_stream, media_type="application/octet-stream"
    )
