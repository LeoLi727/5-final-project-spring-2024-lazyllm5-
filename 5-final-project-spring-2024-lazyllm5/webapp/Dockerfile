# Use an official Python runtime as a parent image (adjust version as necessary)
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install pipenv
RUN pip install --upgrade pip && \
    pip install pipenv

# Install dependencies from Pipfile
COPY Pipfile Pipfile.lock /app/
RUN pipenv install --deploy --ignore-pipfile

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development
ENV MONGO_URI=mongodb://admin:123456@mongodb:27017/BudgetTracker?authSource=admin
# Run the application
CMD ["pipenv", "run", "flask", "run"]
