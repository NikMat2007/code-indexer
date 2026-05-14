import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from config import DATABASE_CONFIG
from urllib.parse import urlparse
import os


if os.environ.get('DATABASE_URL'):
    url = urlparse(os.environ['DATABASE_URL'])
    DATABASE_CONFIG = {
        'host': url.hostname,
        'port': url.port,
        'database': url.path[1:],
        'user': url.username,
        'password': url.password
    } 

DATABASE_PATH = "code_index.db"
SCHEMA = """
-- Таблица файлов 
CREATE TABLE IF NOT EXISTS files (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    path TEXT NOT NULL  
);
-- Таблица классов и функций
CREATE TABLE IF NOT EXISTS code_entities(
    id SERIAL PRIMARY KEY,
    file_id INTEGER NOT NULL,
    entity_type TEXT NOT NULL,
    name TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    docstring TEXT,
    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
);
-- Индекс делает колонку name отсортированной для бинарного поиска
CREATE INDEX IF NOT EXISTS idx_entity_name ON code_entities(name);
-- Индекс сортирует имена в нижнем регистре (LOWER(name)) для регистронезависимого бинарного поиска
CREATE INDEX IF NOT EXISTS idx_entity_name_lower ON code_entities(LOWER(name));
-- Составной индекс сортирует сначала по типу (entity_type), потом по имени (name) для бинарного поиска по фильтру "тип + имя"
CREATE INDEX IF NOT EXISTS idx_entity_type_name ON code_entities(entity_type, name);
-- Индекс сортирует file_id для быстрого поиска всех функций и классов
CREATE INDEX IF NOT EXISTS idx_entity_file_id ON code_entities(file_id);
"""

@contextmanager
def get_db():
    """Контекстный менеджер для подключения к PostgreSQL"""
    connect = None
    try:
        connect = psycopg2.connect(**DATABASE_CONFIG,cursor_factory=RealDictCursor)
        yield connect
        connect.commit()
    except Exception as e:
        if connect:
            connect.rollback()
        raise e
    
    finally:
        if connect:
            connect.close()
            
def init_db():
    """Инициализация базы данных"""
    with get_db() as connect:
        with connect.cursor() as cursor:
            for statement in SCHEMA.split(';'):
                if statement.strip(): 
                    cursor.execute(statement)
        connect.commit()
              
def clear_db():
    """Очистка БД перед новой индексацией"""
    with get_db() as connect:
        with connect.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE code_entities CASCADE")
            cursor.execute("TRUNCATE TABLE files CASCADE")
        connect.commit()
        
def insert_file(connection,name,path):
    """Вставка файла с возвратом ID"""
    with connection.cursor() as cursor:
        cursor.execute(
            """INSERT INTO files (name, path) VALUES (%s, %s)
               ON CONFLICT (name) DO UPDATE SET path = EXCLUDED.path
               RETURNING id""",
            (name, path)
        )
        return cursor.fetchone()['id']

def insert_entity(connection, file_id, entity_type, name, start_line, end_line, docstring):
    """Вставка сущности (функции или класса)"""
    with connection.cursor() as cursor:
        cursor.execute(
            """INSERT INTO code_entities 
               (file_id, entity_type, name, start_line, end_line, docstring)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (file_id, entity_type, name, start_line, end_line, docstring)
        )

def get_all_files_with_counts(limit = None,offset = None):
     """Список всех файлов + количество сущностей в каждом (с пагинацией)"""
     with get_db() as connect:
        query = """
            SELECT files.name, COUNT(code_entities.id) as entity_count
            FROM files
            LEFT JOIN code_entities ON files.id = code_entities.file_id
            GROUP BY files.id,files.name
            ORDER BY files.name
        """
        params = []
        if limit is not None:
            query += " LIMIT %s"
            params.append(limit)
            if offset is not None:
                query += " OFFSET %s"
                params.append(offset)
        with connect.cursor() as cursor:
            cursor.execute(query,params)
            rows = cursor.fetchall()
        
        return [
            {"name": row["name"],"entities_count": row["entity_count"]}
            for row in rows
        ]

def get_file_structure(file_name):
    """Полная структура файла: все функции и классы"""
    with get_db() as connect:
        with connect.cursor() as cursor:
            cursor.execute("""
                SELECT code_entities.entity_type, code_entities.name, 
                       code_entities.start_line, code_entities.end_line, 
                       code_entities.docstring
                FROM code_entities
                JOIN files ON files.id = code_entities.file_id
                WHERE files.name = %s
                ORDER BY code_entities.start_line
            """, (file_name,))
            rows = cursor.fetchall()
        if not rows:
            return []
        return [
            {
                "type": row["entity_type"],
                "name": row["name"],
                "start_line": row["start_line"],
                "end_line": row["end_line"],
                "docstring": row["docstring"] or ""
            }
            for row in rows 
        ]
            
def search_entities(keyword,entity_type = None, limit = None, offset = None):
    """Поиск по имени или docstring с фильтрацией по типу и пагинацией"""
    with get_db() as connect:
        query = """
            SELECT files.name as file_name,code_entities.entity_type,code_entities.name,
                code_entities.start_line,code_entities.end_line,code_entities.docstring
            FROM code_entities
            JOIN files ON files.id = code_entities.file_id
            WHERE 1=1
        """
        params = []
        if keyword:
            query += " AND (LOWER(code_entities.name) LIKE %s OR LOWER(code_entities.docstring) LIKE %s)"
            keyword_lower = f"%{keyword.lower()}%"     
            params.extend([keyword_lower,keyword_lower])
        if entity_type and entity_type in ['function','class']:
            query += " AND code_entities.entity_type = %s"
            params.append(entity_type)
        query += " ORDER BY files.name,code_entities.start_line"
        if limit is not None:
            query += " LIMIT %s"
            params.append(limit)
            if offset is not None:
                query += " OFFSET %s"
                params.append(offset)
        with connect.cursor() as cursor:
            cursor.execute(query,params)
            rows = cursor.fetchall()
        return [
             {
                "file": row["file_name"],
                "type": row["entity_type"],
                "name": row["name"],
                "start_line": row["start_line"],
                "end_line": row["end_line"],
                "docstring": row["docstring"] or ""
            }
            for row in rows
        ]

def get_stats():
    """Сводная статистика"""
    with get_db() as connect:
        with connect.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM files")
            files_count = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM code_entities WHERE entity_type = 'function'")
            functions_count = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM code_entities WHERE entity_type = 'class'")
            classes_count = cursor.fetchone()["count"]
            
            cursor.execute("""
                SELECT files.name,COUNT(code_entities.id) as entity_count
                FROM  files
                LEFT JOIN code_entities ON files.id = code_entities.file_id
                GROUP BY files.id,files.name
                ORDER BY entity_count DESC
                LIMIT 5    
            """)
            top_files = cursor.fetchall()
        
        return {
            "total_files": files_count,
            "total_functions": functions_count,
            "total_classes": classes_count,
            "total_entities": functions_count + classes_count,
            "top_files": [
                {"name": row["name"], "entities": row["entity_count"]}
                for row in top_files
            ]
        }