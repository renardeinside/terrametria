from contextlib import asynccontextmanager
from importlib.resources import files
from pathlib import Path
from typing import Annotated, Callable, Generator
from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from terrametria.config import Config
import pyarrow as pa
import io
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from terrametria.logger import logger
from databricks.sdk import WorkspaceClient
from functools import lru_cache

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


@lru_cache
def density_file(
    config: Annotated[Config, Depends(config)]
) -> Generator[bytes, None, None]:
    logger.info(f"Loading density file")
    w = WorkspaceClient(config=config.endpoint.to_databricks_config())
    response = w.files.download(config.output_path.as_posix())
    bytes_io = io.BytesIO(response.contents.read())
    logger.info(f"Loaded density file")

    def generator():
        bytes_io.seek(0)
        yield from bytes_io

    return generator


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
    density_data_stream: Annotated[Generator[bytes, None, None], Depends(density_file)]
):
    return StreamingResponse(density_data_stream(), media_type="application/geo+json")
