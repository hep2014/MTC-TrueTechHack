FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        lua5.4 \
        lua5.4-dev \
        luarocks \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN ln -sf /usr/bin/lua5.4 /usr/local/bin/lua \
    && ln -sf /usr/bin/luac5.4 /usr/local/bin/luac


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
