FROM python:3.8.1-slim

COPY app /app
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

CMD ["python", "front.py"]