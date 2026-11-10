# Đóng gói backend Smart CRM – luồng L4 (FastAPI + psycopg). Chỉ cần Docker, không cần cài Python trên máy.
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1

# 1. Tệp khoá trước -> chỉ cài lại thư viện khi requirements.txt đổi (tận dụng cache)
COPY requirements.txt .
RUN pip install -r requirements.txt

# 2. Mã nguồn, SQL, test (BT3 chạy test TRONG container), công cụ test case, dữ liệu mẫu
COPY src ./src
COPY db ./db
COPY tests ./tests
COPY scripts ./scripts
COPY data ./data

# 3. Không chạy bằng root
RUN useradd -m appuser && mkdir -p docs && chown -R appuser /app
USER appuser

EXPOSE 3000
CMD ["uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "3000"]
