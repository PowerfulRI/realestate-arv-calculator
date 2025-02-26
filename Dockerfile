FROM python:3.10-slim

WORKDIR /app

# Install Chrome and dependencies for Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    xvfb \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome WebDriver
RUN CHROME_DRIVER_VERSION=$(wget -qO- https://chromedriver.storage.googleapis.com/LATEST_RELEASE) \
    && wget -q "https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip" \
    && unzip chromedriver_linux64.zip -d /usr/local/bin \
    && rm chromedriver_linux64.zip \
    && chmod +x /usr/local/bin/chromedriver

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY ./src /app/src
COPY setup.py .
COPY README.md .

# Install the application in development mode
RUN pip install -e .

# Create a config directory for API keys
RUN mkdir -p /config

# Create an entrypoint script for web mode
RUN echo '#!/bin/bash\n\
# Load environment variables from config if it exists\n\
if [ -f "/config/config.env" ]; then\n\
    set -a\n\
    source "/config/config.env"\n\
    set +a\n\
fi\n\
\n\
# Check if web mode is enabled\n\
if [ "$1" = "--web" ]; then\n\
    # Run the web application with gunicorn\n\
    exec gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --threads 4 "realestate_arv_app.ui.web_app:app"\n\
else\n\
    # Run the CLI calculator\n\
    exec python -m realestate_arv_app.main "$@"\n\
fi\n' > /entrypoint.sh \
    && chmod +x /entrypoint.sh

# Expose the web port
EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["--web"]