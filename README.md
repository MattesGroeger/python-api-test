# E-Commerce Microservices API

A microservices-based e-commerce platform with API Gateway, built with FastAPI.

## Setup

1. Create virtual environment and install dependencies:
```bash
make setup
```

2. Run the API Gateway:
```bash
make run
```

The API will be available at `http://localhost:8000`

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Features

- API Gateway with rate limiting
- Request logging
- Product and Order microservices
- Versioned API endpoints
- CORS support 