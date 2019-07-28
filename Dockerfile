FROM python:3

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt


# Run app.py when the container launches
CMD ["python", "bs4.py"]

CMD ["python", "fruit.py"]
