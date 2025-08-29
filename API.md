# Tài liệu API – AI Server

API cung cấp 2 chức năng chính: phân tích ảnh (vision) và phân tích hội thoại y khoa (text). Tất cả trả về JSON.

## Thông tin chung
- Base URL mặc định: `http://127.0.0.1:8000`
- Phiên bản: `v1`
- Content-Type: `application/json`
- Xác thực: Không yêu cầu (có thể bổ sung sau)

## Khởi chạy server
```bash
python ai_server/run_server.py
# hoặc
python -m ai_server.run_server
```

Biến môi trường (tùy chọn):
- `AI_SERVER_HOST` (mặc định `0.0.0.0`)
- `AI_SERVER_PORT` (mặc định `8000`)
- `VISION_KERAS_FILE` (mặc định `DermaAI.keras`)
- `.env` support: tạo file `ai_server/.env` hoặc copy `ai_server/ENV_EXAMPLE.txt` thành `.env` và điền khóa

Yêu cầu model đặt trong thư mục `ai_server/models/`:
- Vision: file Keras, ví dụ `DermaAI.keras`
- Text: một file GGUF, ví dụ `tinyllama-1.1b-chat-v1.0.Q8_0.gguf`

## Sức khỏe hệ thống
### GET /health
- Mục đích: kiểm tra trạng thái server.
- Phản hồi thành công (200):
```json
{
  "status": "healthy",
  "services": {
    "vision": true,
    "text": true
  }
}
```

## Vision API (Phân loại ảnh da liễu)
### POST /v1/vision/predict
- Body (JSON):
```json
{
  "image": "data:image/jpeg;base64,...."
}
```
Ghi chú:
- Trường `image` chấp nhận cả base64 thuần hoặc chuỗi dạng Data URI (`data:image/...;base64,...`).
- Ảnh nên là JPG/PNG, hệ thống sẽ resize về 224x224 để suy luận.

- Phản hồi thành công (200) – ví dụ:
```json
{
  "prediction": "Psoriasis",
  "confidence": 87.12,
  "all_confidences": {
    "Atopic Dermatitis": 0.1,
    "Eczema": 10.3,
    "Psoriasis": 87.12,
    "Seborrheic Keratoses": 1.2,
    "Tinea Ringworm Candidiasis": 1.28
  },
  "top_alternatives": [
    {"class": "Eczema", "confidence": 10.3},
    {"class": "Seborrheic Keratoses", "confidence": 1.2}
  ],
  "recommendation": "High confidence prediction. Always consult healthcare professional for confirmation."
}
```

- Mã lỗi thường gặp:
  - 400: Thiếu hoặc sai trường `image`
  - 500: Lỗi nội bộ (model chưa sẵn sàng, file model thiếu, ảnh hỏng…)

- Ví dụ cURL:
```bash
curl -s -X POST http://127.0.0.1:8000/v1/vision/predict \
  -H "Content-Type: application/json" \
  -d '{"image":"data:image/jpeg;base64,REPLACE_ME"}'
```

- Ví dụ Python:
```python
import base64, requests, pathlib

api = "http://127.0.0.1:8000/v1/vision/predict"
img_path = pathlib.Path("ai_server/models/test.jpg")
b64 = base64.b64encode(img_path.read_bytes()).decode()
payload = {"image": f"data:image/jpeg;base64,{b64}"}
resp = requests.post(api, json=payload, timeout=300)
print(resp.json())
```

## Text API (Phân tích hội thoại y khoa)
### POST /v1/text/analyze
- Body (chọn một trong hai):
```json
{"text": "..."}
```
hoặc
```json
{"texts": ["...", "..."]}
```

- Phản hồi thành công (200):
  - Trường `raw`: chuỗi JSON gốc do model sinh
  - Trường `json`: bản đã chuẩn hóa phía server, luôn có đúng 2 khóa
```json
{
  "raw": "{\"symptom\":[\"đau đầu\"],\"diagnosis\":\"Nghi ngờ nhiễm virus.\"}",
  "json": {
    "symptom": ["đau đầu"],
    "diagnosis": "Nghi ngờ nhiễm virus."
  }
}
```

- Quy ước chuẩn hóa phía server:
  - Luôn trả về `json` với hai khóa chính xác: `symptom` (mảng chuỗi) và `diagnosis` (chuỗi)
  - Nếu model trả về khóa gần giống (ví dụ "symptoom"), hệ thống ánh xạ gần đúng về `symptom`
  - Nếu thiếu dữ liệu, giá trị mặc định: `symptom: []`, `diagnosis: "Unknown"`

- Mã lỗi thường gặp:
  - 400: Thiếu cả `text` lẫn `texts`, hoặc `texts` trống
  - 500: Lỗi nội bộ (model chưa sẵn sàng, file GGUF thiếu…)

- Ví dụ cURL:
```bash
curl -s -X POST http://127.0.0.1:8000/v1/text/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"Bệnh nhân bị sốt 38.5 độ và buồn nôn."}'
```

- Ví dụ Python:
```python
import requests, json
api = "http://127.0.0.1:8000/v1/text/analyze"
payload = {"text": "Bệnh nhân bị sốt 38.5 độ và buồn nôn."}
resp = requests.post(api, json=payload, timeout=600)
print(json.dumps(resp.json(), ensure_ascii=False, indent=2))
```

### POST /v1/text/transcribe
- multipart/form-data fields:
  - `file`: bắt buộc (audio/webm|wav|mp3|m4a|ogg)
  - `language`: tùy chọn (`vi`|`en`, mặc định `vi`)
- Phản hồi thành công (200):
```json
{ "transcript": "..." }
```

- Ví dụ cURL (Windows PowerShell dùng `-F` với `@path`):
```bash
curl -X POST http://127.0.0.1:8000/v1/text/transcribe \
  -H "Accept: application/json" \
  -F "file=@sample.wav" -F "language=vi"
```

### POST /v1/text/transcribe-and-analyze
- multipart/form-data: cùng trường như trên
- Luồng: Transcribe (OpenAI|Deepgram) → Analyze → Chuẩn hóa khóa
- Phản hồi thành công (200):
```json
{
  "transcript": "...",
  "ai": {
    "raw": "{\"symptom\":[\"đau đầu\"],\"diagnosis\":\"...\"}",
    "json": { "symptom": ["đau đầu"], "diagnosis": "..." }
  }
}
```

### Alias /ai/text/...
- Hỗ trợ gọi qua: `/ai/text/transcribe` và `/ai/text/transcribe-and-analyze`

### Cấu hình ASR qua ENV
- `ASR_PROVIDER` = `openai` | `deepgram`
- `ASR_API_KEY` = khóa provider
- `ASR_MODEL` (OpenAI: `whisper-1`; Deepgram: ví dụ `whisper-large`)
- Timeout: `ASR_TIMEOUT` (mặc định 600 giây)
Ghi chú Deepgram:
- Với file `.m4a`, server tự ánh xạ Content-Type sang `audio/mp4`.
- Nếu gặp lỗi model/language, đặt `ASR_MODEL` phù hợp (vd: `whisper-large`).

## Ghi chú vận hành
- Lần chạy đầu có thể chậm do tải/khởi tạo model
- Vision cần file Keras trong `ai_server/models/`
- Text cần file GGUF trong `ai_server/models/`
- Timeout khuyến nghị khi gọi API: Vision ~300s, Text ~600s (tùy cấu hình máy)

## Phiên bản & mở rộng
- API được namespaced theo `/v1/...` để dễ mở rộng về sau
- Chưa có cơ chế rate limit, auth – có thể thêm theo yêu cầu
