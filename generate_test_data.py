# generate_test_data.py
import os
from pathlib import Path

def generate_test_files(output_dir="sample_data", num_files=30):
    """Генерация тестовых Python файлов для индексации"""
    Path(output_dir).mkdir(exist_ok=True)
    
    templates = {
        "controller": '''
class {name}Controller:
    """Контроллер для управления {name}"""
    
    def __init__(self):
        """Инициализация контроллера"""
        self.name = "{name}"
    
    def get_{name}(self, id: int):
        """Получить {name} по идентификатору"""
        return {{"id": id, "name": self.name}}
    
    def create_{name}(self, data: dict):
        """Создать новый {name}"""
        return {{"status": "created", "data": data}}
    
    def update_{name}(self, id: int, data: dict):
        """Обновить {name}"""
        return {{"status": "updated"}}
    
    def delete_{name}(self, id: int):
        """Удалить {name}"""
        return {{"status": "deleted"}}
''',
        "service": '''
class {name}Service:
    """Сервис для работы с {name}"""
    
    def process_{name}(self, data):
        """Обработка данных {name}"""
        return self._validate(data)
    
    def _validate(self, data):
        """Внутренняя валидация"""
        return True
    
    def transform_{name}(self, data):
        """Трансформация данных"""
        return {{"transformed": data}}
''',
        "repository": '''
class {name}Repository:
    """Репозиторий для {name}"""
    
    def __init__(self):
        self._storage = []
    
    def find_by_id(self, id: int):
        """Поиск по ID"""
        return next((item for item in self._storage if item["id"] == id), None)
    
    def save(self, entity):
        """Сохранить сущность"""
        self._storage.append(entity)
        return entity
    
    def delete(self, id: int):
        """Удалить сущность"""
        self._storage = [item for item in self._storage if item["id"] != id]
    
    def find_all(self):
        """Найти все записи"""
        return self._storage
'''
    }
    
    names = ["user", "product", "order", "auth", "payment", "notification", 
             "report", "analytics", "config", "cache", "logger", "validator",
             "parser", "formatter", "serializer", "deserializer", "mapper",
             "factory", "builder", "handler", "middleware", "decorator",
             "adapter", "proxy", "observer", "strategy", "state", "command",
             "facade", "singleton"]
    
    print(f" Создание {num_files} тестовых файлов в папке '{output_dir}/'...")
    
    for i in range(num_files):
        name = names[i % len(names)]
        file_type = list(templates.keys())[i % 3]
        template = templates[file_type]
        
        content = template.format(name=name.capitalize())
        
        filename = f"{name}_{file_type}.py"
        filepath = Path(output_dir) / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        
        print(f" Created: {filename}")
    
    print(f"\n Успешно создано {num_files} файлов в папке '{output_dir}/'")

if __name__ == "__main__":
    import sys
    output = sys.argv[1] if len(sys.argv) > 1 else "sample_data"
    num = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    generate_test_files(output, num)