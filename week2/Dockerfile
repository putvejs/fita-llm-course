FROM python:3.12-slim

WORKDIR /app

COPY week2/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY week2/ .
COPY context.md .

EXPOSE 5002
CMD ["python", "app.py"]
