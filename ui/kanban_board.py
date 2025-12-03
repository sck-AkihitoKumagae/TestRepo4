"""
Kanban board widget for task visualization.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ui.task_card import TaskCard


class KanbanColumn(QFrame):
    """Widget representing a single column in the Kanban board."""

    task_add_requested = pyqtSignal(str)  # status
    task_clicked = pyqtSignal(dict)
    task_deleted = pyqtSignal(int)
    task_edited = pyqtSignal(dict)
    task_dropped = pyqtSignal(int, str)  # task_id, new_status

    def __init__(self, title: str, status: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.status = status
        self.task_cards = []
        self._setup_ui()
        self.setAcceptDrops(True)

    def _setup_ui(self):
        """Setup the column UI."""
        self.setMinimumWidth(280)
        self.setMaximumWidth(320)
        self.setStyleSheet("""
            KanbanColumn {
                background: #1F2937;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Header
        header = QHBoxLayout()

        title_label = QLabel(self.title)
        title_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #E5E7EB;")
        header.addWidget(title_label)

        # Task count
        self.count_label = QLabel("0")
        self.count_label.setStyleSheet("""
            color: #9CA3AF;
            font-size: 11px;
            padding: 2px 6px;
        """)
        header.addWidget(self.count_label)

        header.addStretch()

        # Menu button
        menu_btn = QPushButton("⋯")
        menu_btn.setFixedSize(24, 24)
        menu_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #6B7280;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #FFFFFF;
            }
        """)
        header.addWidget(menu_btn)

        layout.addLayout(header)

        # Scroll area for tasks
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #374151;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #4B5563;
                border-radius: 3px;
            }
        """)

        self.tasks_container = QWidget()
        self.tasks_container.setStyleSheet("background: transparent;")
        self.tasks_layout = QVBoxLayout(self.tasks_container)
        self.tasks_layout.setContentsMargins(0, 0, 0, 0)
        self.tasks_layout.setSpacing(8)
        self.tasks_layout.addStretch()

        scroll.setWidget(self.tasks_container)
        layout.addWidget(scroll, 1)

        # Add task button
        add_btn = QPushButton("+ タスクを追加")
        add_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #6B7280;
                font-size: 12px;
                padding: 8px;
                text-align: left;
            }
            QPushButton:hover {
                color: #FFFFFF;
            }
        """)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(lambda: self.task_add_requested.emit(self.status))
        layout.addWidget(add_btn)

    def set_tasks(self, tasks: list):
        """Set the tasks for this column."""
        # Clear existing cards
        for card in self.task_cards:
            card.deleteLater()
        self.task_cards.clear()

        # Add new cards
        for task in tasks:
            card = TaskCard(task)
            card.task_clicked.connect(self.task_clicked.emit)
            card.task_deleted.connect(self.task_deleted.emit)
            card.task_edited.connect(self.task_edited.emit)
            self.task_cards.append(card)

            # Insert before stretch
            self.tasks_layout.insertWidget(
                self.tasks_layout.count() - 1, card
            )

        # Update count
        self.count_label.setText(str(len(tasks)))

    def dragEnterEvent(self, event):
        """Handle drag enter."""
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Handle drop."""
        task_id = int(event.mimeData().text())
        self.task_dropped.emit(task_id, self.status)
        event.acceptProposedAction()


class KanbanBoard(QWidget):
    """Kanban board widget with multiple columns."""

    task_add_requested = pyqtSignal(str)  # status
    task_clicked = pyqtSignal(dict)
    task_deleted = pyqtSignal(int)
    task_edited = pyqtSignal(dict)
    task_status_changed = pyqtSignal(int, str)  # task_id, new_status

    COLUMNS = [
        ("やること", "やること"),
        ("進行中", "進行中"),
        ("レビュー", "レビュー"),
        ("完了", "完了"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.columns = {}
        self._setup_ui()

    def _setup_ui(self):
        """Setup the board UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        for title, status in self.COLUMNS:
            column = KanbanColumn(title, status)
            column.task_add_requested.connect(self.task_add_requested.emit)
            column.task_clicked.connect(self.task_clicked.emit)
            column.task_deleted.connect(self.task_deleted.emit)
            column.task_edited.connect(self.task_edited.emit)
            column.task_dropped.connect(self.task_status_changed.emit)
            self.columns[status] = column
            layout.addWidget(column)

        layout.addStretch()

    def set_tasks(self, tasks: list):
        """Distribute tasks to columns by status."""
        for status, column in self.columns.items():
            status_tasks = [t for t in tasks if t["status"] == status]
            column.set_tasks(status_tasks)

    def refresh_column(self, status: str, tasks: list):
        """Refresh a specific column with new tasks."""
        if status in self.columns:
            self.columns[status].set_tasks(tasks)
