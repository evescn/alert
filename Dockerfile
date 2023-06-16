FROM python:3.8.7-alpine3.11

# 设置时区为 Asia/Shanghai
ENV TZ=Asia/Shanghai

RUN apk add --no-cache tzdata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /alert
COPY ./ ./
RUN pip install -r /alert/requirements.txt

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]