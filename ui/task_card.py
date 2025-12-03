"""
Task card widget for displaying individual tasks.
"""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QAction


class TaskCard(QFrame):
    """Widget representing a single task card in the Kanban board."""

    task_clicked = pyqtSignal(dict)
    task_deleted = pyqtSignal(int)
    task_edited = pyqtSignal(dict)

    PRIORITY_COLORS = {
        "高": "#EF4444",  # Red
        "中": "#F59E0B",  # Amber
        "低": "#10B981",  # Green
    }

    def __init__(self, task: dict, parent=None):
        super().__init__(parent)
        self.task = task
        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self):
        """Setup the card UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        # Header with task name and menu
        header = QHBoxLayout()

        # Task checkbox and name
        name_layout = QHBoxLayout()
        name_layout.setSpacing(8)

        checkbox = QLabel("○")
        checkbox.setStyleSheet("color: #9CA3AF; font-size: 14px;")
        name_layout.addWidget(checkbox)

        self.name_label = QLabel(self.task["name"])
        self.name_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.name_label.setWordWrap(True)
        self.name_label.setStyleSheet("color: #FFFFFF;")
        name_layout.addWidget(self.name_label, 1)

        header.addLayout(name_layout, 1)

        # Menu button
        self.menu_btn = QPushButton("⋯")
        self.menu_btn.setFixedSize(24, 24)
        self.menu_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #6B7280;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #FFFFFF;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
            }
        """)
        self.menu_btn.clicked.connect(self._show_menu)
        header.addWidget(self.menu_btn)

        layout.addLayout(header)

        # Due date row
        if self.task.get("due_date"):
            date_layout = QHBoxLayout()
            date_layout.setSpacing(6)

            # Priority indicator
            priority = self.task.get("priority", "中")
            priority_color = self.PRIORITY_COLORS.get(priority, "#F59E0B")

            assignee_icon = QLabel("👤")
            assignee_icon.setStyleSheet(f"""
                background: {priority_color};
                border-radius: 10px;
                padding: 2px 6px;
                font-size: 10px;
            """)
            date_layout.addWidget(assignee_icon)

            # Date label
            date_label = QLabel(self.task["due_date"])
            date_label.setStyleSheet(f"""
                background: {priority_color};
                color: white;
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 11px;
            """)
            date_layout.addWidget(date_label)

            date_layout.addStretch()

            # Comment count indicator (placeholder)
            comment_label = QLabel("💬 0")
            comment_label.setStyleSheet("color: #6B7280; font-size: 11px;")
            date_layout.addWidget(comment_label)

            layout.addLayout(date_layout)

        # Progress bar (if progress > 0)
        if self.task.get("progress", 0) > 0:
            progress_layout = QHBoxLayout()
            progress_label = QLabel(f"進捗: {self.task['progress']}%")
            progress_label.setStyleSheet("color: #9CA3AF; font-size: 10px;")
            progress_layout.addWidget(progress_label)
            layout.addLayout(progress_layout)

        # Make card clickable
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def _apply_styles(self):
        """Apply card styles."""
        self.setStyleSheet("""
            TaskCard {
                background: #374151;
                border-radius: 8px;
                border: 1px solid #4B5563;
            }
            TaskCard:hover {
                border: 1px solid #6B7280;
            }
        """)
        self.setMinimumHeight(80)

    def _show_menu(self):
        """Show context menu."""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: #1F2937;
                border: 1px solid #374151;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                color: #E5E7EB;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background: #374151;
            }
        """)

        edit_action = QAction("編集", self)
        edit_action.triggered.connect(lambda: self.task_edited.emit(self.task))
        menu.addAction(edit_action)

        delete_action = QAction("削除", self)
        delete_action.triggered.connect(lambda: self.task_deleted.emit(self.task["id"]))
        menu.addAction(delete_action)

        menu.exec(self.menu_btn.mapToGlobal(self.menu_btn.rect().bottomLeft()))

    def mousePressEvent(self, event):
        """Handle mouse press for drag start."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.task_clicked.emit(self.task)
        super().mousePressEvent(event)

    def get_task_id(self) -> int:
        """Get the task ID."""
        return self.task["id"]

    def update_task(self, task: dict):
        """Update the task data and refresh display."""
        self.task = task
        self.name_label.setText(task["name"])
