# filename: infra/proxy_lambda/source/Dockerfile
FROM python:3.12-bookworm

# Install dependencies for Playwright
RUN apt-get update && apt-get install -y curl gnupg && \
    curl https://sdk.cloud.google.com | bash && \
    /bin/bash -c "source $HOME/google-cloud-sdk/path.bash.inc"

# Install Playwright
RUN pip install --upgrade pip && \
    pip install playwright==1.56.0 && \
    playwright install --with-deps

WORKDIR /app
COPY . .

RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

CMD ["python3", "main.py"]