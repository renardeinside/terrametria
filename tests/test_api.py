from fastapi.testclient import TestClient
from terrametria.backend import app
import io
import pyarrow as pa

client = TestClient(app)


def test_get_density():
    response = client.get("/api/density")
    assert response.status_code == 200
    stream = io.BytesIO(response.read())

    # Deserialize the Arrow IPC stream
    reader = pa.ipc.open_stream(stream)

    # Read the Arrow table from the stream
    df = reader.read_all().to_pandas()

    assert len(df) > 0