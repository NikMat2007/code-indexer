import os 
import ast 
from pathlib import Path
import database as db
import sys


class PythonParser(ast.NodeVisitor):
    def __init__(self,file_path,file_name,conn):
            self.file_path = file_path
            self.file_name = file_name 
            self.conn = conn
            self.file_id = None
            self.source_lines = None
    def parser(self):
        try:
            with open(self.file_path , 'r',encoding='utf-8') as f:
                source = f.read()
            self.source_lines = source.splitlines()
            
            self.file_id = db.insert_file(self.conn,self.file_name,str(self.file_path))
            
            tree = ast.parse(source,filename=self.file_path)
            self.visit(tree)
        except SyntaxError as e:
            print(f"Syntax error in {self.file_name}: {e}")
        except Exception as e:
            print(f"Error parsing {self.file_name}: {e}")
            
    def visit_FunctionDef(self,node):
        self._extract_entity(node,'function')
        self.generic_visit(node)
        
    def visit_ClassDef(self,node):
        self._extract_entity(node,'class')
        self.generic_visit(node)
    
    def _extract_entity(self,node,entity_type):
        name = node.name 
        start_line = node.lineno
        end_line = node.end_lineno if hasattr(node,'end_lineno') else start_line
        
        docstring = ast.get_docstring(node) or ""
        
        db.insert_entity(
            self.conn,self.file_id,entity_type,
            name,start_line,end_line,docstring
        )
def index_directory(directory_path):
        """Индексация всех Python файлов в директории"""
        print(f"\n Индексация директории: {directory_path}")
        
        db.init_db()
        db.clear_db()
        
        py_files = list(Path(directory_path).rglob("*.py"))
        total = len(py_files)
        
        print(f" Найдено {total} .py файлов")
        print(f" База данных: PostgreSQL")
        
        with db.get_db() as conn:
            for i,py_file in enumerate(py_files,1):
                parser = PythonParser(py_file,py_file.name,conn)
                parser.parser()
                print(f"[{i}/{total}]{py_file.name}")
                
        stats = db.get_stats()
        print("\n" + "=" * 50)
        print(" ИТОГИ ИНДЕКСАЦИИ:")
        print(f" Файлов: {stats['total_files']}")
        print(f" Функций: {stats['total_functions']}")
        print(f" Классов: {stats['total_classes']}")
        print(f" Всего сущностей: {stats['total_entities']}")
        print("=" * 50 + "\n")

index_directory(sys.argv[1])
    