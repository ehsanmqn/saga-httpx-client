FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1
ENV HOSTS="http://127.0.0.1:8000,http://127.0.0.1:8001,http://127.0.0.1:8002"

WORKDIR /saga-httpx-client

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
