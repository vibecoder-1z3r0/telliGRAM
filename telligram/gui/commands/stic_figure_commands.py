"""
Undo/redo commands for STIC Figure operations.

Provides QUndoCommand implementations for all STIC Figure editing operations.
"""

from PySide6.QtGui import QUndoCommand
from telligram.core.stic_figure import SticFigure


class CreateSticFigureCommand(QUndoCommand):
    """Command for creating a new STIC figure"""

    def __init__(self, main_window, figure_name):
        super().__init__(f"Create Figure '{figure_name}'")
        self.main_window = main_window
        self.figure_name = figure_name
        self.figure = None

    def redo(self):
        """Create the figure"""
        self.figure = SticFigure(name=self.figure_name)
        self.main_window.project.add_stic_figure(self.figure)
        self.main_window.stic_figures._refresh_figure_list()
        # Select the newly created figure
        index = len(self.main_window.project.stic_figures) - 1
        self.main_window.stic_figures.figure_combo.setCurrentIndex(index)

    def undo(self):
        """Remove the figure"""
        if self.figure in self.main_window.project.stic_figures:
            self.main_window.project.stic_figures.remove(self.figure)
        self.main_window.stic_figures._refresh_figure_list()
        # Select another figure or none
        if len(self.main_window.project.stic_figures) > 0:
            self.main_window.stic_figures.figure_combo.setCurrentIndex(0)


class RenameSticFigureCommand(QUndoCommand):
    """Command for renaming a STIC figure"""

    def __init__(self, main_window, figure, old_name, new_name):
        super().__init__(f"Rename Figure '{old_name}' to '{new_name}'")
        self.main_window = main_window
        self.figure = figure
        self.old_name = old_name
        self.new_name = new_name

    def redo(self):
        """Apply new name"""
        self.figure.name = self.new_name
        self.main_window.stic_figures._refresh_figure_list()

    def undo(self):
        """Restore old name"""
        self.figure.name = self.old_name
        self.main_window.stic_figures._refresh_figure_list()


class DeleteSticFigureCommand(QUndoCommand):
    """Command for deleting a STIC figure"""

    def __init__(self, main_window, figure, figure_index):
        super().__init__(f"Delete Figure '{figure.name}'")
        self.main_window = main_window
        self.figure = figure
        self.figure_index = figure_index
        # Store full figure state
        self.figure_data = figure.to_dict()

    def redo(self):
        """Delete the figure"""
        if self.figure in self.main_window.project.stic_figures:
            self.main_window.project.stic_figures.remove(self.figure)
        self.main_window.stic_figures._refresh_figure_list()
        # Select another figure or none
        if len(self.main_window.project.stic_figures) > 0:
            index = min(self.figure_index, len(self.main_window.project.stic_figures) - 1)
            self.main_window.stic_figures.figure_combo.setCurrentIndex(index)

    def undo(self):
        """Restore the figure"""
        restored_figure = SticFigure.from_dict(self.figure_data)
        self.main_window.project.stic_figures.insert(self.figure_index, restored_figure)
        self.main_window.stic_figures._refresh_figure_list()
        self.main_window.stic_figures.figure_combo.setCurrentIndex(self.figure_index)
        self.figure = restored_figure


class SetTileCommand(QUndoCommand):
    """Command for setting a single BACKTAB tile"""

    def __init__(self, main_window, figure, row, col, old_tile, new_tile):
        super().__init__(f"Set Tile ({row}, {col})")
        self.main_window = main_window
        self.figure = figure
        self.row = row
        self.col = col
        self.old_tile = old_tile.copy()
        self.new_tile = new_tile.copy()

    def redo(self):
        """Apply new tile"""
        self.figure.set_tile(
            self.row,
            self.col,
            self.new_tile["card"],
            self.new_tile["fg_color"],
            self.new_tile.get("bg_color", 0),
            self.new_tile.get("advance_stack", False)
        )
        self.main_window.stic_figures.canvas.update()

    def undo(self):
        """Restore old tile"""
        self.figure.set_tile(
            self.row,
            self.col,
            self.old_tile["card"],
            self.old_tile["fg_color"],
            self.old_tile.get("bg_color", 0),
            self.old_tile.get("advance_stack", False)
        )
        self.main_window.stic_figures.canvas.update()


class SetColorStackCommand(QUndoCommand):
    """Command for changing the color stack"""

    def __init__(self, main_window, figure, old_stack, new_stack):
        super().__init__(f"Set Color Stack")
        self.main_window = main_window
        self.figure = figure
        self.old_stack = old_stack.copy()
        self.new_stack = new_stack.copy()

    def redo(self):
        """Apply new color stack"""
        self.figure.color_stack = self.new_stack.copy()
        self.main_window.stic_figures.canvas.color_stack = self.new_stack.copy()
        self.main_window.stic_figures.canvas.update()

    def undo(self):
        """Restore old color stack"""
        self.figure.color_stack = self.old_stack.copy()
        self.main_window.stic_figures.canvas.color_stack = self.old_stack.copy()
        self.main_window.stic_figures.canvas.update()


class SetBorderCommand(QUndoCommand):
    """Command for changing border settings"""

    def __init__(self, main_window, figure, old_border, new_border):
        super().__init__(f"Set Border")
        self.main_window = main_window
        self.figure = figure
        self.old_border = old_border.copy()
        self.new_border = new_border.copy()

    def redo(self):
        """Apply new border settings"""
        self.figure.border_visible = self.new_border["visible"]
        self.figure.border_color = self.new_border["color"]
        self.figure.show_left_border = self.new_border["show_left"]
        self.figure.show_top_border = self.new_border["show_top"]

        # Update canvas
        self.main_window.stic_figures.canvas.border_visible = self.new_border["visible"]
        self.main_window.stic_figures.canvas.border_color = self.new_border["color"]
        self.main_window.stic_figures.canvas.show_left_border = self.new_border["show_left"]
        self.main_window.stic_figures.canvas.show_top_border = self.new_border["show_top"]
        self.main_window.stic_figures.canvas.update()

    def undo(self):
        """Restore old border settings"""
        self.figure.border_visible = self.old_border["visible"]
        self.figure.border_color = self.old_border["color"]
        self.figure.show_left_border = self.old_border["show_left"]
        self.figure.show_top_border = self.old_border["show_top"]

        # Update canvas
        self.main_window.stic_figures.canvas.border_visible = self.old_border["visible"]
        self.main_window.stic_figures.canvas.border_color = self.old_border["color"]
        self.main_window.stic_figures.canvas.show_left_border = self.old_border["show_left"]
        self.main_window.stic_figures.canvas.show_top_border = self.old_border["show_top"]
        self.main_window.stic_figures.canvas.update()
