# Code Indexer — система поиска по Python файлам (PostgreSQL)

## Описание

Система индексации и поиска функций и классов в Python файлах с использованием:
- **PostgreSQL** для хранения данных
- **FastAPI** для REST API
- **Docker** для контейнеризации

## Схема базы данных

### Таблица `files`
- `id` (SERIAL PRIMARY KEY) — внутренний идентификатор файла
- `name` (TEXT) — имя файла
- `path` (TEXT) — полный путь

### Таблица `code_entities`
- `id` (SERIAL PRIMARY KEY)
- `file_id` (FOREIGN KEY → files.id)
- `entity_type` (TEXT) — 'function' или 'class'
- `name` (TEXT) — имя функции/класса
- `start_line`, `end_line` (INTEGER) — позиция в файле
- `docstring` (TEXT) — документация

### Индексы
- `idx_entity_name` — ускоряет поиск по имени
- `idx_entity_name_lower` — регистронезависимый поиск
- `idx_entity_type_name` — фильтрация по типу

## Установка и запуск

### Локальный запуск (с PostgreSQL)

```bash
# 1. Установить зависимости
pip install -r requirements.txt

# 2. Запустить PostgreSQL (через Docker)
docker-compose up -d postgres

# 3. Создать тестовые данные
python generate_test_data.py

# 4. Запустить индексатор
python indexer.py sample_data

# 5. Запустить API сервер
uvicorn main:app --reload     

``` 
### Через Docker (рекомендуется) 
```bash docker-compose up --build --force-recreate
```
### Проверка работы 
```bash curl http://localhost:8000/app/stats
```