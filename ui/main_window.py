"""
Main window for the task management application.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QLineEdit, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon

from task_manager import TaskManager
from ui.sidebar import Sidebar
from ui.kanban_board import KanbanBoard
from ui.list_view import ListView
from ui.timeline_view import TimelineView
from ui.dialogs import TaskDialog, ProjectDialog


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.task_manager = TaskManager()
        self.current_project_id = None
        self.current_view = "board"
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Setup the main window UI."""
        self.setWindowTitle("タスク管理")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet("background: #111827;")

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.project_selected.connect(self._on_project_selected)
        self.sidebar.project_add_requested.connect(self._show_add_project_dialog)
        self.sidebar.search_changed.connect(self._on_search_changed)
        main_layout.addWidget(self.sidebar)

        # Content area
        content = QWidget()
        content.setStyleSheet("background: #1F2937;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Header
        header = self._create_header()
        content_layout.addWidget(header)

        # Navigation bar
        navbar = self._create_navbar()
        content_layout.addWidget(navbar)

        # View stack
        self.view_stack = QStackedWidget()

        # Kanban board view
        self.kanban_board = KanbanBoard()
        self.kanban_board.task_add_requested.connect(self._show_add_task_dialog)
        self.kanban_board.task_clicked.connect(self._on_task_clicked)
        self.kanban_board.task_deleted.connect(self._delete_task)
        self.kanban_board.task_edited.connect(self._show_edit_task_dialog)
        self.kanban_board.task_status_changed.connect(self._on_task_status_changed)
        self.view_stack.addWidget(self.kanban_board)

        # List view
        self.list_view = ListView()
        self.list_view.task_edited.connect(self._show_edit_task_dialog)
        self.list_view.task_deleted.connect(self._delete_task)
        self.list_view.sort_changed.connect(self._on_sort_changed)
        self.list_view.filter_changed.connect(self._on_filter_changed)
        self.view_stack.addWidget(self.list_view)

        # Timeline view
        self.timeline_view = TimelineView()
        self.timeline_view.task_clicked.connect(self._on_task_clicked)
        self.view_stack.addWidget(self.timeline_view)

        content_layout.addWidget(self.view_stack, 1)

        main_layout.addWidget(content, 1)

    def _create_header(self) -> QWidget:
        """Create the header section."""
        header = QWidget()
        header.setStyleSheet("background: #1F2937;")
        header.setFixedHeight(100)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 20, 24, 10)

        # Project info
        info_layout = QVBoxLayout()

        # Project name with icon
        name_layout = QHBoxLayout()

        project_icon = QLabel("📋")
        project_icon.setStyleSheet("""
            background: #374151;
            padding: 8px;
            border-radius: 6px;
            font-size: 18px;
        """)
        name_layout.addWidget(project_icon)

        self.project_name_label = QLabel("プロジェクトを選択してください")
        self.project_name_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.project_name_label.setStyleSheet("color: #FFFFFF;")
        name_layout.addWidget(self.project_name_label)
        name_layout.addStretch()

        info_layout.addLayout(name_layout)

        # Description
        self.project_desc_label = QLabel("")
        self.project_desc_label.setStyleSheet("color: #9CA3AF; font-size: 12px;")
        info_layout.addWidget(self.project_desc_label)

        layout.addLayout(info_layout, 1)

        # Team members (placeholder)
        members_layout = QHBoxLayout()
        members_layout.setSpacing(-8)

        for i in range(3):
            avatar = QLabel("👤")
            avatar.setFixedSize(32, 32)
            avatar.setStyleSheet(f"""
                background: {'#F59E0B' if i == 0 else '#3B82F6' if i == 1 else '#10B981'};
                border-radius: 16px;
                border: 2px solid #1F2937;
                font-size: 12px;
            """)
            avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            members_layout.addWidget(avatar)

        layout.addLayout(members_layout)

        # Share button
        share_btn = QPushButton("🔗 共有する")
        share_btn.setStyleSheet("""
            QPushButton {
                background: #3B82F6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #2563EB;
            }
        """)
        layout.addWidget(share_btn)

        return header

    def _create_navbar(self) -> QWidget:
        """Create the navigation bar."""
        navbar = QWidget()
        navbar.setStyleSheet("background: #1F2937;")
        navbar.setFixedHeight(50)

        layout = QHBoxLayout(navbar)
        layout.setContentsMargins(24, 0, 24, 0)

        # Add task button
        add_task_btn = QPushButton("+ タスクを追加")
        add_task_btn.setStyleSheet("""
            QPushButton {
                background: #10B981;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #059669;
            }
        """)
        add_task_btn.clicked.connect(lambda: self._show_add_task_dialog("やること"))
        layout.addWidget(add_task_btn)

        layout.addSpacing(16)

        # View toggle buttons
        self.view_buttons = {}

        list_btn = QPushButton("📋 リスト")
        list_btn.clicked.connect(lambda: self._switch_view("list"))
        self.view_buttons["list"] = list_btn
        layout.addWidget(list_btn)

        board_btn = QPushButton("📊 ボード")
        board_btn.clicked.connect(lambda: self._switch_view("board"))
        self.view_buttons["board"] = board_btn
        layout.addWidget(board_btn)

        timeline_btn = QPushButton("📅 タイムライン")
        timeline_btn.clicked.connect(lambda: self._switch_view("timeline"))
        self.view_buttons["timeline"] = timeline_btn
        layout.addWidget(timeline_btn)

        self._update_view_buttons()

        layout.addStretch()

        # Search
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("color: #6B7280;")
        layout.addWidget(search_icon)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("検索")
        self.search_input.setFixedWidth(150)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: #374151;
                border: 1px solid #4B5563;
                border-radius: 6px;
                padding: 6px 12px;
                color: #E5E7EB;
            }
            QLineEdit:focus {
                border: 1px solid #3B82F6;
            }
        """)
        self.search_input.textChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_input)

        layout.addSpacing(8)

        # Filter button
        filter_btn = QPushButton("🔽 フィルター")
        filter_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #9CA3AF;
                border: none;
                padding: 8px;
            }
            QPushButton:hover {
                color: #FFFFFF;
            }
        """)
        layout.addWidget(filter_btn)

        # Sort button
        sort_btn = QPushButton("↕️ ソート")
        sort_btn.setStyleSheet(filter_btn.styleSheet())
        layout.addWidget(sort_btn)

        return navbar

    def _update_view_buttons(self):
        """Update view button styles."""
        for view, btn in self.view_buttons.items():
            if view == self.current_view:
                btn.setStyleSheet("""
                    QPushButton {
                        background: #374151;
                        color: #FFFFFF;
                        border: none;
                        border-radius: 6px;
                        padding: 8px 12px;
                        font-size: 12px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background: transparent;
                        color: #9CA3AF;
                        border: none;
                        border-radius: 6px;
                        padding: 8px 12px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background: #374151;
                        color: #FFFFFF;
                    }
                """)

    def _switch_view(self, view: str):
        """Switch between view modes."""
        self.current_view = view
        self._update_view_buttons()

        view_map = {"board": 0, "list": 1, "timeline": 2}
        self.view_stack.setCurrentIndex(view_map.get(view, 0))

    def _load_data(self):
        """Load projects and tasks."""
        projects = self.task_manager.get_all_projects()
        self.sidebar.set_projects(projects)

        # Select first project if available
        if projects and not self.current_project_id:
            self._on_project_selected(projects[0]["id"])

    def _refresh_tasks(self):
        """Refresh tasks for current project."""
        if not self.current_project_id:
            return

        tasks = self.task_manager.get_tasks_by_project(self.current_project_id)

        # Update all views
        self.kanban_board.set_tasks(tasks)
        self.list_view.set_tasks(tasks)
        self.timeline_view.set_tasks(tasks)

    def _on_project_selected(self, project_id: int):
        """Handle project selection."""
        self.current_project_id = project_id
        project = self.task_manager.get_project(project_id)

        if project:
            self.project_name_label.setText(project["name"])
            self.project_desc_label.setText(project.get("description", ""))

        self._refresh_tasks()

    def _show_add_project_dialog(self):
        """Show dialog to add a new project."""
        dialog = ProjectDialog(parent=self)
        if dialog.exec() == ProjectDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data:
                project_id = self.task_manager.create_project(
                    data["name"], data.get("description", ""), data.get("color")
                )
                self._load_data()
                self._on_project_selected(project_id)

    def _show_add_task_dialog(self, status: str = "やること"):
        """Show dialog to add a new task."""
        if not self.current_project_id:
            QMessageBox.warning(self, "警告", "先にプロジェクトを選択してください。")
            return

        dialog = TaskDialog({"status": status}, parent=self)
        if dialog.exec() == TaskDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data:
                self.task_manager.create_task(
                    self.current_project_id,
                    data["name"],
                    data.get("due_date"),
                    data.get("priority", "中"),
                    data.get("status", "やること"),
                    data.get("progress", 0),
                    data.get("assignee")
                )
                self._refresh_tasks()

    def _show_edit_task_dialog(self, task: dict):
        """Show dialog to edit a task."""
        dialog = TaskDialog(task, parent=self)
        if dialog.exec() == TaskDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data and "id" in data:
                task_id = data.pop("id")
                self.task_manager.update_task(task_id, **data)
                self._refresh_tasks()

    def _on_task_clicked(self, task: dict):
        """Handle task click."""
        self._show_edit_task_dialog(task)

    def _delete_task(self, task_id: int):
        """Delete a task."""
        reply = QMessageBox.question(
            self, "確認",
            "このタスクを削除しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.task_manager.delete_task(task_id)
            self._refresh_tasks()

    def _on_task_status_changed(self, task_id: int, new_status: str):
        """Handle task status change (drag-and-drop)."""
        self.task_manager.update_task_status(task_id, new_status)
        self._refresh_tasks()

    def _on_search_changed(self, text: str):
        """Handle search input change."""
        if not self.current_project_id:
            return

        if text:
            tasks = self.task_manager.search_tasks(self.current_project_id, keyword=text)
        else:
            tasks = self.task_manager.get_tasks_by_project(self.current_project_id)

        self.kanban_board.set_tasks(tasks)
        self.list_view.set_tasks(tasks)
        self.timeline_view.set_tasks(tasks)

    def _on_sort_changed(self, sort_by: str):
        """Handle sort change."""
        if not self.current_project_id:
            return

        tasks = self.task_manager.get_tasks_sorted(self.current_project_id, sort_by)
        self.list_view.set_tasks(tasks)

    def _on_filter_changed(self, filter_type: str, value: str):
        """Handle filter change."""
        if not self.current_project_id:
            return

        if value:
            tasks = self.task_manager.search_tasks(
                self.current_project_id,
                **{filter_type: value}
            )
        else:
            tasks = self.task_manager.get_tasks_by_project(self.current_project_id)

        self.list_view.set_tasks(tasks)

    def closeEvent(self, event):
        """Handle window close - auto backup."""
        self.task_manager.export_backup()
        event.accept()
