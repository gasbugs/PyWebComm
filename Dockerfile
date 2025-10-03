# 1. Base Image: Use an official lightweight Python image
FROM python:3.12-slim

# 2. Set the working directory in the container
WORKDIR /app

# 3. Copy the dependencies file first
# This leverages Docker layer caching. This layer is only rebuilt if requirements.txt changes.
COPY requirements.txt .

# 4. Install the dependencies
# --no-cache-dir reduces image size
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application's source code
COPY . .

# 6. Specify the default command to run when the container starts
# This will run the scanner and print its help message by default.
# Users can override this command.
# Example override: docker run my-web-scanner python step4_final_scanner/scanner.py --level 0
CMD ["python", "step4_final_scanner/scanner.py", "--help"]
