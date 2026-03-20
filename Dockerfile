# Dùng Python bản slim để giảm kích cỡ Image Docker
FROM python:3.12-slim

# Biến môi trường chống tạo bytecode (.pyc) và flush stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Cài đặt dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code vào bên trong thư mục /app của container
COPY . /app/

# Port chạy FastAPI
EXPOSE 8000

# Lệnh CMD mặc định khi chạy
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
