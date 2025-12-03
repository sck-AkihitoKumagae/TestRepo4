"""
Task manager module for CRUD operations.
Provides high-level interface for managing projects and tasks.
"""

import logging
import os
from datetime import datetime
from typing import Optional
from storage import Storage

# Configure logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    filename=os.path.join(log_dir, "app.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)
logger = logging.getLogger(__name__)


class TaskManager:
    """High-level task manager for project and task operations."""

    STATUSES = ["やること", "進行中", "レビュー", "完了"]
    PRIORITIES = ["低", "中", "高"]
    DEFAULT_COLORS = [
        "#3B82F6",  # Blue
        "#10B981",  # Green
        "#F59E0B",  # Amber
        "#EF4444",  # Red
        "#8B5CF6",  # Purple
        "#EC4899",  # Pink
    ]

    def __init__(self, db_path: str = "tasks.db"):
        """Initialize task manager with storage backend."""
        self.storage = Storage(db_path)
        logger.info("TaskManager initialized with database: %s", db_path)

    # Project management
    def create_project(self, name: str, description: str = "", color: str = None) -> int:
        """Create a new project."""
        if not name.strip():
            raise ValueError("Project name cannot be empty")

        if color is None:
            projects = self.get_all_projects()
            color = self.DEFAULT_COLORS[len(projects) % len(self.DEFAULT_COLORS)]

        project_id = self.storage.create_project(name.strip(), description.strip(), color)
        logger.info("Created project: %s (ID: %d)", name, project_id)
        return project_id

    def get_project(self, project_id: int) -> Optional[dict]:
        """Get a project by ID."""
        return self.storage.get_project(project_id)

    def get_all_projects(self) -> list:
        """Get all projects."""
        return self.storage.get_all_projects()

    def update_project(self, project_id: int, **kwargs) -> bool:
        """Update a project."""
        success = self.storage.update_project(project_id, **kwargs)
        if success:
            logger.info("Updated project ID: %d", project_id)
        return success

    def delete_project(self, project_id: int) -> bool:
        """Delete a project and all its tasks."""
        success = self.storage.delete_project(project_id)
        if success:
            logger.info("Deleted project ID: %d", project_id)
        return success

    # Task management
    def create_task(self, project_id: int, name: str, due_date: str = None,
                    priority: str = "中", status: str = "やること",
                    progress: int = 0, assignee: str = None) -> int:
        """Create a new task."""
        if not name.strip():
            raise ValueError("Task name cannot be empty")

        if priority not in self.PRIORITIES:
            raise ValueError(f"Invalid priority. Must be one of: {self.PRIORITIES}")

        if status not in self.STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {self.STATUSES}")

        if not 0 <= progress <= 100:
            raise ValueError("Progress must be between 0 and 100")

        # Validate project exists
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project ID {project_id} does not exist")

        task_id = self.storage.create_task(
            project_id, name.strip(), due_date, priority, status, progress, assignee
        )
        logger.info("Created task: %s (ID: %d) in project ID: %d", name, task_id, project_id)
        return task_id

    def get_task(self, task_id: int) -> Optional[dict]:
        """Get a task by ID."""
        return self.storage.get_task(task_id)

    def get_tasks_by_project(self, project_id: int) -> list:
        """Get all tasks for a project."""
        return self.storage.get_tasks_by_project(project_id)

    def get_tasks_by_status(self, project_id: int, status: str) -> list:
        """Get tasks by project and status."""
        if status not in self.STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {self.STATUSES}")
        return self.storage.get_tasks_by_status(project_id, status)

    def update_task(self, task_id: int, **kwargs) -> bool:
        """Update a task."""
        # Validate priority if provided
        if "priority" in kwargs and kwargs["priority"] not in self.PRIORITIES:
            raise ValueError(f"Invalid priority. Must be one of: {self.PRIORITIES}")

        # Validate status if provided
        if "status" in kwargs and kwargs["status"] not in self.STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {self.STATUSES}")

        # Validate progress if provided
        if "progress" in kwargs:
            progress = kwargs["progress"]
            if not isinstance(progress, int) or not 0 <= progress <= 100:
                raise ValueError("Progress must be an integer between 0 and 100")

        success = self.storage.update_task(task_id, **kwargs)
        if success:
            logger.info("Updated task ID: %d", task_id)
        return success

    def update_task_status(self, task_id: int, status: str) -> bool:
        """Update task status (convenience method for drag-and-drop)."""
        return self.update_task(task_id, status=status)

    def update_task_progress(self, task_id: int, progress: int) -> bool:
        """Update task progress."""
        return self.update_task(task_id, progress=progress)

    def delete_task(self, task_id: int) -> bool:
        """Delete a task."""
        success = self.storage.delete_task(task_id)
        if success:
            logger.info("Deleted task ID: %d", task_id)
        return success

    # Search and filter
    def search_tasks(self, project_id: int, keyword: str = None,
                     status: str = None, assignee: str = None,
                     priority: str = None) -> list:
        """Search and filter tasks."""
        return self.storage.search_tasks(project_id, keyword, status, assignee, priority)

    def get_tasks_sorted(self, project_id: int, sort_by: str = "priority") -> list:
        """Get tasks sorted by specified field."""
        tasks = self.get_tasks_by_project(project_id)

        if sort_by == "priority":
            priority_order = {"高": 0, "中": 1, "低": 2}
            tasks.sort(key=lambda t: priority_order.get(t["priority"], 1))
        elif sort_by == "due_date":
            tasks.sort(key=lambda t: t["due_date"] or "9999-12-31")
        elif sort_by == "status":
            status_order = {s: i for i, s in enumerate(self.STATUSES)}
            tasks.sort(key=lambda t: status_order.get(t["status"], 0))
        elif sort_by == "name":
            tasks.sort(key=lambda t: t["name"])

        return tasks

    # Backup operations
    def export_backup(self, filepath: str = None) -> bool:
        """Export data to JSON backup file."""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"backup_{timestamp}.json"

        success = self.storage.export_to_json(filepath)
        if success:
            logger.info("Exported backup to: %s", filepath)
        return success

    def import_backup(self, filepath: str) -> bool:
        """Import data from JSON backup file."""
        success = self.storage.import_from_json(filepath)
        if success:
            logger.info("Imported backup from: %s", filepath)
        return success

    # Statistics
    def get_project_stats(self, project_id: int) -> dict:
        """Get statistics for a project."""
        tasks = self.get_tasks_by_project(project_id)

        stats = {
            "total": len(tasks),
            "by_status": {},
            "by_priority": {},
            "avg_progress": 0
        }

        for status in self.STATUSES:
            stats["by_status"][status] = sum(1 for t in tasks if t["status"] == status)

        for priority in self.PRIORITIES:
            stats["by_priority"][priority] = sum(1 for t in tasks if t["priority"] == priority)

        if tasks:
            stats["avg_progress"] = sum(t["progress"] for t in tasks) / len(tasks)

        return stats
