"""
SQLite storage manager for task management application.
Handles database initialization and CRUD operations for projects and tasks.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Optional


class Storage:
    """SQLite database manager for persistent storage."""

    def __init__(self, db_path: str = "tasks.db"):
        """Initialize storage with database path."""
        self.db_path = db_path
        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_database(self) -> None:
        """Initialize database tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Create projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                color TEXT DEFAULT '#3B82F6',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                due_date TEXT,
                priority TEXT DEFAULT '中',
                status TEXT DEFAULT 'やること',
                progress INTEGER DEFAULT 0,
                assignee TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        conn.close()

    # Project operations
    def create_project(self, name: str, description: str = "", color: str = "#3B82F6") -> int:
        """Create a new project and return its ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO projects (name, description, color) VALUES (?, ?, ?)",
            (name, description, color)
        )
        project_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return project_id

    def get_project(self, project_id: int) -> Optional[dict]:
        """Get a project by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_all_projects(self) -> list:
        """Get all projects."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def update_project(self, project_id: int, **kwargs) -> bool:
        """Update a project's fields."""
        if not kwargs:
            return False

        allowed_fields = {"name", "description", "color"}
        fields = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not fields:
            return False

        fields["updated_at"] = datetime.now().isoformat()
        set_clause = ", ".join(f"{k} = ?" for k in fields.keys())

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE projects SET {set_clause} WHERE id = ?",
            (*fields.values(), project_id)
        )
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0

    def delete_project(self, project_id: int) -> bool:
        """Delete a project and all its tasks."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE project_id = ?", (project_id,))
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0

    # Task operations
    def create_task(self, project_id: int, name: str, due_date: str = None,
                    priority: str = "中", status: str = "やること",
                    progress: int = 0, assignee: str = None) -> int:
        """Create a new task and return its ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO tasks (project_id, name, due_date, priority, status, progress, assignee)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (project_id, name, due_date, priority, status, progress, assignee)
        )
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id

    def get_task(self, task_id: int) -> Optional[dict]:
        """Get a task by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_tasks_by_project(self, project_id: int) -> list:
        """Get all tasks for a project."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tasks WHERE project_id = ? ORDER BY created_at DESC",
            (project_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_tasks_by_status(self, project_id: int, status: str) -> list:
        """Get tasks by project and status."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tasks WHERE project_id = ? AND status = ? ORDER BY created_at DESC",
            (project_id, status)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def update_task(self, task_id: int, **kwargs) -> bool:
        """Update a task's fields."""
        if not kwargs:
            return False

        allowed_fields = {"name", "due_date", "priority", "status", "progress", "assignee"}
        fields = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not fields:
            return False

        fields["updated_at"] = datetime.now().isoformat()
        set_clause = ", ".join(f"{k} = ?" for k in fields.keys())

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE tasks SET {set_clause} WHERE id = ?",
            (*fields.values(), task_id)
        )
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0

    def delete_task(self, task_id: int) -> bool:
        """Delete a task."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0

    def search_tasks(self, project_id: int, keyword: str = None,
                     status: str = None, assignee: str = None,
                     priority: str = None) -> list:
        """Search and filter tasks."""
        conn = self._get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM tasks WHERE project_id = ?"
        params = [project_id]

        if keyword:
            query += " AND name LIKE ?"
            params.append(f"%{keyword}%")

        if status:
            query += " AND status = ?"
            params.append(status)

        if assignee:
            query += " AND assignee = ?"
            params.append(assignee)

        if priority:
            query += " AND priority = ?"
            params.append(priority)

        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # Backup operations
    def export_to_json(self, filepath: str) -> bool:
        """Export all data to JSON file."""
        try:
            data = {
                "projects": self.get_all_projects(),
                "tasks": []
            }

            for project in data["projects"]:
                tasks = self.get_tasks_by_project(project["id"])
                data["tasks"].extend(tasks)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return True
        except (OSError, IOError):
            return False

    def import_from_json(self, filepath: str) -> bool:
        """Import data from JSON file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Create projects
            project_id_map = {}
            for project in data.get("projects", []):
                old_id = project.pop("id", None)
                project.pop("created_at", None)
                project.pop("updated_at", None)
                new_id = self.create_project(**project)
                if old_id:
                    project_id_map[old_id] = new_id

            # Create tasks with mapped project IDs
            for task in data.get("tasks", []):
                old_project_id = task.pop("project_id", None)
                task.pop("id", None)
                task.pop("created_at", None)
                task.pop("updated_at", None)

                if old_project_id in project_id_map:
                    task["project_id"] = project_id_map[old_project_id]
                    self.create_task(**task)

            return True
        except (OSError, IOError, json.JSONDecodeError, KeyError):
            return False
