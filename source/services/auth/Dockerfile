FROM openai-base:v2
# 为外层的dockerfile打成的容器，方便每次修改只打包代码，不下载pip包了

ENV OPENAI_API_KEY xxxxx
ENV OPENAI_SERVICE_PORT 8090
ENV ENV PRODUCTION
ENV PYTHONPATH "${PYTHONPATH}:$PWD/app:$PWD/app/source"
ENV DB_HOST postgres
WORKDIR /app/source/
COPY ./services/auth/ /app/source/services/auth/
COPY ./basic/ /app/source/basic/
EXPOSE 8090
CMD ["python3","/app/source/services/auth/main.py"]

# 根目录docker build -t swr.cn-north-4.myhuaweicloud.com/weizhanjun/openai-gateway:v1 -f ./source/services/auth/Dockerfile .