FROM python:3.12-slim

WORKDIR /app

COPY requirements-api.txt .

RUN pip install --no-cache-dir -r requirements-api.txt

COPY . .

EXPOSE 8000

ENV FRIX_TEST_MODE=true

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]