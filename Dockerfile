FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install telebot
CMD ["python", "main.py"]
