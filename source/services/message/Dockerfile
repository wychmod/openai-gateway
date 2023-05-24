FROM openai-base:v2
# 为外层的dockerfile打成的容器，方便每次修改只打包代码，不下载pip包了

ENV PYTHONPATH "${PYTHONPATH}:$PWD/app:$PWD/app/source"
ENV DB_HOST postgres
WORKDIR /app/source/
COPY ./services/message/ /app/source/services/message/
COPY ./basic/ /app/source/basic/
CMD ["python3","/app/source/services/message/main.py"]

# 根目录docker build -t swr.cn-north-4.myhuaweicloud.com/weizhanjun/openai-gateway:v1 -f ./source/services/auth/Dockerfile .