FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
COPY README.md .
COPY src/ ./src/

RUN pip install --no-cache-dir .

# Expose the proxy port
EXPOSE 8082

# Start the proxy
ENTRYPOINT ["nim-proxy"]
CMD ["start", "--host", "0.0.0.0", "--port", "8082"]
