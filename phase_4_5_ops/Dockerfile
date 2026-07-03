FROM python:3.10-slim
WORKDIR /app
COPY ./artha_backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY ./artha_backend /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
