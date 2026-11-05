-- Employee Task Management System SQL schema and sample records
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Employee (
 Employee_ID INTEGER PRIMARY KEY AUTOINCREMENT,
 Employee_Name VARCHAR(100) NOT NULL,
 Department VARCHAR(80) NOT NULL,
 Email VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Task (
 Task_ID INTEGER PRIMARY KEY AUTOINCREMENT,
 Employee_ID INTEGER NOT NULL,
 Task_Name VARCHAR(200) NOT NULL,
 Task_Status VARCHAR(20) NOT NULL DEFAULT 'Pending'
 CHECK(Task_Status IN ('Pending','In Progress','Completed')),
 Due_Date DATE NOT NULL,
 FOREIGN KEY(Employee_ID) REFERENCES Employee(Employee_ID) ON DELETE CASCADE
);

INSERT OR IGNORE INTO Employee(Employee_ID,Employee_Name,Department,Email) VALUES
(1,'Aarav Sharma','IT','aarav@example.com'),
(2,'Priya Reddy','HR','priya@example.com'),
(3,'Rahul Kumar','Finance','rahul@example.com');

INSERT OR IGNORE INTO Task(Task_ID,Employee_ID,Task_Name,Task_Status,Due_Date) VALUES
(1,1,'Prepare API documentation','In Progress','2026-11-07'),
(2,2,'Update employee onboarding','Pending','2026-11-08'),
(3,3,'Review monthly expense report','Completed','2026-11-04');

-- Required JOIN
SELECT t.Task_ID,t.Task_Name,t.Task_Status,t.Due_Date,
       e.Employee_Name,e.Department,e.Email
FROM Task t JOIN Employee e ON t.Employee_ID=e.Employee_ID
ORDER BY t.Due_Date;

-- SQL aggregate sample
SELECT Task_Status,COUNT(*) AS Total_Tasks FROM Task GROUP BY Task_Status;
