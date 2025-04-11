# 构建前端
FROM node:18-alpine as frontend-builder
WORKDIR /frontend

# 添加必要的依赖
RUN apk add --no-cache python3 make g++

# 设置环境变量
ENV PATH=/frontend/node_modules/.bin:$PATH

# 清理并安装依赖
COPY frontend/package*.json ./
RUN npm cache clean --force && \
    npm install

# 复制源代码并构建
COPY frontend/ .
RUN rm -rf node_modules && \
    npm cache clean --force && \
    npm install && \
    chmod +x node_modules/.bin/vite && \
    npm run build && \
    echo "Frontend build completed. Contents of dist:" && \
    ls -la dist/

# 构建后端
FROM python:3.8-slim
WORKDIR /backend

# 设置时区为北京时间
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 安装 nginx 和 SSL 工具
RUN apt-get update && \
    apt-get install -y nginx openssl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /usr/share/nginx/html/*

# 创建 SSL 证书目录
RUN mkdir -p /etc/nginx/ssl && \
    chmod 755 /etc/nginx/ssl

# 复制前端构建产物
COPY --from=frontend-builder /frontend/dist/ /usr/share/nginx/html/
RUN chmod -R 755 /usr/share/nginx/html

# 配置 nginx
COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf
RUN rm -f /etc/nginx/sites-enabled/default

# 安装后端依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 创建数据目录并复制后端代码
RUN mkdir -p data && \
    chmod -R 777 data
COPY app/ /backend/app/

# 启动脚本
COPY docker/start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 80 443 8000

# 设置工作目录并启动服务
WORKDIR /backend
CMD ["/start.sh"] 