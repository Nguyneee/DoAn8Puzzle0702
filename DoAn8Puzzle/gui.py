import pygame
import heapq
import time
import random
import math
from collections import deque
from typing import List, Tuple, Optional

class PuzzleSolver:
    """Lớp chính quản lý việc giải 8-Puzzle"""
    def __init__(self):
        # Cấu hình Pygame
        pygame.init()
        info = pygame.display.Info()
        self.WIDTH = int(info.current_w * 1)
        self.HEIGHT = int(info.current_h * 1)
        self.WINDOW = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("8-Puzzle Solver")
        self.clock = pygame.time.Clock()
        self.current_move = None
        self.speed_levels = [200, 100, 20]
        self.speed_names = ["Slow", "Medium", "Fast"]
        self.speed_index = 0
        self.step_delay = self.speed_levels[self.speed_index]

        # Cấu hình màu sắc
        self.COLORS = {
            'BACKGROUND': (240, 240, 250),
            'TILE_EMPTY': (220, 220, 230),
            'TILE_ACTIVE': (100, 149, 237),
            'TEXT_BLACK': (0, 0, 0),
            'BUTTON_DEFAULT': (200, 210, 230),
            'BUTTON_HIGHLIGHT': (150, 180, 220),
            'GRID_LINE': (180, 180, 200)
        }

        # Cấu hình phông chữ
        pygame.font.init()
        self.FONTS = {
            'TILE': pygame.font.SysFont("Arial", 50, bold=True),
            'BUTTON': pygame.font.SysFont("Arial", 24),
            'TITLE': pygame.font.SysFont("Arial", 30, bold=True)
        }

        # Cấu hình bảng
        self.TILE_SIZE = 100
        self.BOARD_SIZE = 3

        # Trạng thái game
        self.original_state = self.generate_fixed_puzzle()
        self.start_state = self.original_state.copy()
        self.goal_state = list(range(1, 9)) + [0]
        
        # Biến điều khiển
        self.running = True
        self.solving = False
        self.solution = []
        self.algorithm_name = None
        self.step_count = 0
        self.start_time = 0
        self.end_time = 0

        # Ánh xạ thuật toán
        self.ALGORITHMS = {
            "BFS": self.bfs_solve,
            "DFS": self.dfs_solve,
            "UCS": self.ucs_solve,
            "IDDFS": self.iddfs_solve,
            "Greedy": self.greedy_solve,
            "A*": self.astar_solve,
            "IDA*": self.ida_star_solve,
            "Hill": self.hill_climbing_solve,
            "Steepest Ascent": self.steepest_ascent_hill_climbing_solve,
            "And-Or": self.and_or_solve,
            "Observation": self.observation_search_solve,
            "Partial Obs": self.partial_observable_search_solve,
            "No Obs": self.no_observation_search_solve, 
            "Stochastic": self.stochastic_hill_climbing_solve,
            "SimulatedAnnealing": self.simulated_annealing_solve,
            "Beam": self.beam_search_solve,
            "Backtracking CSP": self.backtracking_csp_solve,
            "Const Checking": self.constraint_checking_solve,
            "AC3": self.ac3_solve,
            "Genetic": self.genetic_algorithm_solve,
            "Q-Learning": self.q_learning_solve,
            "Reset": "reset"
        }
