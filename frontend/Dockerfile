# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /frontend

# Copy the current directory contents into the container at /app
COPY . /frontend

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 7860 available to the world outside this container
EXPOSE 7860

# Run the Gradio app when the container launches
CMD ["python", "app.py"]
