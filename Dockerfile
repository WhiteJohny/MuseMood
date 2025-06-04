FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

COPY .env .
COPY ./src ./src

ENV PYTHONPATH "${PYTHONPATH}:/app"

CMD [ "python", "./src/__main__.py" ]
