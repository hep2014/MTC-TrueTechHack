# MTS Local Lua Agent

Проект разработан в рамках кейса МТС и представляет собой локальный AI-агент для генерации Lua-кода с контролем качества, валидацией и поддержкой диалогового взаимодействия.

В отличие от классических решений, система реализует **полный управляемый pipeline генерации**, включая анализ задачи, генерацию, валидацию, автоматическое исправление и оценку качества результата.

---

# Проблематика

Современные LLM-инструменты для генерации кода сталкиваются с рядом критических проблем:

- генерация некорректного или неисполняемого кода  
- отсутствие проверки результата  
- невозможность адаптации под конкретный runtime (например, Lua / LowCode)  
- «чёрный ящик» без объяснения, почему ответ считается корректным  
- отсутствие воспроизводимости (зависимость от внешних API)  

В контексте МТС это особенно критично, так как:

- требуется генерация кода под контролируемые среды (LowCode, workflow)
- важно исключить использование недопустимых API
- необходимо обеспечить предсказуемость и повторяемость результата

---

# Наше решение

Мы реализовали систему управляемой генерации кода, которая:

- анализирует задачу перед генерацией  
- определяет доменный контекст (general / lowcode)  
- применяет шаблоны и правила  
- валидирует код на нескольких уровнях  
- выполняет runtime-проверку  
- автоматически исправляет ошибки  
- рассчитывает confidence-score  
- поддерживает диалог и уточнение задачи  

Система полностью работает локально через Ollama и Docker.

---

# Архитектура

Система состоит из нескольких компонентов:

- **backend (FastAPI)** — orchestration pipeline  
- **frontend (Vite)** — пользовательский интерфейс  
- **PostgreSQL** — хранение сессий и pipeline  
- **Ollama** — локальная LLM  

---

### Структура проекта

```
MTC-TrueTechHack/
├── localscript_backend/ # Backend (FastAPI + pipeline)
│ ├── app/
│ │ ├── services/ # бизнес-логика и pipeline
│ │ ├── routers/ # API
│ │ ├── models/ # ORM / схемы
│ │ └── main.py # entrypoint
│ ├── alembic/ # миграции БД
│ ├── Dockerfile
│ └── docker-entrypoint.sh
│
├── frontend/ # Vite frontend
│ ├── src/
│ ├── index.html
│ ├── package.json
│ └── Dockerfile
│
├── docker-compose.yml # базовый стек
├── docker-compose.ollama.yml # overlay с LLM
└── README.md
```


---

### Pipeline генерации

Каждый запрос проходит следующие этапы:

1. **Task Analysis** — разбор задачи  
2. **Template Selection** — подбор шаблонов  
3. **Generation** — генерация кода  
4. **Validation**:
   - syntax
   - policy
   - domain
   - runtime
   - scenario
5. **Repair (опционально)** — исправление ошибок  
6. **Evaluation** — формирование отчёта и confidence  

---

### Запуск проекта

Проект запускается через Docker Compose.

Есть два режима:

- базовый  
- полный (с Ollama)

---

## Требования

- Docker
- Docker Compose

Проверка:

```
docker --version
docker compose version
```

**Базовый запуск**

Поднимает:

- PostgreSQL
- backend
- frontend

```
docker compose up -d --build
```

После запуска:
```
frontend: http://localhost:5173
backend: http://localhost:8000
health: http://localhost:8000/health
Как работает backend при старте
```
Контейнер backend:
- ждёт доступность базы данных
- выполняет миграции Alembic
- запускает FastAPI

Это гарантирует, что база всегда в актуальном состоянии.

**Ollama (в базовом режиме)**

Backend ожидает Ollama по адресу:
```
http://host.docker.internal:11434
```

Модель по умолчанию:
```
qwen2.5:7b
```
Можно переопределить:
```
OLLAMA_BASE_URL=http://host.docker.internal:11434 docker compose up -d --build
```
### Полный запуск (вместе с LLM)

```
docker compose -f docker-compose.yml -f docker-compose.ollama.yml up -d --build
```
Поднимается:

- Ollama
- загрузка модели
- backend подключается внутри сети

Остановка:
```
docker compose -f docker-compose.yml -f docker-compose.ollama.yml down
```

**Полезные команды**

Статус:
```
docker compose ps
```
Логи backend:
```
docker compose logs app
```
Логи frontend:
```
docker compose logs frontend
```
Полный стек:
```
docker compose -f docker-compose.yml -f docker-compose.ollama.yml logs
```

### Переменные окружения

Основные:
```
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
OLLAMA_BASE_URL
OLLAMA_MODEL
REQUEST_TIMEOUT_SECONDS
```
Пример:
```
POSTGRES_PASSWORD=mysecret docker compose up -d --build
```
Проверка работы
````
curl http://localhost:8000/health
````
Ожидаемый ответ:
```
{"status":"ok"}
```

### Участники

- [Илья Матвеев](http://t.me/hep2014) - backend
- [Анастасия Кабанова](https://t.me/anastaness) - frontend, визуализация
- [Мясников Евгений](https://t.me/Myzn1k) - devops
- [Щеголев Иван](https://t.me/hep2O14) - frontend
- [Косинский Эдуард](https://t.me/tominvst) - backend

### Преимущества решения
- управляемый pipeline вместо «чёрного ящика»
- многоуровневая валидация
- runtime-проверка кода
- автоматическое исправление
- адаптация под LowCode
- объяснимая confidence-оценка
- полностью локальная работа
