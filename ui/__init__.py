"""
UI module for task management application.
"""

from ui.main_window import MainWindow
from ui.sidebar import Sidebar
from ui.kanban_board import KanbanBoard
from ui.list_view import ListView
from ui.timeline_view import TimelineView
from ui.task_card import TaskCard
from ui.dialogs import TaskDialog, ProjectDialog

__all__ = [
    "MainWindow",
    "Sidebar",
    "KanbanBoard",
    "ListView",
    "TimelineView",
    "TaskCard",
    "TaskDialog",
    "ProjectDialog",
]
