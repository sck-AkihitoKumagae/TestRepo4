"""
Sidebar widget for project navigation.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class ProjectItem(QFrame):
    """Widget representing a single project in the sidebar."""

    clicked = pyqtSignal(int)

    def __init__(self, project: dict, parent=None):
        super().__init__(parent)
        self.project = project
        self.is_selected = False
        self._setup_ui()

    def _setup_ui(self):
        """Setup the project item UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        # Color indicator
        color = self.project.get("color", "#3B82F6")
        color_indicator = QLabel()
        color_indicator.setFixedSize(12, 12)
        color_indicator.setStyleSheet(f"""
            background: {color};
            border-radius: 2px;
        """)
        layout.addWidget(color_indicator)

        # Project name
        name_label = QLabel(self.project["name"])
        name_label.setFont(QFont("Segoe UI", 10))
        name_label.setStyleSheet("color: #E5E7EB;")
        layout.addWidget(name_label, 1)

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_style()

    def _update_style(self):
        """Update style based on selection state."""
        if self.is_selected:
            self.setStyleSheet("""
                ProjectItem {
                    background: #374151;
                    border-radius: 6px;
                    border-left: 3px solid #3B82F6;
                }
            """)
        else:
            self.setStyleSheet("""
                ProjectItem {
                    background: transparent;
                    border-radius: 6px;
                }
                ProjectItem:hover {
                    background: #374151;
                }
            """)

    def set_selected(self, selected: bool):
        """Set selection state."""
        self.is_selected = selected
        self._update_style()

    def mousePressEvent(self, event):
        """Handle mouse press."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.project["id"])
        super().mousePressEvent(event)


class Sidebar(QWidget):
    """Sidebar widget for project navigation."""

    project_selected = pyqtSignal(int)
    project_add_requested = pyqtSignal()
    search_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_items = {}
        self.selected_project_id = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup the sidebar UI."""
        self.setFixedWidth(220)
        self.setStyleSheet("background: #111827;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setStyleSheet("background: #111827;")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(16, 16, 16, 8)

        # My Tasks label
        my_tasks = QHBoxLayout()
        tasks_icon = QLabel("☐")
        tasks_icon.setStyleSheet("color: #9CA3AF; font-size: 14px;")
        my_tasks.addWidget(tasks_icon)

        tasks_label = QLabel("マイタスク")
        tasks_label.setFont(QFont("Segoe UI", 11))
        tasks_label.setStyleSheet("color: #E5E7EB;")
        my_tasks.addWidget(tasks_label)
        my_tasks.addStretch()

        header_layout.addLayout(my_tasks)

        # Projects section header
        projects_header = QHBoxLayout()
        projects_label = QLabel("プロジェクト")
        projects_label.setFont(QFont("Segoe UI", 10))
        projects_label.setStyleSheet("color: #6B7280;")
        projects_header.addWidget(projects_label)
        projects_header.addStretch()

        header_layout.addSpacing(16)
        header_layout.addLayout(projects_header)

        # Search box
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 検索")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: #1F2937;
                border: 1px solid #374151;
                border-radius: 6px;
                padding: 8px 12px;
                color: #E5E7EB;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #3B82F6;
            }
        """)
        self.search_input.textChanged.connect(self.search_changed.emit)
        search_layout.addWidget(self.search_input)

        # Add project button
        self.add_btn = QPushButton("+")
        self.add_btn.setFixedSize(32, 32)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background: #3B82F6;
                border: none;
                border-radius: 6px;
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2563EB;
            }
        """)
        self.add_btn.clicked.connect(self.project_add_requested.emit)
        search_layout.addWidget(self.add_btn)

        header_layout.addSpacing(8)
        header_layout.addLayout(search_layout)

        layout.addWidget(header)

        # Scroll area for projects
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #1F2937;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #374151;
                border-radius: 4px;
            }
        """)

        self.projects_container = QWidget()
        self.projects_layout = QVBoxLayout(self.projects_container)
        self.projects_layout.setContentsMargins(8, 8, 8, 8)
        self.projects_layout.setSpacing(4)
        self.projects_layout.addStretch()

        scroll.setWidget(self.projects_container)
        layout.addWidget(scroll, 1)

    def set_projects(self, projects: list):
        """Set the list of projects."""
        # Clear existing items
        for item in self.project_items.values():
            item.deleteLater()
        self.project_items.clear()

        # Add new items
        for project in projects:
            item = ProjectItem(project)
            item.clicked.connect(self._on_project_clicked)
            self.project_items[project["id"]] = item

            # Insert before stretch
            self.projects_layout.insertWidget(
                self.projects_layout.count() - 1, item
            )

        # Restore selection
        if self.selected_project_id in self.project_items:
            self.project_items[self.selected_project_id].set_selected(True)

    def _on_project_clicked(self, project_id: int):
        """Handle project click."""
        # Update selection
        if self.selected_project_id in self.project_items:
            self.project_items[self.selected_project_id].set_selected(False)

        self.selected_project_id = project_id
        if project_id in self.project_items:
            self.project_items[project_id].set_selected(True)

        self.project_selected.emit(project_id)

    def select_project(self, project_id: int):
        """Programmatically select a project."""
        self._on_project_clicked(project_id)
