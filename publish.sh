#!/bin/bash

# 检查是否提供了 Docker Hub 用户名
if [ -z "$1" ]; then
    echo "请提供 Docker Hub 用户名"
    echo "用法: ./publish.sh <DOCKER_USERNAME> [TAG]"
    exit 1
fi

# 设置变量
DOCKER_USERNAME=$1
TAG=${2:-latest}  # 如果没有提供 TAG，默认使用 latest

echo "准备发布镜像到 Docker Hub..."
echo "用户名: $DOCKER_USERNAME"
echo "版本号: $TAG"

# 登录 Docker Hub
echo "正在登录 Docker Hub..."
docker login

# 导出环境变量
export DOCKER_USERNAME=$DOCKER_USERNAME
export TAG=$TAG

# 构建镜像
echo "正在构建镜像..."
docker-compose build

# 推送镜像
echo "正在推送镜像到 Docker Hub..."
docker push ${DOCKER_USERNAME}/itkefu:${TAG}

echo "发布完成！"
echo "镜像地址："
echo "- ${DOCKER_USERNAME}/itkefu:${TAG}" 