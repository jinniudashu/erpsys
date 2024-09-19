# 使用官方的 Python 3.11 镜像作为基础镜像
FROM python:3.11.5-slim

# 设置环境变量，以便在容器内安装 Python 包时不会生成缓存文件
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    nano \
    && rm -rf /var/lib/apt/lists/*

# 将 requirements.txt 文件复制到容器中
COPY requirements.txt /app/

# 安装 Python 依赖
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 将当前目录下的所有文件复制到容器中
COPY . /app/

USER root

# 为 wait-for-it.sh 脚本授予执行权限
RUN chmod +x /app/wait-for-it.sh

# 收集静态文件
RUN python manage.py collectstatic --noinput

# 暴露应用运行端口
EXPOSE 8000

# 启动应用
# CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "cxerp.asgi:application"]