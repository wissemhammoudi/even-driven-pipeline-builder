FROM python:3.11

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY source /app/source
COPY app.py /app/

EXPOSE 8010

ENTRYPOINT ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8010"]

CMD ["--reload"]
