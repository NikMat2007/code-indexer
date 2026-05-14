# Code Indexer                     Python        (PostgreSQL)

##         

                                                Python                        :
- **PostgreSQL**                    
- **FastAPI**     REST API
- **Docker**                    

##                  

###         `files`
- `id` (SERIAL PRIMARY KEY)                                 
- `name` (TEXT)            
- `path` (TEXT)              

###         `code_entities`
- `id` (SERIAL PRIMARY KEY)
- `file_id` (FOREIGN KEY ? files.id)
- `entity_type` (TEXT)   'function'     'class'
- `name` (TEXT)              /      
- `start_line`, `end_line` (INTEGER)                  
- `docstring` (TEXT)               

###        
- `idx_entity_name`                          
- `idx_entity_name_lower`                            
- `idx_entity_type_name`                     

##                   

###                  (  PostgreSQL)

```bash
# 1.                       
pip install -r requirements.txt

# 2.           PostgreSQL (      Docker)
docker-compose up -d postgres

# 3.                        
python generate_test_data.py

# 4.                     
python indexer.py sample_data

# 5.           API       
uvicorn main:app --reload
### Через Docker (рекомендуется)  
```bash 
docker-compose up --build --force-recreate 
 ### Проверка работы ```bash curl http://localhost:8000/app/stats           