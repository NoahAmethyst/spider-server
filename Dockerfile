FROM python:3.11.2-alpine

WORKDIR /app

COPY ./ .
RUN pip install --no-cache-dir -r requirements.txt && pip cache purge

EXPOSE 9090

CMD ["python3', '/app/main.py"]
