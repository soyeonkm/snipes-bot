# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy ALL application code from your GitHub repo into /app
COPY . .

# Expose port (Northflank will set PORT env var)
EXPOSE 8080

# Run the bot
CMD ["python", "snipes_bot.py"]

