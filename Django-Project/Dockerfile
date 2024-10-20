# Use an official Python runtime as a parent image
FROM python:3.12

# Install dependencies required for PostgreSQL
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory to /usr/src/app (the Django-Project folder)
WORKDIR /usr/src/app

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project folder content to the container
COPY . .

# Change working directory to BlockhouseTest where manage.py is located
WORKDIR /usr/src/app/BlockhouseTest

# Expose port 8000 to the outside world
EXPOSE 8000

# Define environment variable to ensure proper output
ENV PYTHONUNBUFFERED=1

# Entry point to run migrations and start the Django development server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]