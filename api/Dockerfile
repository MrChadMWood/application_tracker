FROM python:3.12

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

COPY ./requirements.txt .
RUN uv pip install --system --no-cache-dir -r requirements.txt
