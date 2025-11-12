FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

RUN useradd -m slauser
USER slauser

EXPOSE 9200

ENV PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=9200

CMD ["python", "main.py"]