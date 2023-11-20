FROM python:3.11.2-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive

RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt && pip cache purge

COPY . /app

CMD ["python /app/main.py"]
