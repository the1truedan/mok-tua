FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

ENV MOCK_TUA_CONFIG=/config
ENV WORK_FALLBACK=/work
ENV PYTHONUNBUFFERED=1

EXPOSE 8799

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8799"]
