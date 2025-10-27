# Use a standard, slim Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to cache the installation
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your app code into the container
COPY . .

# Tell Docker that your app will run on port 8501
EXPOSE 8501

# Add a health check to see if Streamlit is running
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# The command to run your Streamlit app
# We use 0.0.0.0 to make it accessible outside the container
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]