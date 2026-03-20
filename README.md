# OmniScraper-AI

**OmniScraper-AI** là một hệ thống thu thập dữ liệu đa nền tảng (Multi-platform Data Scraper) được xây dựng trên nền tảng FastAPI và Celery.

## 🚀 Tổng quan

Hệ thống được thiết kế để thay thế các quy trình crawl thủ công hoặc các service cũ, cung cấp khả năng mở rộng cao thông qua kiến trúc Microservices và Message Queue.

### 💡 Sơ đồ Luồng hoạt động (Data Flow)

```mermaid
graph TD
    User([Hệ thống / Giao diện / CronJob]) -->|Ví dụ: POST /api/facebook/crawl-page| API_Gateway[FastAPI Server]
    
    API_Gateway -->|1. Đẩy Task kèm params| RabbitMQ[(Message Broker: RabbitMQ)]
    
    subgraph Celery_Worker_Cluster [Các Server xử lý nề (Worker)]
        WorkerFB[Worker Facebook]
        WorkerTT[Worker TikTok]
    end
    
    RabbitMQ -->|2. Phân phối dựa theo Queue| WorkerFB
    RabbitMQ -->|2. Phân phối dựa theo Queue| WorkerTT
    
    WorkerFB -->|3a. Xin Token| TokenMgr[Token Manager\nRound-Robin]
    WorkerFB -->|4a. Gọi API bằng Token| FB_API{Facebook\nGraph API}
    
    WorkerTT -->|4b. Parse HTML/API| TT_Web{TikTok Web}
    
    FB_API -.->|5a. Trả JSON Data| WorkerFB
    TT_Web -.->|5b. Trả JSON Data| WorkerTT
    
    WorkerFB -->|6. Lưu Data hoặc Đẩy tiếp| Database[(PostgreSQL/Elastic\nOr Next Queue)]
    WorkerTT -->|6. Lưu Data hoặc Đẩy tiếp| Database
    
    WorkerFB -.->|Cache/Chống trùng lặp| Redis[(Redis Cache)]
    WorkerTT -.->|Cache/Chống trùng lặp| Redis
```

### 🌟 Các tính năng chính
- **Đa nền tảng**: Hỗ trợ Facebook, TikTok (và có thể mở rộng sang Instagram, X, YouTube).
- **Kiến trúc phân tán**: Sử dụng **RabbitMQ** làm Message Broker và **Celery** làm Worker để xử lý tác vụ bất đồng bộ.
- **Quản lý Token thông minh**: Tích hợp **Token Manager** để xoay vòng (Round-Robin) các Facebook Graph Token, giúp tránh bị khóa tài khoản.
- **API Gateway**: Giao diện FastAPI để điều khiển và giám sát quá trình crawl.

## 🛠️ Cài đặt và Chạy

### Yêu cầu hệ thống
- Docker
- Docker Compose

### Cấu hình môi trường
1. Tạo file `.env` từ `.env.example`:
   ```bash
   cp .env.example .env
   ```
2. Chỉnh sửa file `.env` với các thông tin cần thiết (đặc biệt là `FB_GRAPH_TOKENS`).

### Khởi động hệ thống
Sử dụng Docker Compose để khởi động toàn bộ hạ tầng (RabbitMQ, Redis, PostgreSQL) và ứng dụng:

```bash
docker-compose up --build
```

### Truy cập API
Sau khi hệ thống khởi động, bạn có thể truy cập API tại:
- **Swagger UI**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🎯 Cấu trúc dự án

```
OmniScraper-AI/
├── app/
│   ├── api/             # FastAPI Routers (API Endpoints)
│   ├── crawlers/        # Logic crawl cho từng nền tảng
│   │   ├── facebook/    # Facebook Graph API logic
│   │   └── tiktok/      # TikTok scraper logic
│   ├── core/            # Core modules
│   │   ├── config.py    # Cấu hình ứng dụng
│   │   ├── celery_app.py # Cấu hình Celery
│   │   └── token_manager.py # Facebook Token Manager
│   ├── models/          # Pydantic Models
│   └── workers/         # Celery Workers (Xử lý tác vụ)
│       ├── facebook_worker.py
│       └── tiktok_worker.py
├── .agent/              # Cấu hình Agent (Google Antigravity)
├── .env.example         # File mẫu cấu hình
├── Dockerfile           # Docker image cho ứng dụng
├── docker-compose.yml   # Cấu hình Docker services
└── requirements.txt     # Dependencies Python
```

## 🔌 API Endpoints

### Facebook
- `POST /api/facebook/crawl-post`: Kích hoạt crawl một bài viết cụ thể.
- `POST /api/facebook/crawl-page`: Kích hoạt crawl danh sách bài viết từ một Page.

### TikTok
- `POST /api/tiktok/crawl-user`: Kích hoạt crawl thông tin người dùng TikTok.
- `POST /api/tiktok/crawl-video`: Kích hoạt crawl video TikTok.

## 🧪 Kiểm thử

### Test Facebook
```bash
curl -X POST "http://localhost:8000/api/facebook/crawl-post" \
     -H "Content-Type: application/json" \
     -d '{"post_id": "1234567890", "crawl_method": 1}'
```

### Test TikTok
```bash
curl -X POST "http://localhost:8000/api/tiktok/crawl-user" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "loop_count": 5}'
```

## 📊 Giám sát

### RabbitMQ Web UI
Truy cập: http://localhost:15672
- User: `guest`
- Pass: `guest`

### Celery Worker Logs
Xem logs của worker:
```bash
docker logs omniscraper_celery
```

## 🔐 Facebook Token Management

Hệ thống sử dụng `TokenManager` để quản lý danh sách Facebook Graph Tokens.

### Cấu hình Token
Trong file `.env`, thêm danh sách token ngăn cách bởi dấu phẩy:
```env
FB_GRAPH_TOKENS=EAAAAU...,EAAABV...,EAAACW...
```

### Cách thức hoạt động
1. Khi có request crawl, hệ thống sẽ lấy token từ pool.
2. Nếu token bị lỗi (400, 403, 500), token đó sẽ bị đánh dấu là "bad" và không được sử dụng lại trong 5 phút.
3. Hệ thống sẽ xoay vòng qua các token còn lại để đảm bảo không bị chặn.

## 📚 Tài liệu tham khảo

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)

## 🤝 Đóng góp

1. Fork dự án
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

## 📝 License

MIT License