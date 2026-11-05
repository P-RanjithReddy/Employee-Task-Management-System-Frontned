from pathlib import Path
import sqlite3
from contextlib import contextmanager
from datetime import date

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr, Field

ROOT = Path(__file__).resolve().parent
DB_FILE = ROOT / "employee_tasks.db"

app = FastAPI(title="Employee Task Management System", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")
templates = Jinja2Templates(directory=str(ROOT / "templates"))

@contextmanager
def db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def initialize_database():
    with db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Employee(
                Employee_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Employee_Name TEXT NOT NULL,
                Department TEXT NOT NULL,
                Email TEXT NOT NULL UNIQUE
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Task(
                Task_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Employee_ID INTEGER NOT NULL,
                Task_Name TEXT NOT NULL,
                Task_Status TEXT NOT NULL DEFAULT 'Pending'
                    CHECK(Task_Status IN ('Pending','In Progress','Completed')),
                Due_Date TEXT NOT NULL,
                FOREIGN KEY(Employee_ID) REFERENCES Employee(Employee_ID) ON DELETE CASCADE
            )
        """)
        if conn.execute("SELECT COUNT(*) FROM Employee").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO Employee(Employee_Name,Department,Email) VALUES(?,?,?)",
                [
                    ("Aarav Sharma", "IT", "aarav@example.com"),
                    ("Priya Reddy", "HR", "priya@example.com"),
                    ("Rahul Kumar", "Finance", "rahul@example.com"),
                ],
            )
        if conn.execute("SELECT COUNT(*) FROM Task").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO Task(Employee_ID,Task_Name,Task_Status,Due_Date) VALUES(?,?,?,?)",
                [
                    (1, "Prepare API documentation", "In Progress", "2026-11-07"),
                    (2, "Update employee onboarding", "Pending", "2026-11-08"),
                    (3, "Review monthly expense report", "Completed", "2026-11-04"),
                ],
            )

@app.on_event("startup")
def on_startup():
    initialize_database()

class EmployeeCreate(BaseModel):
    employee_name: str = Field(min_length=2, max_length=100)
    department: str = Field(min_length=2, max_length=80)
    email: EmailStr

class TaskCreate(BaseModel):
    employee_id: int
    task_name: str = Field(min_length=2, max_length=200)
    task_status: str = "Pending"
    due_date: date

class TaskStatusUpdate(BaseModel):
    task_status: str

STATUSES = {"Pending", "In Progress", "Completed"}

@app.post("/api/employees", status_code=201)
def create_employee(data: EmployeeCreate):
    try:
        with db_connection() as conn:
            cur = conn.execute(
                "INSERT INTO Employee(Employee_Name,Department,Email) VALUES(?,?,?)",
                (data.employee_name.strip(), data.department.strip(), str(data.email)),
            )
            result = conn.execute(
                "SELECT * FROM Employee WHERE Employee_ID=?", (cur.lastrowid,)
            ).fetchone()
            return dict(result)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Email already exists.")

@app.get("/api/employees")
def get_employees():
    with db_connection() as conn:
        rows = conn.execute("SELECT * FROM Employee ORDER BY Employee_ID DESC").fetchall()
        return [dict(row) for row in rows]

@app.post("/api/tasks", status_code=201)
def create_task(data: TaskCreate):
    if data.task_status not in STATUSES:
        raise HTTPException(status_code=400, detail="Invalid task status.")
    try:
        with db_connection() as conn:
            cur = conn.execute(
                """INSERT INTO Task(Employee_ID,Task_Name,Task_Status,Due_Date)
                   VALUES(?,?,?,?)""",
                (data.employee_id, data.task_name.strip(), data.task_status, data.due_date.isoformat()),
            )
            row = conn.execute(
                """SELECT t.*, e.Employee_Name, e.Department, e.Email
                   FROM Task t JOIN Employee e ON e.Employee_ID=t.Employee_ID
                   WHERE t.Task_ID=?""", (cur.lastrowid,)
            ).fetchone()
            return dict(row)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Employee ID does not exist.")

@app.get("/api/tasks")
def get_tasks():
    with db_connection() as conn:
        rows = conn.execute(
            """SELECT t.*, e.Employee_Name, e.Department, e.Email
               FROM Task t INNER JOIN Employee e ON e.Employee_ID=t.Employee_ID
               ORDER BY t.Due_Date ASC, t.Task_ID DESC"""
        ).fetchall()
        return [dict(row) for row in rows]

@app.get("/api/tasks/employee/{employee_id}")
def get_tasks_by_employee(employee_id: int):
    with db_connection() as conn:
        rows = conn.execute(
            """SELECT t.*, e.Employee_Name, e.Department
               FROM Task t JOIN Employee e ON e.Employee_ID=t.Employee_ID
               WHERE t.Employee_ID=? ORDER BY t.Due_Date""",
            (employee_id,),
        ).fetchall()
        return [dict(row) for row in rows]

@app.patch("/api/tasks/{task_id}/status")
def update_task_status(task_id: int, data: TaskStatusUpdate):
    if data.task_status not in STATUSES:
        raise HTTPException(status_code=400, detail="Status must be Pending, In Progress, or Completed.")
    with db_connection() as conn:
        cur = conn.execute(
            "UPDATE Task SET Task_Status=? WHERE Task_ID=?",
            (data.task_status, task_id),
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found.")
        row = conn.execute(
            """SELECT t.*, e.Employee_Name, e.Department
               FROM Task t JOIN Employee e ON e.Employee_ID=t.Employee_ID
               WHERE t.Task_ID=?""", (task_id,)
        ).fetchone()
        return dict(row)

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    with db_connection() as conn:
        cur = conn.execute("DELETE FROM Task WHERE Task_ID=?", (task_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found.")
        return {"message": "Task deleted successfully."}

# IMPORTANT: Starlette's current TemplateResponse signature is
# TemplateResponse(request, name, context). Use keyword arguments to avoid
# tuple/dict argument confusion across versions.
@app.get("/", response_class=__import__("fastapi").responses.HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})

@app.get("/employees", response_class=__import__("fastapi").responses.HTMLResponse)
def employees_page(request: Request):
    return templates.TemplateResponse(request=request, name="employees.html", context={})

@app.get("/tasks", response_class=__import__("fastapi").responses.HTMLResponse)
def tasks_page(request: Request):
    return templates.TemplateResponse(request=request, name="tasks.html", context={})

@app.get("/register", response_class=__import__("fastapi").responses.HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html", context={})

@app.get("/add-task", response_class=__import__("fastapi").responses.HTMLResponse)
def add_task_page(request: Request):
    return templates.TemplateResponse(request=request, name="add_task.html", context={})
