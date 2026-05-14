from fastapi import FastAPI,HTTPException,Query
from fastapi.responses import JSONResponse 
from typing import Optional 
import database as db 

app = FastAPI(
    title="Code Indexer API",
    description="Поиск функций и классов в Python файлах (PostgreSQL)"
)

@app.on_event("startup")
async def startup_event():
    db.init_db()
    print("API сервер запущен с PostgreSQL")

@app.get("/api/files")
def list_files(
    limit: Optional[int] = Query(None,ge=1,description="Максимальное количество записей"),
    offset: Optional[int] = Query(None,ge=0,description="Смещение (пагинация)")
):
    """Список всех проиндексированных файлов с количеством функций/классов"""
    result = db.get_all_files_with_counts(limit = limit,offset = offset if limit else None)
    return JSONResponse(content=result)    

@app.get("/api/files/{name}/structure")
def get_file_structure(name: str):
    """Полная структура файла: все функции и классы с номерами строк и docstring"""
    result = db.get_file_structure(name)
    if not result:
        return JSONResponse(content=[])
    return JSONResponse(content=result)


@app.get("/api/search")
def search(
    q: str = Query(...,description="Ключевое слово для поиска"),
    type: Optional[str] = Query(None,regex="^(function|class)$",description="Фильтр по типу сущности"),
    limit: Optional[int] = Query(None,ge=1,description="Максимальное количество записей"),
    offset: Optional[int] = Query(None,ge=0,description="Смещение (пагинация)")
):
    """Поиск функций и классов по ключевому слову (регистронезависимо)"""
    if not q:
        return JSONResponse(content=[])
    result = db.search_entities(keyword=q,
                                entity_type=type,
                                limit=limit,
                                offset=offset if limit else None
    )
    return JSONResponse(content=result)

    
@app.get("/app/stats")
def get_stats():
    """Сводная статистика по индексу"""
    result = db.get_stats()
    return JSONResponse(content=result)

@app.exception_handler(404)
async def not_found_handler(r):
    return JSONResponse(content=[],status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)