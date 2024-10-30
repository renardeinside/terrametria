from importlib.resources import files
from pathlib import Path
from typing import Generator
from fastapi import Depends, FastAPI
from contextlib import contextmanager
from databricks import sql
from databricks.sql.client import Connection
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from terrametria.config import Config
import pyarrow as pa
import io
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

STATIC_ASSETS_PATH = Path(str(files("terrametria"))) / Path("static")


def config() -> Config:
    load_dotenv()  # Load environment variables from .env file if present
    return Config.from_env()


@contextmanager
def session(config: Config = Depends(config)) -> Generator[Connection, None, None]:
    with sql.connect(
        server_hostname=config.endpoint.host,
        http_path=config.endpoint.http_path,
        client_id=config.endpoint.client_id,
        client_secret=config.endpoint.client_secret,
    ) as connection:
        yield connection


app = FastAPI()
ui_app = StaticFiles(directory=STATIC_ASSETS_PATH, html=True)
api_app = FastAPI(config=Depends(config))

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


@app.get("/density")
def get_density(
    session: Connection = Depends(session), config: Config = Depends(config)
):
    with session.cursor() as cursor:
        cursor.execute(
            f"SELECT * FROM {config.catalog}.{config.schema}.{config.density_table}"
        )
        table: pa.Table = cursor.fetchall_arrow()

        def stream_arrow_data():
            sink = io.BytesIO()
            writer = pa.ipc.new_stream(sink, table.schema)
            writer.write_table(table)
            sink.seek(0)

            while chunk := sink.read(1024 * 1024):  # 1MB
                yield chunk

        return StreamingResponse(
            stream_arrow_data(), media_type="application/octet-stream"
        )
