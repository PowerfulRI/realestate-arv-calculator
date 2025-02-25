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

# Copy the application files
COPY dist/realestate_arv_app-1.0.0-py3-none-any.whl .
COPY README.md .

# Install the application
RUN pip install --no-cache-dir realestate_arv_app-1.0.0-py3-none-any.whl

# Create a config directory for API keys
RUN mkdir -p /config

# Create an entrypoint script
RUN echo '#!/bin/bash\n\
# Load environment variables from config if it exists\n\
if [ -f "/config/config.env" ]; then\n\
    set -a\n\
    source "/config/config.env"\n\
    set +a\n\
fi\n\
# Run the calculator\n\
arv-calculator "$@"\n' > /entrypoint.sh \
    && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["--help"]