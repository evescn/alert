FROM python:3.8.7-alpine3.11

WORKDIR /alert
COPY ./ ./
RUN pip install -r /alert/requirements.txt

EXPOSE 8080
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]