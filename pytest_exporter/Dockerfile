FROM python:3.9-slim

COPY . /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONBUFFERED=1
ENTRYPOINT [ "python", "exporter.py" ]