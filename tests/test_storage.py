"""
Tests for storage module.
"""

import os
import unittest
import tempfile
from storage import Storage


class TestStorage(unittest.TestCase):
    """Test cases for Storage class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.storage = Storage(self.db_path)

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)

    def test_create_project(self):
        """Test creating a project."""
        project_id = self.storage.create_project("Test Project", "Description", "#FF0000")
        self.assertIsNotNone(project_id)
        self.assertGreater(project_id, 0)

    def test_get_project(self):
        """Test getting a project."""
        project_id = self.storage.create_project("Test Project", "Description", "#FF0000")
        project = self.storage.get_project(project_id)

        self.assertIsNotNone(project)
        self.assertEqual(project["name"], "Test Project")
        self.assertEqual(project["description"], "Description")
        self.assertEqual(project["color"], "#FF0000")

    def test_get_all_projects(self):
        """Test getting all projects."""
        self.storage.create_project("Project 1")
        self.storage.create_project("Project 2")

        projects = self.storage.get_all_projects()
        self.assertEqual(len(projects), 2)

    def test_update_project(self):
        """Test updating a project."""
        project_id = self.storage.create_project("Original", "Desc")
        success = self.storage.update_project(project_id, name="Updated")

        self.assertTrue(success)

        project = self.storage.get_project(project_id)
        self.assertEqual(project["name"], "Updated")

    def test_delete_project(self):
        """Test deleting a project."""
        project_id = self.storage.create_project("To Delete")
        success = self.storage.delete_project(project_id)

        self.assertTrue(success)

        project = self.storage.get_project(project_id)
        self.assertIsNone(project)

    def test_create_task(self):
        """Test creating a task."""
        project_id = self.storage.create_project("Project")
        task_id = self.storage.create_task(
            project_id, "Test Task", "2025-12-31", "高", "進行中", 50, "user1"
        )

        self.assertIsNotNone(task_id)
        self.assertGreater(task_id, 0)

    def test_get_task(self):
        """Test getting a task."""
        project_id = self.storage.create_project("Project")
        task_id = self.storage.create_task(
            project_id, "Test Task", "2025-12-31", "高", "進行中", 50, "user1"
        )

        task = self.storage.get_task(task_id)

        self.assertIsNotNone(task)
        self.assertEqual(task["name"], "Test Task")
        self.assertEqual(task["priority"], "高")
        self.assertEqual(task["status"], "進行中")
        self.assertEqual(task["progress"], 50)

    def test_get_tasks_by_project(self):
        """Test getting tasks by project."""
        project_id = self.storage.create_project("Project")
        self.storage.create_task(project_id, "Task 1")
        self.storage.create_task(project_id, "Task 2")

        tasks = self.storage.get_tasks_by_project(project_id)
        self.assertEqual(len(tasks), 2)

    def test_get_tasks_by_status(self):
        """Test getting tasks by status."""
        project_id = self.storage.create_project("Project")
        self.storage.create_task(project_id, "Task 1", status="やること")
        self.storage.create_task(project_id, "Task 2", status="進行中")
        self.storage.create_task(project_id, "Task 3", status="やること")

        tasks = self.storage.get_tasks_by_status(project_id, "やること")
        self.assertEqual(len(tasks), 2)

    def test_update_task(self):
        """Test updating a task."""
        project_id = self.storage.create_project("Project")
        task_id = self.storage.create_task(project_id, "Original")
        success = self.storage.update_task(task_id, name="Updated", status="完了")

        self.assertTrue(success)

        task = self.storage.get_task(task_id)
        self.assertEqual(task["name"], "Updated")
        self.assertEqual(task["status"], "完了")

    def test_delete_task(self):
        """Test deleting a task."""
        project_id = self.storage.create_project("Project")
        task_id = self.storage.create_task(project_id, "To Delete")
        success = self.storage.delete_task(task_id)

        self.assertTrue(success)

        task = self.storage.get_task(task_id)
        self.assertIsNone(task)

    def test_search_tasks(self):
        """Test searching tasks."""
        project_id = self.storage.create_project("Project")
        self.storage.create_task(project_id, "Design mockup", priority="高")
        self.storage.create_task(project_id, "Write tests", priority="中")
        self.storage.create_task(project_id, "Design review", priority="高")

        # Search by keyword
        results = self.storage.search_tasks(project_id, keyword="Design")
        self.assertEqual(len(results), 2)

        # Search by priority
        results = self.storage.search_tasks(project_id, priority="高")
        self.assertEqual(len(results), 2)

    def test_export_import_json(self):
        """Test JSON export and import."""
        # Create data
        project_id = self.storage.create_project("Project", "Description", "#FF0000")
        self.storage.create_task(project_id, "Task 1", "2025-12-31", "高")
        self.storage.create_task(project_id, "Task 2", "2025-12-15", "中")

        # Export
        export_path = os.path.join(self.temp_dir, "export.json")
        success = self.storage.export_to_json(export_path)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(export_path))

        # Create new storage
        new_db_path = os.path.join(self.temp_dir, "new.db")
        new_storage = Storage(new_db_path)

        # Import
        success = new_storage.import_from_json(export_path)
        self.assertTrue(success)

        # Verify
        projects = new_storage.get_all_projects()
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]["name"], "Project")

        # Clean up
        os.remove(export_path)
        os.remove(new_db_path)


if __name__ == "__main__":
    unittest.main()
