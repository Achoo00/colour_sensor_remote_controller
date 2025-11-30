"""
A scrollable grid of anime tiles.
"""
from typing import List, Dict, Any, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFrame, QGridLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize

from .anime_tile import AnimeTile

class AnimeGrid(QWidget):
    """A scrollable grid of anime tiles."""
    
    # Signal emitted when an anime tile is clicked
    # Parameters: (anime_title: str, episode: int)
    anime_selected = pyqtSignal(str, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._anime_list = []
        self._selected_index = -1
        self._tiles = []
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Container widget for the grid
        self.container = QWidget()
        self.grid_layout = QGridLayout(self.container)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.grid_layout.setSpacing(15)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Set up the scroll area
        scroll.setWidget(self.container)
        main_layout.addWidget(scroll)
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    
    def set_anime_list(self, anime_list: List[Dict[str, Any]]):
        """
        Set the list of anime to display in the grid.
        
        Args:
            anime_list: List of dictionaries containing anime data with keys:
                - 'title': The anime title
                - 'episode': The episode number
                - 'cover_url': (Optional) URL to the cover image
        """
        self._anime_list = anime_list
        self._selected_index = -1 if not anime_list else 0
        self._update_grid()
    
    def _update_grid(self):
        """Update the grid with the current anime list."""
        # Clear existing tiles
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self._tiles = []
        
        if not self._anime_list:
            return
        
        # Add anime tiles to the grid
        for i, anime in enumerate(self._anime_list):
            row = i // 4  # 4 columns
            col = i % 4
            
            tile = AnimeTile(
                anime_title=anime['title'],
                episode=anime.get('episode', 1),
                cover_url=anime.get('cover_url')
            )
            
            # Connect signals
            tile.clicked.connect(lambda checked, idx=i: self._on_tile_clicked(idx))
            
            # Add to grid
            self.grid_layout.addWidget(tile, row, col, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            self._tiles.append(tile)
        
        # Select the first tile by default
        if self._tiles:
            self._tiles[0].set_selected(True)
    
    def _on_tile_clicked(self, index: int):
        """Handle tile click events."""
        if 0 <= index < len(self._anime_list):
            self.select_anime(index)
            anime = self._anime_list[index]
            self.anime_selected.emit(anime['title'], anime.get('episode', 1))
    
    def select_anime(self, index: int):
        """Select the anime at the given index."""
        if not (0 <= index < len(self._tiles)):
            return
        
        # Deselect current selection
        if 0 <= self._selected_index < len(self._tiles):
            self._tiles[self._selected_index].set_selected(False)
        
        # Select new item
        self._selected_index = index
        self._tiles[index].set_selected(True)
    
    def get_selected_anime(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected anime, or None if none is selected."""
        if 0 <= self._selected_index < len(self._anime_list):
            return self._anime_list[self._selected_index]
        return None
    
    def keyPressEvent(self, event):
        """Handle key press events for navigation."""
        if not self._tiles:
            return
        
        current_row = self._selected_index // 4
        current_col = self._selected_index % 4
        new_index = self._selected_index
        
        if event.key() == Qt.Key.Key_Right:
            new_index = min(self._selected_index + 1, len(self._tiles) - 1)
        elif event.key() == Qt.Key.Key_Left:
            new_index = max(0, self._selected_index - 1)
        elif event.key() == Qt.Key.Key_Down:
            new_row = min(current_row + 1, (len(self._tiles) - 1) // 4)
            new_index = min(new_row * 4 + current_col, len(self._tiles) - 1)
        elif event.key() == Qt.Key.Key_Up:
            new_row = max(0, current_row - 1)
            new_index = new_row * 4 + current_col
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if 0 <= self._selected_index < len(self._anime_list):
                anime = self._anime_list[self._selected_index]
                self.anime_selected.emit(anime['title'], anime.get('episode', 1))
            return
        else:
            super().keyPressEvent(event)
            return
        
        if new_index != self._selected_index:
            self.select_anime(new_index)
        
        # Ensure the selected item is visible
        self.ensure_visible(new_index)
    
    def ensure_visible(self, index: int):
        """Ensure the tile at the given index is visible in the scroll area."""
        if not (0 <= index < len(self._tiles)):
            return
        
        # Get the scroll area's viewport
        scroll_area = self.parentWidget().parentWidget()
        if not isinstance(scroll_area, QScrollArea):
            return
        
        # Get the tile's position in the scroll area
        tile = self._tiles[index]
        pos = tile.mapTo(scroll_area, tile.rect().topLeft())
        
        # Calculate the visible area
        viewport = scroll_area.viewport()
        view_rect = viewport.rect()
        
        # Scroll if needed
        if pos.y() < view_rect.top() + 50:  # 50px margin
            scroll_area.verticalScrollBar().setValue(
                scroll_area.verticalScrollBar().value() + pos.y() - view_rect.top() - 50
            )
        elif pos.y() + tile.height() > view_rect.bottom() - 50:  # 50px margin
            scroll_area.verticalScrollBar().setValue(
                scroll_area.verticalScrollBar().value() + 
                (pos.y() + tile.height() - view_rect.bottom() + 50)
            )
    
    def sizeHint(self) -> QSize:
        """Provide a reasonable default size for the widget."""
        return QSize(800, 600)
