# MTS Local Stack

Проект запускается через Docker Compose. Есть два режима:

- базовый: `db + app + frontend`
- полный: `db + ollama + ollama-init + app + frontend`

## Что поднимается

### Базовый режим

- `db` - Postgres
- `app` - FastAPI backend
- `frontend` - Vite frontend из `./frontend`

В этом режиме `Ollama` должен быть запущен отдельно, вне Compose.

### Полный режим

- `db` - Postgres
- `ollama` - LLM server
- `ollama-init` - один раз скачивает модель
- `app` - FastAPI backend
- `frontend` - Vite frontend из `./frontend`

## Требования

- Docker
- Docker Compose

Проверка:

```bash
docker --version
docker compose version
```

## Быстрый старт

### Вариант 1. Базовый режим

Поднимает `db`, `app` и `frontend`.

```bash
docker compose up -d --build
```

После запуска будут доступны:

- frontend: `http://localhost:5173`
- backend: `http://localhost:8000`
- healthcheck backend: `http://localhost:8000/health`

Остановить стек:

```bash
docker compose down
```

## Как работает backend при старте

Контейнер `app` запускается не сразу. Он:

1. ждёт готовности Postgres
2. выполняет `alembic upgrade head`
3. только потом стартует FastAPI

Это уже встроено в Docker-образ backend.

## Ollama в базовом режиме

В базовом режиме backend ожидает, что Ollama уже доступен по адресу:

```text
http://host.docker.internal:11434
```

То есть Ollama можно держать отдельно на хост-машине.

По умолчанию используется модель:

```text
qwen2.5:7b
```

Если Ollama у тебя запущен на другом адресе или порту, можно переопределить переменную окружения перед запуском:

```bash
OLLAMA_BASE_URL=http://host.docker.internal:11434 docker compose up -d --build
```

Для PowerShell:

```powershell
$env:OLLAMA_BASE_URL="http://host.docker.internal:11434"
docker compose up -d --build
```

## Полный запуск вместе с Ollama

Если хочешь поднимать и Ollama внутри Compose, используй оба файла:

```bash
docker compose -f docker-compose.yml -f docker-compose.ollama.yml up -d --build
```

В этом режиме:

- `ollama` хранит данные в volume, поэтому модель не скачивается заново при каждом запуске
- `ollama-init` один раз подтягивает модель
- `app` подключается к Ollama внутри docker-сети

Остановить полный стек:

```bash
docker compose -f docker-compose.yml -f docker-compose.ollama.yml down
```

## Полезные команды

Посмотреть статус контейнеров:

```bash
docker compose ps
```

Посмотреть логи backend:

```bash
docker compose logs app
```

Посмотреть логи frontend:

```bash
docker compose logs frontend
```

Посмотреть логи полного стека с Ollama:

```bash
docker compose -f docker-compose.yml -f docker-compose.ollama.yml logs
```

## Полезные переменные

Базовые значения уже зашиты в `docker-compose.yml`, но при необходимости можно переопределять:

- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `OLLAMA_BASE_URL`
- `OLLAMA_MODEL`
- `REQUEST_TIMEOUT_SECONDS`
- `USE_STUB_MODEL`

Пример для PowerShell:

```powershell
$env:POSTGRES_PASSWORD="mysecret"
$env:OLLAMA_MODEL="qwen2.5:7b"
docker compose up -d --build
```

## Проверка после запуска

Проверь backend:

```bash
curl http://localhost:8000/health
```

Ожидаемый ответ:

```json
{"status":"ok"}
```

Проверь frontend, открыв в браузере:

```text
http://localhost:5173
```

## Частые сценарии

### Пересобрать и заново запустить

```bash
docker compose up -d --build
```

### Полностью остановить и удалить контейнеры

```bash
docker compose down
```

### Остановить с удалением volume базы

```bash
docker compose down -v
```

Это удалит данные Postgres.
