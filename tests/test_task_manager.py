"""
Tests for task manager module.
"""

import os
import unittest
import tempfile
from task_manager import TaskManager


class TestTaskManager(unittest.TestCase):
    """Test cases for TaskManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.manager = TaskManager(self.db_path)

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        # Clean up log directory if empty
        log_dir = "logs"
        if os.path.exists(log_dir):
            try:
                for f in os.listdir(log_dir):
                    os.remove(os.path.join(log_dir, f))
                os.rmdir(log_dir)
            except OSError:
                pass
        os.rmdir(self.temp_dir)

    def test_create_project_success(self):
        """Test successful project creation."""
        project_id = self.manager.create_project("Test Project", "Description")
        self.assertGreater(project_id, 0)

    def test_create_project_empty_name_raises(self):
        """Test that empty project name raises ValueError."""
        with self.assertRaises(ValueError):
            self.manager.create_project("")

    def test_create_project_auto_color(self):
        """Test that projects get auto-assigned colors."""
        id1 = self.manager.create_project("Project 1")
        id2 = self.manager.create_project("Project 2")

        project1 = self.manager.get_project(id1)
        project2 = self.manager.get_project(id2)

        self.assertIsNotNone(project1["color"])
        self.assertIsNotNone(project2["color"])

    def test_get_all_projects(self):
        """Test getting all projects."""
        self.manager.create_project("Project 1")
        self.manager.create_project("Project 2")

        projects = self.manager.get_all_projects()
        self.assertEqual(len(projects), 2)

    def test_update_project(self):
        """Test updating a project."""
        project_id = self.manager.create_project("Original")
        success = self.manager.update_project(project_id, name="Updated")

        self.assertTrue(success)
        project = self.manager.get_project(project_id)
        self.assertEqual(project["name"], "Updated")

    def test_delete_project(self):
        """Test deleting a project."""
        project_id = self.manager.create_project("To Delete")
        success = self.manager.delete_project(project_id)

        self.assertTrue(success)
        self.assertIsNone(self.manager.get_project(project_id))

    def test_create_task_success(self):
        """Test successful task creation."""
        project_id = self.manager.create_project("Project")
        task_id = self.manager.create_task(
            project_id, "Test Task", "2025-12-31", "高", "進行中", 50, "user1"
        )
        self.assertGreater(task_id, 0)

    def test_create_task_empty_name_raises(self):
        """Test that empty task name raises ValueError."""
        project_id = self.manager.create_project("Project")
        with self.assertRaises(ValueError):
            self.manager.create_task(project_id, "")

    def test_create_task_invalid_priority_raises(self):
        """Test that invalid priority raises ValueError."""
        project_id = self.manager.create_project("Project")
        with self.assertRaises(ValueError):
            self.manager.create_task(project_id, "Task", priority="invalid")

    def test_create_task_invalid_status_raises(self):
        """Test that invalid status raises ValueError."""
        project_id = self.manager.create_project("Project")
        with self.assertRaises(ValueError):
            self.manager.create_task(project_id, "Task", status="invalid")

    def test_create_task_invalid_progress_raises(self):
        """Test that invalid progress raises ValueError."""
        project_id = self.manager.create_project("Project")
        with self.assertRaises(ValueError):
            self.manager.create_task(project_id, "Task", progress=150)

    def test_create_task_nonexistent_project_raises(self):
        """Test that creating task for nonexistent project raises ValueError."""
        with self.assertRaises(ValueError):
            self.manager.create_task(99999, "Task")

    def test_get_tasks_by_project(self):
        """Test getting tasks by project."""
        project_id = self.manager.create_project("Project")
        self.manager.create_task(project_id, "Task 1")
        self.manager.create_task(project_id, "Task 2")

        tasks = self.manager.get_tasks_by_project(project_id)
        self.assertEqual(len(tasks), 2)

    def test_get_tasks_by_status(self):
        """Test getting tasks by status."""
        project_id = self.manager.create_project("Project")
        self.manager.create_task(project_id, "Task 1", status="やること")
        self.manager.create_task(project_id, "Task 2", status="進行中")

        tasks = self.manager.get_tasks_by_status(project_id, "やること")
        self.assertEqual(len(tasks), 1)

    def test_get_tasks_by_status_invalid_raises(self):
        """Test that invalid status raises ValueError."""
        project_id = self.manager.create_project("Project")
        with self.assertRaises(ValueError):
            self.manager.get_tasks_by_status(project_id, "invalid")

    def test_update_task(self):
        """Test updating a task."""
        project_id = self.manager.create_project("Project")
        task_id = self.manager.create_task(project_id, "Original")
        success = self.manager.update_task(task_id, name="Updated")

        self.assertTrue(success)
        task = self.manager.get_task(task_id)
        self.assertEqual(task["name"], "Updated")

    def test_update_task_status(self):
        """Test updating task status."""
        project_id = self.manager.create_project("Project")
        task_id = self.manager.create_task(project_id, "Task", status="やること")
        success = self.manager.update_task_status(task_id, "完了")

        self.assertTrue(success)
        task = self.manager.get_task(task_id)
        self.assertEqual(task["status"], "完了")

    def test_update_task_progress(self):
        """Test updating task progress."""
        project_id = self.manager.create_project("Project")
        task_id = self.manager.create_task(project_id, "Task", progress=0)
        success = self.manager.update_task_progress(task_id, 75)

        self.assertTrue(success)
        task = self.manager.get_task(task_id)
        self.assertEqual(task["progress"], 75)

    def test_delete_task(self):
        """Test deleting a task."""
        project_id = self.manager.create_project("Project")
        task_id = self.manager.create_task(project_id, "To Delete")
        success = self.manager.delete_task(task_id)

        self.assertTrue(success)
        self.assertIsNone(self.manager.get_task(task_id))

    def test_search_tasks(self):
        """Test searching tasks."""
        project_id = self.manager.create_project("Project")
        self.manager.create_task(project_id, "Design mockup", priority="高")
        self.manager.create_task(project_id, "Write tests", priority="中")

        results = self.manager.search_tasks(project_id, keyword="Design")
        self.assertEqual(len(results), 1)

    def test_get_tasks_sorted(self):
        """Test getting sorted tasks."""
        project_id = self.manager.create_project("Project")
        self.manager.create_task(project_id, "Low priority", priority="低")
        self.manager.create_task(project_id, "High priority", priority="高")
        self.manager.create_task(project_id, "Medium priority", priority="中")

        tasks = self.manager.get_tasks_sorted(project_id, "priority")
        self.assertEqual(tasks[0]["name"], "High priority")
        self.assertEqual(tasks[2]["name"], "Low priority")

    def test_get_project_stats(self):
        """Test getting project statistics."""
        project_id = self.manager.create_project("Project")
        self.manager.create_task(project_id, "Task 1", status="やること", progress=0)
        self.manager.create_task(project_id, "Task 2", status="進行中", progress=50)
        self.manager.create_task(project_id, "Task 3", status="完了", progress=100)

        stats = self.manager.get_project_stats(project_id)

        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["by_status"]["やること"], 1)
        self.assertEqual(stats["by_status"]["進行中"], 1)
        self.assertEqual(stats["by_status"]["完了"], 1)
        self.assertEqual(stats["avg_progress"], 50)

    def test_export_backup(self):
        """Test exporting backup."""
        project_id = self.manager.create_project("Project")
        self.manager.create_task(project_id, "Task")

        backup_path = os.path.join(self.temp_dir, "backup.json")
        success = self.manager.export_backup(backup_path)

        self.assertTrue(success)
        self.assertTrue(os.path.exists(backup_path))

        # Clean up
        os.remove(backup_path)


if __name__ == "__main__":
    unittest.main()
