#!/bin/bash

echo "Starting services..."

# 生成自签名 SSL 证书
echo "Generating SSL certificate..."
if [ ! -f "/etc/nginx/ssl/server.crt" ]; then
    openssl req -x509 -nodes -days 7300 -newkey rsa:2048 \
        -keyout /etc/nginx/ssl/server.key \
        -out /etc/nginx/ssl/server.crt \
        -subj "/C=CN/ST=Shanghai/L=Shanghai/O=IT/CN=localhost"
    
    # 设置正确的权限
    chmod 644 /etc/nginx/ssl/server.crt
    chmod 600 /etc/nginx/ssl/server.key
fi

# 检查证书是否生成成功
if [ ! -f "/etc/nginx/ssl/server.crt" ] || [ ! -f "/etc/nginx/ssl/server.key" ]; then
    echo "Error: SSL certificate generation failed!"
    exit 1
fi

# 检查数据库文件是否存在
echo "Checking database..."
if [ ! -f "./data/db.sqlite3" ]; then
    echo "Database file not found, initializing..."
    # 确保目录存在
    mkdir -p ./data
    chmod -R 777 ./data
    
    # 初始化数据库和管理员账户
    python -m app.init_admin
    if [ $? -ne 0 ]; then
        echo "Failed to initialize database!"
        exit 1
    fi
    echo "Database initialized successfully!"
else
    echo "Database file exists, skipping initialization."
fi

# 检查前端文件
echo "Checking frontend files..."
if [ -d "/usr/share/nginx/html" ]; then
    echo "Contents of /usr/share/nginx/html:"
    ls -la /usr/share/nginx/html/
else
    echo "Error: /usr/share/nginx/html directory not found!"
fi

# 启动 nginx
echo "Starting Nginx..."
nginx
if [ $? -ne 0 ]; then
    echo "Failed to start Nginx"
    exit 1
fi

# 确保后端目录正确
cd /backend
if [ ! -d "app" ]; then
    echo "Backend directory structure incorrect!"
    ls -la
    exit 1
fi

# 启动后端服务
echo "Starting Backend service..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 