from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import psycopg2
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.environ.get("DATABASE_URL")
SECRET_KEY = os.environ.get("SECRET_KEY")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

class Task(BaseModel):
    id: Optional[int] = Field(default=None, alias="task_id")
    title: str
    description: str

    class Config:
        allow_population_by_field_name = True  # permite usar `task_id` internamente y `id` en JSON

# Crear tarea
@app.post("/tasks")
def create_task(task: Task):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (title, description) VALUES (%s, %s) RETURNING task_id;",
        (task.title, task.description)
    )
    task_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"id": task_id, "title": task.title, "description": task.description}

# Listar tareas
@app.get("/tasks", response_model=List[Task])
def get_tasks():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT task_id, title, description FROM tasks;")
    tasks = [{"id": t[0], "title": t[1], "description": t[2]} for t in cur.fetchall()]
    cur.close()
    conn.close()
    return tasks

# Obtener tarea por id
@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT task_id, title, description FROM tasks WHERE task_id=%s;", (task_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"id": row[0], "title": row[1], "description": row[2]}

# Actualizar tarea
@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task: Task):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE tasks SET title=%s, description=%s WHERE task_id=%s RETURNING task_id;",
        (task.title, task.description, task_id)
    )
    updated = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"id": task_id, "title": task.title, "description": task.description}

# Eliminar tarea
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE task_id=%s RETURNING task_id;", (task_id,))
    deleted = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}


# Modelo Pydantic para listas de tareas
class ListTask(BaseModel):
    id: Optional[int] = Field(default=None, alias="list_id")
    name: str

    class Config:
        allow_population_by_field_name = True

# Crear una lista de tareas
@app.post("/lists", response_model=ListTask)
def create_list(list_task: ListTask):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO list_task_ (name) VALUES (%s) RETURNING list_id;",
        (list_task.name,)
    )
    list_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"id": list_id, "name": list_task.name}

# Listar todas las listas
@app.get("/lists", response_model=List[ListTask])
def get_lists():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT list_id, name FROM list_task_;")
    lists = [{"id": l[0], "name": l[1]} for l in cur.fetchall()]
    cur.close()
    conn.close()
    return lists

# Obtener una lista por id
@app.get("/lists/{list_id}", response_model=ListTask)
def get_list(list_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT list_id, name FROM list_task_ WHERE list_id=%s;", (list_id  ,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="List not found")
    return {"id": row[0], "name": row[1]}

# Actualizar una lista
@app.put("/lists/{list_id}", response_model=ListTask)
def update_list(list_id: int, list_task: ListTask):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE list_task_ SET name=%s WHERE list_id=%s RETURNING list_id;",
        (list_task.name, list_id)
    )
    updated = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not updated:
        raise HTTPException(status_code=404, detail="List not found")
    return {"id": list_id, "name": list_task.name}

# Eliminar una lista
@app.delete("/lists/{list_id}")
def delete_list(list_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM list_task_ WHERE list_id=%s RETURNING list_id;", (list_id,))
    deleted = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not deleted:
        raise HTTPException(status_code=404, detail="List not found")
    return {"message": "List deleted"}

# Model Pydantic
class User(BaseModel):
    id: Optional[int] = Field(default=None, alias="user_id")
    name: str
    class Config:
        allow_population_by_field_name = True

# Crear usuari
@app.post("/users", response_model=User)
def create_user(user: User):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (name) VALUES (%s) RETURNING user_id;",
        (user.name,)
    )
    user_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"id": user_id, "name": user.name}

# Llistar tots els usuaris
@app.get("/users", response_model=List[User])
def get_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id, name FROM users;")
    users = [{"id": u[0], "name": u[1]} for u in cur.fetchall()]
    cur.close()
    conn.close()
    return users

# Obtenir usuari per id
@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id, name FROM users WHERE user_id=%s;", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Usuari no trobat")
    return {"id": row[0], "name": row[1]}

# Actualitzar usuari
@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user: User):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET name=%s WHERE user_id=%s RETURNING user_id;",
        (user.name, user_id)
    )
    updated = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not updated:
        raise HTTPException(status_code=404, detail="Usuari no trobat")
    return {"id": user_id, "name": user.name}

# Eliminar usuari
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE user_id=%s RETURNING user_id;", (user_id,))
    deleted = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not deleted:
        raise HTTPException(status_code=404, detail="Usuari no trobat")
    return {"message": "Usuari eliminat correctament"}
