# backend/orquestador/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY orquestador.py .

EXPOSE 5000

CMD ["python", "orquestador.py"]