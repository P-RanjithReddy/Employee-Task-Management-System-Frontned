# Employee Task Management System (Fixed Version)

## Tech stack
Python, FastAPI, SQLite (SQL database), HTML, CSS, JavaScript, Jinja2.

SQLite is used so the app runs instantly without installing/configuring MySQL. It fulfills SQL table, CRUD, JOIN, and dynamic data requirements.

## Run (Windows / VS Code)
1. Extract this ZIP.
2. Open the extracted folder in VS Code.
3. Open Terminal > New Terminal in the project folder.
4. Install pinned compatible packages:
   `python -m pip install -r requirements.txt`
5. Run:
   `python -m uvicorn main:app --reload`
6. Frontend: http://127.0.0.1:8000
7. Swagger: http://127.0.0.1:8000/docs

## Important
The HTML routes use `templates.TemplateResponse(request=request, name="...", context={})` keyword arguments. This avoids the tuple/dict-key error seen with incompatible Starlette/Jinja templating signatures.

## Features
- Employee registration and listing
- Task creation and assignment
- View tasks with SQL JOIN (employee name and department)
- Search/filter employees and tasks
- Inline status update (Pending / In Progress / Completed)
- Delete task
- API validation and error handling
- Auto-created database and seeded sample data

## APIs
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/employees` | Add employee |
| GET | `/api/employees` | View all employees |
| POST | `/api/tasks` | Add task |
| GET | `/api/tasks` | View all tasks with employee JOIN |
| GET | `/api/tasks/employee/{employee_id}` | Search task by employee |
| PATCH | `/api/tasks/{task_id}/status` | Update task status |
| DELETE | `/api/tasks/{task_id}` | Delete task |

## Screenshots for submission
Capture Dashboard, Employee Registration, Employees table, Tasks table, and changed task status using Windows + Shift + S.
