FROM openai-base:v1
# 为外层的dockerfile打成的容器，方便每次修改只打包代码，不下载pip包了

ENV OPENAI_SERVICE_PORT 8080
ENV ENV PRODUCTION
ENV PYTHONPATH "${PYTHONPATH}:$PWD/app:$PWD/app/source"
WORKDIR /app/source/

COPY ./services/openai/ /app/source/services/openai/
COPY ./basic/ /app/source/basic/
EXPOSE 8080
CMD ["python3","/app/source/services/openai/main.py"]

# 根目录docker build -t swr.cn-north-4.myhuaweicloud.com/weizhanjun/openai:v1 -f ./source/services/openai/Dockerfile .
