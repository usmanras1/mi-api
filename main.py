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


@app.get("/test-env")
def test_env():
    import os
    db_url = os.environ.get("DATABASE_URL")
    secret = os.environ.get("SECRET_KEY")
    return {
        "database_url_detected": bool(db_url),
        "secret_key_detected": bool(secret)
    }
