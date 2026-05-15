FROM python:3.12-slim

WORKDIR /app

COPY week3/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY week3/ .
RUN mkdir -p /app/output

EXPOSE 5003
CMD ["python", "app.py"]
