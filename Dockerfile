# Use the official Python 3.10.14 image as the base image
FROM python:3.10.14-alpine

# Set the working directory in the container
WORKDIR /app

# Install apk dependencies
RUN apk add --no-cache gcc musl-dev linux-headers git

# Copy the dependencies file to the working directory
COPY requirements.txt .

# 
RUN pip install "cython<3.0.0" && pip install --no-build-isolation pyyaml==5.4.1

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY . .

RUN pip install -e /app
