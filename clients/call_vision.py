import base64
import requests
from pathlib import Path


API = "http://127.0.0.1:8000/v1/vision/predict"


def encode_image(path: str) -> str:
    data = Path(path).read_bytes()
    return "data:image/jpeg;base64," + base64.b64encode(data).decode("utf-8")


if __name__ == "__main__":
    img_path = str(Path(__file__).resolve().parents[1] / "models" / "test.jpg")
    payload = {"image": encode_image(img_path)}
    r = requests.post(API, json=payload, timeout=300)
    print(r.status_code)
    print(r.json())


