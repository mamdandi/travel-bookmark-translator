FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY install_model.py .
RUN python install_model.py
COPY app.py .
EXPOSE 10000
CMD ["python", "app.py"]
