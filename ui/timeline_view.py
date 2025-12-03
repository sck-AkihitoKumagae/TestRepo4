"""
Timeline (Gantt chart) view widget for task visualization.
"""

from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QGraphicsView, QGraphicsScene, QGraphicsRectItem,
    QGraphicsTextItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QFont, QColor, QBrush, QPen


class TimelineView(QWidget):
    """Timeline (Gantt chart) view for tasks."""

    task_clicked = pyqtSignal(dict)

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
        """Setup the timeline view UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        header = QHBoxLayout()
        title = QLabel("タイムライン")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #E5E7EB;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # Graphics view for Gantt chart
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setStyleSheet("""
            QGraphicsView {
                background: #1F2937;
                border: none;
                border-radius: 8px;
            }
        """)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        layout.addWidget(self.view)

    def set_tasks(self, tasks: list):
        """Set tasks and render the timeline."""
        self.tasks = [t for t in tasks if t.get("due_date")]
        self._render_timeline()

    def _render_timeline(self):
        """Render the Gantt chart."""
        self.scene.clear()

        if not self.tasks:
            # Show empty message
            text = self.scene.addText("タスクがありません")
            text.setDefaultTextColor(QColor("#6B7280"))
            text.setFont(QFont("Segoe UI", 12))
            return

        # Configuration
        row_height = 40
        day_width = 30
        header_height = 30
        left_margin = 150

        # Calculate date range
        dates = []
        for task in self.tasks:
            try:
                date = datetime.strptime(task["due_date"], "%Y-%m-%d")
                dates.append(date)
            except (ValueError, TypeError):
                pass

        if not dates:
            return

        min_date = min(dates) - timedelta(days=7)
        max_date = max(dates) + timedelta(days=7)
        total_days = (max_date - min_date).days + 1

        # Draw header (dates)
        for i in range(total_days):
            date = min_date + timedelta(days=i)
            x = left_margin + i * day_width

            # Date label
            text = self.scene.addText(date.strftime("%m/%d"))
            text.setPos(x, 0)
            text.setDefaultTextColor(QColor("#6B7280"))
            text.setFont(QFont("Segoe UI", 8))

            # Vertical grid line
            line = self.scene.addLine(
                x, header_height,
                x, header_height + len(self.tasks) * row_height,
                QPen(QColor("#374151"))
            )

        # Draw tasks
        for row, task in enumerate(self.tasks):
            y = header_height + row * row_height

            # Task name
            name_text = self.scene.addText(task["name"][:15])
            name_text.setPos(5, y + 5)
            name_text.setDefaultTextColor(QColor("#E5E7EB"))
            name_text.setFont(QFont("Segoe UI", 10))

            # Horizontal grid line
            self.scene.addLine(
                0, y + row_height,
                left_margin + total_days * day_width, y + row_height,
                QPen(QColor("#374151"))
            )

            # Task bar
            try:
                due_date = datetime.strptime(task["due_date"], "%Y-%m-%d")
                days_from_start = (due_date - min_date).days

                # Assume task duration of 3 days for visualization
                bar_x = left_margin + (days_from_start - 3) * day_width
                bar_width = 4 * day_width

                status = task.get("status", "やること")
                color = self.STATUS_COLORS.get(status, "#6B7280")

                bar = QGraphicsRectItem(bar_x, y + 8, bar_width, 24)
                bar.setBrush(QBrush(QColor(color)))
                bar.setPen(QPen(Qt.PenStyle.NoPen))
                self.scene.addItem(bar)

            except (ValueError, TypeError):
                pass

        # Set scene rect
        self.scene.setSceneRect(
            0, 0,
            left_margin + total_days * day_width + 50,
            header_height + len(self.tasks) * row_height + 20
        )
