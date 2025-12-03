"""
Dialog widgets for creating and editing tasks and projects.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QDateEdit, QSpinBox, QTextEdit,
    QFormLayout, QFrame, QColorDialog
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont


class TaskDialog(QDialog):
    """Dialog for creating or editing a task."""

    STATUSES = ["やること", "進行中", "レビュー", "完了"]
    PRIORITIES = ["低", "中", "高"]

    def __init__(self, task: dict = None, parent=None):
        super().__init__(parent)
        self.task = task or {}
        self.result_data = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle("タスクを編集" if self.task.get("id") else "タスクを追加")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog {
                background: #1F2937;
            }
            QLabel {
                color: #E5E7EB;
            }
            QLineEdit, QTextEdit, QComboBox, QDateEdit, QSpinBox {
                background: #374151;
                border: 1px solid #4B5563;
                border-radius: 6px;
                padding: 8px;
                color: #E5E7EB;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus,
            QDateEdit:focus, QSpinBox:focus {
                border: 1px solid #3B82F6;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Title
        title = QLabel("タスクを編集" if self.task.get("id") else "新しいタスク")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        # Form
        form = QFormLayout()
        form.setSpacing(12)

        # Task name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("タスク名を入力")
        self.name_input.setText(self.task.get("name", ""))
        form.addRow("タスク名:", self.name_input)

        # Due date
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        if self.task.get("due_date"):
            try:
                parts = self.task["due_date"].split("-")
                self.date_input.setDate(QDate(int(parts[0]), int(parts[1]), int(parts[2])))
            except (ValueError, IndexError):
                self.date_input.setDate(QDate.currentDate())
        else:
            self.date_input.setDate(QDate.currentDate())
        form.addRow("期限:", self.date_input)

        # Priority
        self.priority_input = QComboBox()
        self.priority_input.addItems(self.PRIORITIES)
        current_priority = self.task.get("priority", "中")
        if current_priority in self.PRIORITIES:
            self.priority_input.setCurrentText(current_priority)
        form.addRow("優先度:", self.priority_input)

        # Status
        self.status_input = QComboBox()
        self.status_input.addItems(self.STATUSES)
        current_status = self.task.get("status", "やること")
        if current_status in self.STATUSES:
            self.status_input.setCurrentText(current_status)
        form.addRow("ステータス:", self.status_input)

        # Progress
        self.progress_input = QSpinBox()
        self.progress_input.setRange(0, 100)
        self.progress_input.setSuffix("%")
        self.progress_input.setValue(self.task.get("progress", 0))
        form.addRow("進捗:", self.progress_input)

        # Assignee
        self.assignee_input = QLineEdit()
        self.assignee_input.setPlaceholderText("担当者名")
        self.assignee_input.setText(self.task.get("assignee", "") or "")
        form.addRow("担当者:", self.assignee_input)

        layout.addLayout(form)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("キャンセル")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #374151;
                color: #E5E7EB;
                border: none;
            }
            QPushButton:hover {
                background: #4B5563;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("保存")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #3B82F6;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background: #2563EB;
            }
        """)
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _save(self):
        """Save and close dialog."""
        name = self.name_input.text().strip()
        if not name:
            self.name_input.setFocus()
            return

        self.result_data = {
            "name": name,
            "due_date": self.date_input.date().toString("yyyy-MM-dd"),
            "priority": self.priority_input.currentText(),
            "status": self.status_input.currentText(),
            "progress": self.progress_input.value(),
            "assignee": self.assignee_input.text().strip() or None
        }

        if self.task.get("id"):
            self.result_data["id"] = self.task["id"]

        self.accept()

    def get_data(self) -> dict:
        """Get the entered data."""
        return self.result_data


class ProjectDialog(QDialog):
    """Dialog for creating or editing a project."""

    DEFAULT_COLORS = [
        "#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"
    ]

    def __init__(self, project: dict = None, parent=None):
        super().__init__(parent)
        self.project = project or {}
        self.result_data = None
        self.selected_color = self.project.get("color", self.DEFAULT_COLORS[0])
        self._setup_ui()

    def _setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle("プロジェクトを編集" if self.project.get("id") else "プロジェクトを追加")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog {
                background: #1F2937;
            }
            QLabel {
                color: #E5E7EB;
            }
            QLineEdit, QTextEdit {
                background: #374151;
                border: 1px solid #4B5563;
                border-radius: 6px;
                padding: 8px;
                color: #E5E7EB;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #3B82F6;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Title
        title = QLabel("プロジェクトを編集" if self.project.get("id") else "新しいプロジェクト")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        # Form
        form = QFormLayout()
        form.setSpacing(12)

        # Project name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("プロジェクト名を入力")
        self.name_input.setText(self.project.get("name", ""))
        form.addRow("プロジェクト名:", self.name_input)

        # Description
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("説明（オプション）")
        self.desc_input.setMaximumHeight(100)
        self.desc_input.setPlainText(self.project.get("description", ""))
        form.addRow("説明:", self.desc_input)

        # Color
        color_layout = QHBoxLayout()

        for color in self.DEFAULT_COLORS:
            color_btn = QPushButton()
            color_btn.setFixedSize(32, 32)
            color_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {color};
                    border: 2px solid {'#FFFFFF' if color == self.selected_color else 'transparent'};
                    border-radius: 16px;
                }}
                QPushButton:hover {{
                    border: 2px solid #FFFFFF;
                }}
            """)
            color_btn.clicked.connect(lambda checked, c=color: self._select_color(c))
            color_layout.addWidget(color_btn)

        custom_color_btn = QPushButton("+")
        custom_color_btn.setFixedSize(32, 32)
        custom_color_btn.setStyleSheet("""
            QPushButton {
                background: #374151;
                border: 2px dashed #6B7280;
                border-radius: 16px;
                color: #6B7280;
            }
            QPushButton:hover {
                border-color: #FFFFFF;
                color: #FFFFFF;
            }
        """)
        custom_color_btn.clicked.connect(self._choose_custom_color)
        color_layout.addWidget(custom_color_btn)

        color_layout.addStretch()
        form.addRow("カラー:", color_layout)

        layout.addLayout(form)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("キャンセル")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #374151;
                color: #E5E7EB;
                border: none;
            }
            QPushButton:hover {
                background: #4B5563;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("保存")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #3B82F6;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background: #2563EB;
            }
        """)
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _select_color(self, color: str):
        """Select a color."""
        self.selected_color = color
        # Re-setup UI to update button styles would be needed for visual feedback

    def _choose_custom_color(self):
        """Open color picker for custom color."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = color.name()

    def _save(self):
        """Save and close dialog."""
        name = self.name_input.text().strip()
        if not name:
            self.name_input.setFocus()
            return

        self.result_data = {
            "name": name,
            "description": self.desc_input.toPlainText().strip(),
            "color": self.selected_color
        }

        if self.project.get("id"):
            self.result_data["id"] = self.project["id"]

        self.accept()

    def get_data(self) -> dict:
        """Get the entered data."""
        return self.result_data
