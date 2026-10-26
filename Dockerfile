# Use official lightweight Python image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app code
COPY . .

# Run FastAPI using uvicorn (listening on port 80)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]