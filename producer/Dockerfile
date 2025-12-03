FROM python:3.11-slim

WORKDIR /app

COPY producer.py .

RUN pip install --no-cache-dir kafka-python==2.0.2

CMD ["python", "producer.py"]