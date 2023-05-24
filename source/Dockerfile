FROM python:3.9.16-slim
RUN sed -i s@/deb.debian.org/@/mirrors.aliyun.com/@g /etc/apt/sources.list&&apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/* && wget https://github.com/apache/rocketmq-client-cpp/releases/download/2.0.0/rocketmq-client-cpp-2.0.0.amd64.deb
COPY requirements.txt .
RUN dpkg -i rocketmq-client-cpp-2.0.0.amd64.deb
RUN pip3 install -r requirements.txt -i https://pypi.douban.com/simple/

# 打包成openai-base:v1