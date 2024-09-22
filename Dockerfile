# Use the official Python image from Docker Hub as the base image
FROM python:3.11

# Set the working directory inside the Docker container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the necessary Python dependencies
# First, let's make sure that 'pathway', 'requests', 'feedparser', etc., are installed
RUN pip install -U pathway requests datetime openai python-dotenv feedparser

# Expose the necessary ports for the API and other services
EXPOSE 8080
EXPOSE 8501

# Set the command to run the chatmaster.py script on container start
ENTRYPOINT ["python", "query.py"]
