"""
List view widget for displaying tasks in a table format.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor


class ListView(QWidget):
    """List view widget showing tasks in table format."""

    task_clicked = pyqtSignal(dict)
    task_deleted = pyqtSignal(int)
    task_edited = pyqtSignal(dict)
    sort_changed = pyqtSignal(str)
    filter_changed = pyqtSignal(str, str)  # filter_type, value

    PRIORITY_COLORS = {
        "高": "#EF4444",
        "中": "#F59E0B",
        "低": "#10B981",
    }

    STATUS_COLORS = {
        "やること": "#6B7280",
        "進行中": "#3B82F6",
        "レビュー": "#8B5CF6",
        "完了": "#10B981",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tasks = []
        self._setup_ui()

    def _setup_ui(self):
        """Setup the list view UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Toolbar
        toolbar = QHBoxLayout()

        # Sort selector
        sort_label = QLabel("ソート:")
        sort_label.setStyleSheet("color: #9CA3AF;")
        toolbar.addWidget(sort_label)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["優先度", "期限", "ステータス", "名前"])
        self.sort_combo.setStyleSheet("""
            QComboBox {
                background: #374151;
                border: 1px solid #4B5563;
                border-radius: 4px;
                padding: 6px 12px;
                color: #E5E7EB;
                min-width: 100px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background: #1F2937;
                border: 1px solid #374151;
                color: #E5E7EB;
                selection-background-color: #374151;
            }
        """)
        self.sort_combo.currentTextChanged.connect(self._on_sort_changed)
        toolbar.addWidget(self.sort_combo)

        toolbar.addSpacing(20)

        # Status filter
        filter_label = QLabel("フィルター:")
        filter_label.setStyleSheet("color: #9CA3AF;")
        toolbar.addWidget(filter_label)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["すべて", "やること", "進行中", "レビュー", "完了"])
        self.status_filter.setStyleSheet(self.sort_combo.styleSheet())
        self.status_filter.currentTextChanged.connect(self._on_filter_changed)
        toolbar.addWidget(self.status_filter)

        toolbar.addStretch()

        layout.addLayout(toolbar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "タスク名", "期限", "優先度", "ステータス", "進捗", "担当者"
        ])
        self.table.setStyleSheet("""
            QTableWidget {
                background: #1F2937;
                border: none;
                border-radius: 8px;
                gridline-color: #374151;
                color: #E5E7EB;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #374151;
            }
            QTableWidget::item:selected {
                background: #374151;
            }
            QHeaderView::section {
                background: #111827;
                color: #9CA3AF;
                padding: 10px;
                border: none;
                border-bottom: 1px solid #374151;
                font-weight: bold;
            }
        """)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 80)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 80)
        self.table.setColumnWidth(5, 100)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.cellDoubleClicked.connect(self._on_row_double_clicked)

        layout.addWidget(self.table)

    def set_tasks(self, tasks: list):
        """Set the tasks to display."""
        self.tasks = tasks
        self._refresh_table()

    def _refresh_table(self):
        """Refresh the table with current tasks."""
        self.table.setRowCount(len(self.tasks))

        for row, task in enumerate(self.tasks):
            # Task name
            name_item = QTableWidgetItem(task["name"])
            name_item.setData(Qt.ItemDataRole.UserRole, task)
            self.table.setItem(row, 0, name_item)

            # Due date
            due_date = task.get("due_date", "-")
            date_item = QTableWidgetItem(due_date if due_date else "-")
            self.table.setItem(row, 1, date_item)

            # Priority
            priority = task.get("priority", "中")
            priority_item = QTableWidgetItem(priority)
            color = self.PRIORITY_COLORS.get(priority, "#F59E0B")
            priority_item.setForeground(QColor(color))
            self.table.setItem(row, 2, priority_item)

            # Status
            status = task.get("status", "やること")
            status_item = QTableWidgetItem(status)
            color = self.STATUS_COLORS.get(status, "#6B7280")
            status_item.setForeground(QColor(color))
            self.table.setItem(row, 3, status_item)

            # Progress
            progress = task.get("progress", 0)
            progress_item = QTableWidgetItem(f"{progress}%")
            self.table.setItem(row, 4, progress_item)

            # Assignee
            assignee = task.get("assignee", "-")
            assignee_item = QTableWidgetItem(assignee if assignee else "-")
            self.table.setItem(row, 5, assignee_item)

    def _on_sort_changed(self, text: str):
        """Handle sort change."""
        sort_map = {
            "優先度": "priority",
            "期限": "due_date",
            "ステータス": "status",
            "名前": "name"
        }
        self.sort_changed.emit(sort_map.get(text, "priority"))

    def _on_filter_changed(self, text: str):
        """Handle filter change."""
        if text == "すべて":
            self.filter_changed.emit("status", "")
        else:
            self.filter_changed.emit("status", text)

    def _on_row_double_clicked(self, row: int, column: int):
        """Handle row double-click."""
        item = self.table.item(row, 0)
        if item:
            task = item.data(Qt.ItemDataRole.UserRole)
            if task:
                self.task_edited.emit(task)
