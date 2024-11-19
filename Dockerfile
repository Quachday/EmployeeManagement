# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for tkinter
RUN apt-get update && apt-get install -y \
    tk \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . .

RUN pip install Flask

# Command to run the application (modify as needed)
CMD ["python3", "app.py"]
