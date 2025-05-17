# 📁 gui.py
import pygame
from utils import manhattan_distance

# Initialize Pygame
pygame.init()
info = pygame.display.Info()
WIDTH = int(info.current_w * 0.95)
HEIGHT = int(info.current_h * 0.9)
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("8-Puzzle Solver")

# Fonts
pygame.font.init()
tile_font = pygame.font.SysFont("Arial", 50, bold=True)
button_font = pygame.font.SysFont("Arial", 24)
title_font = pygame.font.SysFont("Arial", 30, bold=True)

# Colors
COLORS = {
    'BACKGROUND': (240, 240, 250),
    'TILE_EMPTY': (220, 220, 230),
    'TILE_ACTIVE': (100, 149, 237),
    'TEXT_BLACK': (0, 0, 0),
    'BUTTON_DEFAULT': (200, 210, 230),
    'BUTTON_HIGHLIGHT': (150, 180, 220),
    'GRID_LINE': (180, 180, 200)
}

# GUI drawing functions
def draw_board(self):
        """Vẽ bảng puzzle"""
        board_x = (self.WIDTH - self.TILE_SIZE * 3) // 2
        board_y = (self.HEIGHT - self.TILE_SIZE * 3) // 2

        pygame.draw.rect(self.WINDOW, self.COLORS['BACKGROUND'],
                        (board_x - 10, board_y - 10,
                        self.TILE_SIZE * 3 + 20, self.TILE_SIZE * 3 + 20),
                        border_radius=10)

        for i, num in enumerate(self.start_state):
            x = board_x + (i % 3) * self.TILE_SIZE
            y = board_y + (i // 3) * self.TILE_SIZE

            # 🟰 Check nếu tile này đang được di chuyển (highlight)
            if self.current_move and (i == self.current_move[0] or i == self.current_move[1]):
                color = (255, 215, 0)  # 🔥 Màu vàng Gold cho ô di chuyển
            else:
                color = self.COLORS['TILE_ACTIVE'] if num != 0 else self.COLORS['TILE_EMPTY']

            pygame.draw.rect(self.WINDOW, color,
                            (x, y, self.TILE_SIZE - 4, self.TILE_SIZE - 4),
                            border_radius=8)

            if num != 0:
                text = self.FONTS['TILE'].render(str(num), True, self.COLORS['TEXT_BLACK'])
                text_rect = text.get_rect(center=(x + self.TILE_SIZE // 2, y + self.TILE_SIZE // 2))
                self.WINDOW.blit(text, text_rect)

def draw_buttons(self):
    """Vẽ các nút thuật toán"""
    algorithms = list(self.ALGORITHMS.keys())
    algorithms.remove("Reset")
    algorithms.append("Reset")
        
    x_start, y_start = 20, 50
    btn_width, btn_height = 120, 40
    spacing_x, spacing_y = btn_width + 10, btn_height + 10
        
    # Vẽ tiêu đề
    title = self.FONTS['TITLE'].render("Algorithm", True, self.COLORS['TEXT_BLACK'])
    self.WINDOW.blit(title, (x_start, 10))
        
    button_positions = []
    for i, name in enumerate(algorithms):
        x = x_start + (i // 5) * (spacing_x + 20)
        y = y_start + (i % 5) * spacing_y
            
        # Màu nút
        color = self.COLORS['BUTTON_DEFAULT']
        if self.algorithm_name == name:
            color = self.COLORS['BUTTON_HIGHLIGHT']
            
        # Vẽ nút
        rect = pygame.Rect(x, y, btn_width, btn_height)
        pygame.draw.rect(self.WINDOW, color, rect, border_radius=6)
            
            # Chữ nút
        text = self.FONTS['BUTTON'].render(name, True, self.COLORS['TEXT_BLACK'])
        text_rect = text.get_rect(center=rect.center)
        self.WINDOW.blit(text, text_rect)
            
        button_positions.append((rect, name))
        
    return button_positions

def draw_state_tables(self):
    """Vẽ bảng trạng thái ban đầu và đích"""
    tile_size = 80
    table_x = self.WIDTH - 250
    board_top = 50

    # Trạng thái ban đầu
    title_font = pygame.font.SysFont("Arial", 24, bold=True)
    self.WINDOW.blit(title_font.render("Initial State", True, self.COLORS['TEXT_BLACK']), (table_x, board_top - 30))
        
    for i, num in enumerate(self.original_state):
        x = table_x + (i % 3) * tile_size
        y = board_top + (i // 3) * tile_size
        color = self.COLORS['TILE_ACTIVE'] if num != 0 else self.COLORS['TILE_EMPTY']
        pygame.draw.rect(self.WINDOW, color, (x, y, tile_size - 4, tile_size - 4), border_radius=8)
            
        if num != 0:
            text = self.FONTS['TILE'].render(str(num), True, self.COLORS['TEXT_BLACK'])
            self.WINDOW.blit(text, text.get_rect(center=(x + tile_size // 2, y + tile_size // 2)))

        # Trạng thái đích
    goal_top = board_top + tile_size * 3 + 40
    self.WINDOW.blit(title_font.render("Goal State", True, self.COLORS['TEXT_BLACK']), (table_x, goal_top - 30))
        
    for i, num in enumerate(self.goal_state):
        x = table_x + (i % 3) * tile_size
        y = goal_top + (i // 3) * tile_size
        color = self.COLORS['TILE_ACTIVE'] if num != 0 else self.COLORS['TILE_EMPTY']
        pygame.draw.rect(self.WINDOW, color, (x, y, tile_size - 4, tile_size - 4), border_radius=8)
            
        if num != 0:
            text = self.FONTS['TILE'].render(str(num), True, self.COLORS['TEXT_BLACK'])
            self.WINDOW.blit(text, text.get_rect(center=(x + tile_size // 2, y + tile_size // 2)))

def draw_algorithm_metrics(self, execution_time=None):
    """Hiển thị các số liệu về thuật toán"""
    if not self.algorithm_name or self.algorithm_name == "Reset":
        return

    metrics_x = self.WIDTH - 250
    metrics_y = self.HEIGHT - 150

        # Nền mờ
    metrics_surface = pygame.Surface((240, 140), pygame.SRCALPHA)
    metrics_surface.fill((200, 200, 200, 128))
    self.WINDOW.blit(metrics_surface, (metrics_x, metrics_y - 10))

    # Sử dụng thời gian thực thi được truyền vào nếu có, nếu không thì sử dụng thời gian kết thúc - bắt đầu
    time_value = execution_time if execution_time is not None else (self.end_time - self.start_time)
        
    metrics = [
        f"Algorithm: {self.algorithm_name}",
        f"Time: {time_value:.4f} seconds" if self.end_time > 0 else "Time: N/A",
        f"Steps: {len(self.solution) if self.solution else 'N/A'}"
    ]

    for i, metric in enumerate(metrics):
        text = self.FONTS['BUTTON'].render(metric, True, self.COLORS['TEXT_BLACK'])
        self.WINDOW.blit(text, (metrics_x + 10, metrics_y + i * 40))