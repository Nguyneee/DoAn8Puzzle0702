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





###Utils Functions###
    def generate_fixed_puzzle(self) -> List[int]:
        """Tạo trạng thái ban đầu của puzzle"""
        return [2,6,5,0,8,7,4,3,1] #[2,3,6,1,5,0,4,7,8]

    def manhattan_distance(self, state: List[int]) -> int:
        """Tính khoảng cách Manhattan"""
        goal_pos = {val: (idx % 3, idx // 3) for idx, val in enumerate(range(1, 9))}
        goal_pos[0] = (2, 2)
        return sum(
            abs((state.index(val) % 3) - goal_pos[val][0]) +
            abs((state.index(val) // 3) - goal_pos[val][1])
            for val in state if val != 0
        )

    def get_next_states(self, state: List[int]) -> List[Tuple[List[int], Tuple[int, int]]]:
        """Sinh các trạng thái kế tiếp"""
        zero_idx = state.index(0)
        moves = [-3, 3, -1, 1]
        next_states = []
        for move in moves:
            new_idx = zero_idx + move
            if 0 <= new_idx < 9 and (
                (move in [-1, 1] and zero_idx // 3 == new_idx // 3) or
                (move in [-3, 3])
            ):
                new_state = state.copy()
                new_state[zero_idx], new_state[new_idx] = new_state[new_idx], new_state[zero_idx]
                next_states.append((new_state, (zero_idx, new_idx)))
        return next_states
    def is_solvable(self, state):
        """Kiểm tra trạng thái có giải được không (dựa trên inversion count)"""
        inversions = 0
        for i in range(len(state)):
            if state[i] == 0:
                continue
            for j in range(i + 1, len(state)):
                if state[j] != 0 and state[i] > state[j]:
                    inversions += 1
        return inversions % 2 == 0



#####GUI Functions#####
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
            # Nút đổi tốc độ
            speed_rect = pygame.Rect(20, self.HEIGHT - 60, 150, 40)
            color = self.COLORS['BUTTON_HIGHLIGHT']
            pygame.draw.rect(self.WINDOW, color, speed_rect, border_radius=6)

            speed_label = f"Speed: {self.speed_names[self.speed_index]}"
            speed_text = self.FONTS['BUTTON'].render(speed_label, True, self.COLORS['TEXT_BLACK'])
            self.WINDOW.blit(speed_text, speed_rect.move(10, 10))

            button_positions.append((speed_rect, "speed_cycle"))
            
            exit_rect = pygame.Rect(self.WIDTH - 170, self.HEIGHT - 60, 120, 40)
            pygame.draw.rect(self.WINDOW, self.COLORS['BUTTON_DEFAULT'], exit_rect, border_radius=6)
            exit_text = self.FONTS['BUTTON'].render("Exit", True, self.COLORS['TEXT_BLACK'])
            self.WINDOW.blit(exit_text, exit_rect.move(25, 10))
            button_positions.append((exit_rect, "exit_app"))
            random_rect = pygame.Rect(350, self.HEIGHT - 60, 150, 40)
            pygame.draw.rect(self.WINDOW, self.COLORS['BUTTON_DEFAULT'], random_rect, border_radius=6)
            random_text = self.FONTS['BUTTON'].render("Random", True, self.COLORS['TEXT_BLACK'])
            self.WINDOW.blit(random_text, random_rect.move(30, 10))
            button_positions.append((random_rect, "backtrack_random"))
        
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
        return
    def draw_input_box(self, x, y, initial_value):
        input_rect = pygame.Rect(x, y, 200, 40)
        color_inactive = pygame.Color('lightskyblue3')
        color_active = pygame.Color('dodgerblue2')
        color = color_inactive
        active = False
        text = ','.join(map(str, initial_value))
        error_msg = ""

        font = pygame.font.SysFont("Arial", 24)
        hint_font = pygame.font.SysFont("Arial", 20)
        error_font = pygame.font.SysFont("Arial", 18)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return initial_value
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_rect.collidepoint(event.pos):
                        active = True
                    else:
                        active = False
                    color = color_active if active else color_inactive

                if event.type == pygame.KEYDOWN and active:
                    if event.key == pygame.K_RETURN:
                        try:
                            new_state = [int(x.strip()) for x in text.split(',')]
                            if len(new_state) == 9 and set(new_state) == set(range(9)):
                                return new_state
                            else:
                                error_msg = "Phai dung 9 so tu 0 den 8!"
                        except ValueError:
                            error_msg = "Chi duoc nhap so!"
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

            overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
            overlay.fill((128, 128, 128, 128))
            self.WINDOW.blit(overlay, (0, 0))

            pygame.draw.rect(self.WINDOW, color, input_rect, 2)
            txt_surface = font.render(text, True, color)
            width = max(200, txt_surface.get_width() + 10)
            input_rect.w = width
            self.WINDOW.blit(txt_surface, (input_rect.x + 5, input_rect.y + 5))

            hint_text = hint_font.render("Nhap so 0 den 8 , so nhau du phay (VD: 1,2,3,4,0,5,6,7,8)", True, (255, 255, 255))
            self.WINDOW.blit(hint_text, (input_rect.x, input_rect.y - 30))

            if error_msg:
                error_surface = error_font.render(error_msg, True, (255, 0, 0))
                self.WINDOW.blit(error_surface, (input_rect.x, input_rect.y + 50))

            pygame.display.flip()
            self.clock.tick(30)
    def draw_solution_table(self, execution_time=None):
        """Vẽ bảng thông tin giải pháp ở góc dưới bên trái"""
        if not self.solution:
            return
        
        # Vị trí của bảng solution
        table_x = 50
        table_y = self.HEIGHT - 200
        
        # Tạo nền mờ cho bảng
        solution_surface = pygame.Surface((400, 180), pygame.SRCALPHA)
        solution_surface.fill((200, 200, 220, 200))
        self.WINDOW.blit(solution_surface, (table_x - 10, table_y - 10))
        
        # Tiêu đề bảng
        title = self.FONTS['TITLE'].render("Solution Details", True, self.COLORS['TEXT_BLACK'])
        self.WINDOW.blit(title, (table_x, table_y))
        
        # Thông tin về solution
        info_font = pygame.font.SysFont("Arial", 22)
        
        # Sử dụng thời gian thực thi được truyền vào nếu có, nếu không thì sử dụng thời gian kết thúc - bắt đầu
        time_value = execution_time if execution_time is not None else (self.end_time - self.start_time)
        
        solution_info = [
            f"Algorithm: {self.algorithm_name}",
            f"Total moves: {len(self.solution)}",
            f"Current step: {self.step_count}/{len(self.solution)}",
            f"Execution time: {time_value:.4f} sec"
        ]
        
        for i, info in enumerate(solution_info):
            text = info_font.render(info, True, self.COLORS['TEXT_BLACK'])
            self.WINDOW.blit(text, (table_x, table_y + 40 + i * 30))
        
        # Hiển thị các bước di chuyển gần đây (tối đa 5 bước)
        if len(self.solution) > 0:
            moves_title = info_font.render("Recent moves:", True, self.COLORS['TEXT_BLACK'])
            self.WINDOW.blit(moves_title, (table_x + 200, table_y + 40))
            
            # Xác định các bước gần đây cần hiển thị
            start_idx = max(0, self.step_count - 5)
            end_idx = self.step_count
            recent_moves = self.solution[start_idx:end_idx]
            
            for i, move in enumerate(recent_moves):
                # Chuyển đổi chỉ số sang tọa độ 2D để dễ hiểu hơn
                from_pos = (move[0] % 3, move[0] // 3)
                to_pos = (move[1] % 3, move[1] // 3)
                
                # Xác định hướng di chuyển
                if to_pos[0] > from_pos[0]:
                    direction = "Right"
                elif to_pos[0] < from_pos[0]:
                    direction = "Left"
                elif to_pos[1] > from_pos[1]:
                    direction = "Down"
                else:
                    direction = "Up"
                
                move_text = info_font.render(f"{start_idx + i + 1}: {direction}", True, self.COLORS['TEXT_BLACK'])
                self.WINDOW.blit(move_text, (table_x + 200, table_y + 70 + i * 20))
    
    
    
    
    ####Algorithm Functions###
    def bfs_solve(self, start_state):
        return self.generic_solve(start_state, self.goal_state, queue=deque([(start_state, [])]), pop_method='popleft')

    def dfs_solve(self, start_state, max_depth=100):
        goal = self.goal_state
        stack = [(start_state, [], 0)]
        visited = set()
        visited.add(tuple(start_state))

        while stack:
            state, path, depth = stack.pop()

            if state == goal:
                return path

            if depth >= max_depth:
                continue

            zero_idx = state.index(0)
            moves = [-3, 3, -1, 1]

            for move in moves:
                new_idx = zero_idx + move
                if 0 <= new_idx < 9 and (
                    (move in [-1, 1] and zero_idx // 3 == new_idx // 3) or
                    (move in [-3, 3])
                ):
                    new_state = state[:]
                    new_state[zero_idx], new_state[new_idx] = new_state[new_idx], new_state[zero_idx]

                    if tuple(new_state) not in visited:
                        visited.add(tuple(new_state))
                        stack.append((new_state, path + [(zero_idx, new_idx)], depth + 1))

        return None
    def ucs_solve(self, start_state):
        return self.generic_solve(start_state, self.goal_state, [(0, start_state, [])], 'heappop', is_priority=True)

    def greedy_solve(self, start_state):
        return self.generic_solve(start_state, self.goal_state, [(self.manhattan_distance(start_state), start_state, [])], 'heappop', is_priority=True)

    def astar_solve(self, start_state):
        visited = set()
        goal = self.goal_state
        pq = [(self.manhattan_distance(start_state), 0, start_state, [])]
        while pq:
            f, g, state, path = heapq.heappop(pq)
            if state == goal:
                return path
            if tuple(state) in visited:
                continue
            visited.add(tuple(state))
            for new_state, move in self.get_next_states(state):
                if tuple(new_state) not in visited:
                    new_g = g + 1
                    new_f = new_g + self.manhattan_distance(new_state)
                    heapq.heappush(pq, (new_f, new_g, new_state, path + [move]))
        return None

    def iddfs_solve(self, start_state):
        goal = self.goal_state
        def dls(state, path, depth_limit, visited):
            if state == goal:
                return path
            if len(path) >= depth_limit:
                return None
            next_list = []
            for new_state, move in self.get_next_states(state):
                if tuple(new_state) not in visited:
                    next_list.append((new_state, path + [move]))
            next_list.sort(key=lambda x: self.manhattan_distance(x[0]))
            for st, p in next_list:
                visited.add(tuple(st))
                res = dls(st, p, depth_limit, visited)
                if res:
                    return res
            return None

        for depth_limit in range(5, 50, 5):
            visited = set()
            res = dls(start_state, [], depth_limit, visited)
            if res:
                return res
        return None

    def ida_star_solve(self, start_state):
        goal = self.goal_state
        def search(path, g, threshold):
            state = path[-1]
            f = g + self.manhattan_distance(state)
            if f > threshold:
                return f, None
            if state == goal:
                return f, []
            min_threshold = float('inf')
            for new_state, move in self.get_next_states(state):
                if new_state in path:
                    continue
                t, result_path = search(path + [new_state], g + 1, threshold)
                if result_path is not None:
                    return t, [move] + result_path
                min_threshold = min(min_threshold, t)
            return min_threshold, None

        threshold = self.manhattan_distance(start_state)
        path = [start_state]
        while True:
            t, result = search(path, 0, threshold)
            if result is not None:
                return result
            if t == float('inf'):
                return None
            threshold = t

    def hill_climbing_solve(self, start_state):
        goal = self.goal_state
        current = start_state.copy()
        path = []
        visited = set()
        while True:
            if current == goal:
                return path
            visited.add(tuple(current))
            neighbors = []
            for new_state, move in self.get_next_states(current):
                if tuple(new_state) not in visited:
                    h = self.manhattan_distance(new_state)
                    neighbors.append((h, new_state, move))
            if not neighbors:
                return None
            neighbors.sort()
            best_h, best_state, best_move = neighbors[0]
            if self.manhattan_distance(current) <= best_h:
                return None
            current = best_state
            path.append(best_move)

    def steepest_ascent_hill_climbing_solve(self, start_state):
        goal = self.goal_state
        current = start_state.copy()
        path = []
        while True:
            if current == goal:
                return path
            neighbors = []
            for new_state, move in self.get_next_states(current):
                h = self.manhattan_distance(new_state)
                neighbors.append((h, new_state, move))
            neighbors.sort()
            best_h, best_state, best_move = neighbors[0]
            if self.manhattan_distance(current) <= best_h:
                return None
            current = best_state
            path.append(best_move)

    def stochastic_hill_climbing_solve(self, start_state):
        goal = self.goal_state
        current = start_state.copy()
        path = []
        while True:
            if current == goal:
                return path
            neighbors = []
            current_h = self.manhattan_distance(current)
            for new_state, move in self.get_next_states(current):
                h = self.manhattan_distance(new_state)
                if h < current_h:
                    neighbors.append((h, new_state, move))
            if not neighbors:
                return None
            _, chosen_state, chosen_move = random.choice(neighbors)
            current = chosen_state
            path.append(chosen_move)
    def simulated_annealing_solve(self, start_state):
        goal = self.goal_state
        current = start_state[:]
        path = []
        T = 100.0                   # Nhiệt độ ban đầu
        alpha = 0.995               # Tốc độ làm nguội
        min_T = 0.01                # Nhiệt độ kết thúc
        max_steps = 10000           # Giới hạn số bước

        def acceptance_prob(current_h, new_h, temperature):
            if new_h < current_h:
                return 1.0
            else:
                try:
                    return math.exp((current_h - new_h) / temperature)
                except OverflowError:
                    return 0

        def heuristic(state):
            return self.manhattan_distance(state)

        current_h = heuristic(current)
        steps = 0
        visited = set()

        while T > min_T and steps < max_steps:
            if current == goal:
                return path

            zero_idx = current.index(0)
            moves = [-3, 3, -1, 1]
            neighbors = []

            for move in moves:
                new_idx = zero_idx + move
                if 0 <= new_idx < 9 and (
                    (move in [-1, 1] and zero_idx // 3 == new_idx // 3) or
                    (move in [-3, 3])
                ):
                    new_state = current[:]
                    new_state[zero_idx], new_state[new_idx] = new_state[new_idx], new_state[zero_idx]
                    if tuple(new_state) not in visited:
                        neighbors.append((new_state, (zero_idx, new_idx)))

            if not neighbors:
                break

            next_state, move = random.choice(neighbors)
            next_h = heuristic(next_state)

            if acceptance_prob(current_h, next_h, T) > random.random():
                current = next_state
                current_h = next_h
                path.append(move)
                visited.add(tuple(current))

            T *= alpha
            steps += 1

        return path if current == goal else None
    def beam_search_solve(self, start_state, beam_width=2):
        goal = self.goal_state
        beam = [(start_state, [])]
        visited = set()

        while beam:
            new_beam = []
            for state, path in beam:
                if state == goal:
                    return path
                for new_state, move in self.get_next_states(state):
                    if tuple(new_state) not in visited:
                        new_path = path + [move]
                        h = self.manhattan_distance(new_state)
                        new_beam.append((h, new_state, new_path))
                        visited.add(tuple(new_state))
            if not new_beam:
                break
            new_beam.sort(key=lambda x: x[0])
            beam = [(state, path) for _, state, path in new_beam[:beam_width]]

        return None
    def generic_solve(self, start_state, goal_state, queue, pop_method, is_priority=False):
        visited = set()
        while queue:
            if is_priority:
                _, state, path = heapq.heappop(queue)
            else:
                state, path = getattr(queue, pop_method)()
            if state == goal_state:
                return path
            zero_idx = state.index(0)
            for new_state, move in self.get_next_states(state):
                if tuple(new_state) not in visited:
                    visited.add(tuple(new_state))
                    new_path = path + [move]
                    if is_priority:
                        heapq.heappush(queue, (self.manhattan_distance(new_state), new_state, new_path))
                    else:
                        queue.append((new_state, new_path))
        return None
    def and_or_solve(self, start_state):
        """
        Giải 8-puzzle bằng thuật toán And-Or Graph Search.
        """
        visited = set()  # Lưu trạng thái đã duyệt để tránh lặp vô hạn
        goal = self.goal_state
        
        # Hàm kiểm tra khả năng giải được của trạng thái
        def is_solvable(state):
            # Tính số nghịch thế (inversion)
            inversions = 0
            for i in range(len(state)):
                if state[i] == 0:
                    continue
                for j in range(i + 1, len(state)):
                    if state[j] != 0 and state[i] > state[j]:
                        inversions += 1
            return inversions % 2 == 0
        
        # Nếu trạng thái ban đầu không thể giải được, trả về None
        if not is_solvable(start_state) and is_solvable(goal):
            return None
        
        # Hàm đệ quy để duyệt cây AND-OR
        def recursive_dfs(state, depth=0, max_depth=30):
            if state == goal:
                return []  # Đã tìm thấy mục tiêu, trả về danh sách rỗng
            
            if depth >= max_depth:
                return None  # Vượt quá độ sâu tối đa
            
            state_tuple = tuple(state)
            if state_tuple in visited:
                return None  # Tránh lặp lại trạng thái
            
            visited.add(state_tuple)
            
            # Đây là nút OR: chúng ta cần tìm ít nhất một đường đi tới đích
            next_moves = self.get_next_states(state)
            
            for next_state, move in next_moves:
                # Gọi đệ quy để tìm đường đi từ trạng thái kế tiếp
                path = recursive_dfs(next_state, depth + 1, max_depth)
                
                if path is not None:
                    # Nếu tìm thấy đường đi, thêm bước di chuyển hiện tại vào đầu đường đi
                    return [move] + path
            
            # Không tìm thấy đường đi nào đến đích
            return None
        
        # Bắt đầu thuật toán với trạng thái ban đầu
        return recursive_dfs(start_state)
    def observation_search_solve(self, start_state):
        """
        Giải 8-puzzle bằng tìm kiếm không quan sát toàn bộ.
        Tác nhân chỉ nhìn thấy các trạng thái lân cận và chọn ngẫu nhiên 1 trong số đó.
        """
        goal = self.goal_state
        current = start_state[:]
        path = []
        visited = set()
        max_steps = 200
        steps = 0

        while steps < max_steps:
            if current == goal:
                return path

            visited.add(tuple(current))
            zero_idx = current.index(0)
            moves = [-3, 3, -1, 1]
            neighbors = []

            for move in moves:
                new_idx = zero_idx + move
                if 0 <= new_idx < 9 and (
                    (move in [-1, 1] and zero_idx // 3 == new_idx // 3) or
                    (move in [-3, 3])
                ):
                    new_state = current[:]
                    new_state[zero_idx], new_state[new_idx] = new_state[new_idx], new_state[zero_idx]
                    if tuple(new_state) not in visited:
                        neighbors.append((new_state, (zero_idx, new_idx)))

            if not neighbors:
                break  # bị kẹt, không có nơi nào chưa đi

            next_state, move = random.choice(neighbors)
            current = next_state
            path.append(move)
            steps += 1

        return path if current == goal else None
    def partial_observable_search_solve(self, start_state):
        """
        Giải 8-Puzzle theo kiểu Partial Observable Search:
        - Biết chắc 3 ô đầu tiên (1st row) là đúng thứ tự.
        - Các ô còn lại sẽ đoán ngẫu nhiên và tìm kiếm giải pháp.
        """
        goal = self.goal_state
        known = start_state[:3]  # Biết chắc 3 ô đầu tiên

        # Tạo các trạng thái có thể có cho 6 ô còn lại
        unknown = start_state[3:]
        candidates = []
        
        # Sinh ra nhiều hoán vị có thể
        from itertools import permutations
        for perm in permutations(unknown):
            candidate = known + list(perm)
            candidates.append(candidate)

        # Thử tìm kiếm trên mỗi trạng thái ứng viên
        for candidate in candidates:
            if self.is_solvable(candidate):
                # Dùng BFS thử giải
                path = self.bfs_solve(candidate)
                if path:
                    print("Found solution from partial observable search.")
                    self.animate_solution(path)
                    return path

        return None  # Nếu không tìm thấy giải pháp
    def backtrack_csp(self, assignment, index, csp, nodes_expanded, max_depth, current_state, path):
        nodes_expanded[0] += 1
        max_depth[0] = max(max_depth[0], len(assignment))

        if index == len(csp['variables']):
            final_state = [assignment[f"X{i+1}"] for i in range(9)]
            return (assignment, path) if self.is_solvable(final_state) else (None, [])

        var = csp['variables'][index]
        domain = csp['domains'][var]

        for value in domain:
            if self.is_consistent_csp(var, value, assignment, csp):
                assignment[var] = value
                idx = int(var[1:]) - 1
                new_state = current_state[:]
                if new_state[idx] != value:
                    swap_idx = new_state.index(value)
                    new_state[idx], new_state[swap_idx] = new_state[swap_idx], new_state[idx]
                    move = (swap_idx, idx)
                else:
                    move = None

                result, sub_path = self.backtrack_csp(assignment, index + 1, csp, nodes_expanded, max_depth, new_state, path + ([move] if move else []))
                if result:
                    return result, sub_path

                del assignment[var]

        return None, []
    def is_consistent_csp(self, var, value, assignment, csp):
        if value in assignment.values():
            return False
        temp_assignment = assignment.copy()
        temp_assignment[var] = value
        for var1, var2, func in csp['constraints']:
            if var1 in temp_assignment and var2 in temp_assignment:
                if not func(temp_assignment[var1], temp_assignment[var2]):
                    return False
        return True
    def create_constraints(self):
        constraints = []
        for r in range(3):
            for c in range(2):
                a = f"X{r * 3 + c + 1}"
                b = f"X{r * 3 + c + 2}"
                constraints.append((a, b, lambda l, r: r == l + 1 and l != 0))
        for c in range(3):
            for r in range(2):
                a = f"X{r * 3 + c + 1}"
                b = f"X{(r + 1) * 3 + c + 1}"
                constraints.append((a, b, lambda t, b: b == t + 3 and t != 0))
        return constraints
    def backtracking_csp_solve(self, start_state):
        nodes_expanded = [0]
        max_depth = [0]
        path = []

        variables = [f"X{i+1}" for i in range(9)]
        domains = {var: list(range(9)) for var in variables}

        for var in domains:
            random.shuffle(domains[var])  # để thêm tính ngẫu nhiên

        constraints = self.create_constraints()
        csp = {
            'variables': variables,
            'domains': domains,
            'constraints': constraints
        }

        result, move_path = self.backtrack_csp({}, 0, csp, nodes_expanded, max_depth, start_state[:], path)
        if result:
            return move_path
        else:
            return None


   
    def no_observation_search_solve(self, start_state):
        def manhattan_distance(state):
            goal_pos = {val: (idx % 3, idx // 3) for idx, val in enumerate(range(1, 9))}
            goal_pos[0] = (2, 2)
            return sum(
                abs((state.index(val) % 3) - goal_pos[val][0]) +
                abs((state.index(val) // 3) - goal_pos[val][1])
                for val in state if val != 0
            )

        goal_state = list(range(1, 9)) + [0]
        visited = set()
        path = []
        MAX_DEPTH = 50

        def explore(state, depth=0):
            if state == goal_state:
                return True
            if depth > MAX_DEPTH:
                return False
            visited.add(tuple(state))
            zero_idx = state.index(0)
            moves = [-3, 3, -1, 1]
            next_states = []
            for move in moves:
                new_idx = zero_idx + move
                if 0 <= new_idx < 9 and (
                    (move in [-1, 1] and zero_idx // 3 == new_idx // 3) or (move in [-3, 3])
                ):
                    new_state = state[:]
                    new_state[zero_idx], new_state[new_idx] = new_state[new_idx], new_state[zero_idx]
                    if tuple(new_state) not in visited:
                        next_states.append((new_state, (zero_idx, new_idx)))
            next_states.sort(key=lambda x: manhattan_distance(x[0]))
            for new_state, move in next_states:
                path.append(move)
                if explore(new_state, depth + 1):
                    return True
                path.pop()
            return False

        if explore(start_state):
            return path
        return None
    def partial_observable_belief_search_solve(self, start_state):
        from collections import deque
        goal_state = list(range(1, 9)) + [0]
        observed_indices = [0, 1, 2]

        def is_solvable(state):
            inversions = 0
            for i in range(len(state)):
                if state[i] == 0:
                    continue
                for j in range(i + 1, len(state)):
                    if state[j] != 0 and state[i] > state[j]:
                        inversions += 1
            return inversions % 2 == 0

        if not is_solvable(start_state):
            return None

        visited = set()
        queue = deque([(start_state, [])])

        while queue:
            current_state, path = queue.popleft()

            if current_state == goal_state:
                return path

            zero_idx = current_state.index(0)
            moves = [-3, 3, -1, 1]

            for move in moves:
                new_idx = zero_idx + move
                if 0 <= new_idx < 9 and (
                    (move in [-1, 1] and zero_idx // 3 == new_idx // 3) or
                    (move in [-3, 3])
                ):
                    if new_idx in observed_indices:
                        continue

                    new_state = current_state[:]
                    new_state[zero_idx], new_state[new_idx] = new_state[new_idx], new_state[zero_idx]

                    if tuple(new_state) not in visited:
                        visited.add(tuple(new_state))
                        queue.append((new_state, path + [(zero_idx, new_idx)]))

        return None
    def constraint_checking_solve(self, start_state):
        from collections import deque
        goal = self.goal_state
        visited = set()
        queue = deque([(start_state, [])])

        while queue:
            state, path = queue.popleft()
            if state == goal:
                return path

            zero_idx = state.index(0)
            moves = [-3, 3, -1, 1]

            for move in moves:
                new_idx = zero_idx + move
                if 0 <= new_idx < 9 and (
                    (move in [-1, 1] and zero_idx // 3 == new_idx // 3) or
                    (move in [-3, 3])
                ):
                    new_state = state[:]
                    new_state[zero_idx], new_state[new_idx] = new_state[new_idx], new_state[zero_idx]

                    if tuple(new_state) not in visited:
                        visited.add(tuple(new_state))
                        queue.append((new_state, path + [(zero_idx, new_idx)]))
        return None
    def ac3_solve(self, start_state):
        from collections import deque
        goal = self.goal_state
        visited = set()
        queue = deque([(start_state, [])])

        while queue:
            state, path = queue.popleft()
            if state == goal:
                return path

            zero_idx = state.index(0)
            moves = [-3, 3, -1, 1]
            for move in moves:
                new_idx = zero_idx + move
                if 0 <= new_idx < 9 and (
                    (move in [-1, 1] and zero_idx // 3 == new_idx // 3) or
                    (move in [-3, 3])
                ):
                    new_state = state[:]
                    new_state[zero_idx], new_state[new_idx] = new_state[new_idx], new_state[zero_idx]
                    if tuple(new_state) not in visited:
                        visited.add(tuple(new_state))
                        queue.append((new_state, path + [(zero_idx, new_idx)]))
        return None
    def genetic_algorithm_solve(self, start_state):
        import random
        goal = self.goal_state
        population_size = 50
        mutation_rate = 0.1
        generations = 200

        def fitness(state):
            return sum([1 if state[i] == goal[i] else 0 for i in range(9)])

        def crossover(p1, p2):
            cut = random.randint(1, 8)
            child = p1[:cut]
            for num in p2:
                if num not in child:
                    child.append(num)
            return child

        def mutate(state):
            if random.random() < mutation_rate:
                i, j = random.sample(range(9), 2)
                state[i], state[j] = state[j], state[i]
            return state

        population = [random.sample(range(9), 9) for _ in range(population_size)]
        best_path = []

        for _ in range(generations):
            population.sort(key=lambda x: -fitness(x))
            best = population[0]
            if best == goal:
                # Tạo path animation từ start_state đến best
                temp = start_state[:]
                path = []
                for i in range(9):
                    if temp[i] != best[i]:
                        j = temp.index(best[i])
                        path.append((i, j))
                        temp[i], temp[j] = temp[j], temp[i]
                self.animate_solution(path)
                return path

            next_gen = []
            for _ in range(population_size):
                p1, p2 = random.choices(population[:10], k=2)
                child = crossover(p1, p2)
                next_gen.append(mutate(child))
            population = next_gen

        return None
    def q_learning_solve(self, start_state, episodes=5000, alpha=0.1, gamma=0.9, epsilon=0.2):
        import random
        from collections import defaultdict

        goal = self.goal_state
        actions = [-3, 3, -1, 1]
        q_table = defaultdict(lambda: {a: 0 for a in actions})

        def get_next_states(state):
            zero_idx = state.index(0)
            next_states = []
            for move in actions:
                new_idx = zero_idx + move
                if 0 <= new_idx < 9 and (
                    (move in [-1, 1] and zero_idx // 3 == new_idx // 3) or
                    (move in [-3, 3])
                ):
                    new_state = state[:]
                    new_state[zero_idx], new_state[new_idx] = new_state[new_idx], new_state[zero_idx]
                    next_states.append((move, new_state))
            return next_states

        for _ in range(episodes):
            state = start_state[:]
            for _ in range(100):
                if state == goal:
                    break
                state_t = tuple(state)
                move = random.choice(actions) if random.random() < epsilon else max(q_table[state_t], key=q_table[state_t].get)
                next_state = None
                for m, s in get_next_states(state):
                    if m == move:
                        next_state = s
                        break
                if not next_state:
                    continue
                reward = 1 if next_state == goal else -0.1
                q_table[state_t][move] += alpha * (reward + gamma * max(q_table[tuple(next_state)].values()) - q_table[state_t][move])
                state = next_state

        current = start_state[:]
        path = []
        visited = set()
        for _ in range(100):
            if current == goal:
                self.animate_solution(path)
                return path
            move = max(q_table[tuple(current)], key=q_table[tuple(current)].get)
            zero_idx = current.index(0)
            new_idx = zero_idx + move
            if not (0 <= new_idx < 9): return None
            if move in [-1, 1] and zero_idx // 3 != new_idx // 3: return None
            next_state = current[:]
            next_state[zero_idx], next_state[new_idx] = next_state[new_idx], next_state[zero_idx]
            if tuple(next_state) in visited: return None
            visited.add(tuple(next_state))
            path.append((zero_idx, new_idx))
            current = next_state

        return None
    
    
    
    
    def animate_solution(self, path):
        for zero_idx, move_idx in path:
            self.start_state[zero_idx], self.start_state[move_idx] = self.start_state[move_idx], self.start_state[zero_idx]
            self.current_move = (zero_idx, move_idx)
            self.draw_board()
            pygame.display.flip()
            pygame.time.delay(self.step_delay)
    ###Main loop###
    def run(self):
        """Vòng lặp chính của trò chơi"""
        button_positions = []
        edit_initial_rect = pygame.Rect(self.WIDTH - 250, self.HEIGHT - 250, 200, 40)
        edit_goal_rect = pygame.Rect(self.WIDTH - 250, self.HEIGHT - 200, 200, 40)
        
        # Thêm biến để lưu thời gian thực thi thuật toán
        execution_time = 0
        
        while self.running:
            self.WINDOW.fill(self.COLORS['BACKGROUND'])
            
            # Vẽ các thành phần
            button_positions = self.draw_buttons()
            self.draw_board()
            self.draw_state_tables()
            self.draw_algorithm_metrics(execution_time)
            
            # Vẽ bảng solution nếu có giải pháp
            if self.solution:
                self.draw_solution_table(execution_time)
            
            # Nút chỉnh sửa trạng thái  
            pygame.draw.rect(self.WINDOW, self.COLORS['BUTTON_DEFAULT'], edit_initial_rect, border_radius=6)
            pygame.draw.rect(self.WINDOW, self.COLORS['BUTTON_DEFAULT'], edit_goal_rect, border_radius=6)
            
            edit_initial_text = self.FONTS['BUTTON'].render("Input Initial State", True, self.COLORS['TEXT_BLACK'])
            edit_goal_text = self.FONTS['BUTTON'].render("Input Goal State", True, self.COLORS['TEXT_BLACK'])
        
            
            self.WINDOW.blit(edit_initial_text, (edit_initial_rect.x + 10, edit_initial_rect.y + 10))
            self.WINDOW.blit(edit_goal_text, (edit_goal_rect.x + 10, edit_goal_rect.y + 10))

            # Xử lý sự kiện
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Xử lý sự kiện nhấp chuột
                    if edit_initial_rect.collidepoint(event.pos):
                        # Chỉnh sửa trạng thái ban đầu
                        self.original_state = self.draw_input_box(
                            edit_initial_rect.x, 
                            edit_initial_rect.y + edit_initial_rect.height + 10, 
                            self.original_state
                        )
                        self.start_state = self.original_state.copy()
                        # Reset trạng thái
                        self.solving = False
                        self.solution = []
                        self.step_count = 0
                        self.algorithm_name = None
                        self.start_time = 0
                        self.end_time = 0
                        execution_time = 0
                    
                    elif edit_goal_rect.collidepoint(event.pos):
                        # Chỉnh sửa trạng thái đích
                        self.goal_state = self.draw_input_box(
                            edit_goal_rect.x, 
                            edit_goal_rect.y + edit_goal_rect.height + 10, 
                            self.goal_state
                        )
                        # Reset trạng thái
                        self.solving = False
                        self.solution = []
                        self.step_count = 0
                        self.algorithm_name = None
                        self.start_time = 0
                        self.end_time = 0
                        execution_time = 0
                    
                    # Các sự kiện khác như cũ
                    for rect, name in button_positions:
                        if rect.collidepoint(event.pos):
                            if name == "backtrack_random":
                                self.algorithm_name = "Backtracking"
                                self.start_time = time.time()
                                self.solution = self.backtracking_search_solve(self.start_state.copy())
                                self.end_time = time.time()
                                execution_time = self.end_time - self.start_time
                                if self.solution is None:
                                    print("❌ Không tìm được lời giải bằng Backtracking.")
                                else:
                                    print("✅ Backtracking tìm thấy đường đi.")
                                    self.solving = True
                                    self.step_count = 0
                            if name == "Reset":
                                # RESET
                                self.start_state = self.original_state.copy()
                                self.solving = False
                                self.solution = []
                                self.step_count = 0
                                self.algorithm_name = None
                                self.start_time = 0
                                self.end_time = 0
                                execution_time = 0
                            if name == "exit_app":
                                self.running = False
                            if name == "speed_cycle":
                                self.speed_index = (self.speed_index + 1) % len(self.speed_levels)
                                self.step_delay = self.speed_levels[self.speed_index]
                                print(f"🕐 Tốc độ mới: {self.speed_names[self.speed_index]}")
                            else:
                                # Chọn thuật toán
                                try:
                                    # Bắt đầu giải
                                    self.algorithm_name = name
                                    self.start_time = time.time()
                                    
                                    # Gọi thuật toán tương ứng
                                    if name in self.ALGORITHMS:
                                        algorithm = self.ALGORITHMS[name]
                                        if algorithm != "reset":
                                            self.solution = algorithm(self.start_state.copy())
                                            
                                            # Kết thúc và lưu thời gian thực thi
                                            self.end_time = time.time()
                                            execution_time = self.end_time - self.start_time
                                            
                                            # Kiểm tra kết quả
                                            if self.solution is None:
                                                print(f"{name} bị bế tắc hoặc không tìm được đường đi.")
                                            else:
                                                print(f"{name} => solution = {self.solution}")
                                                print(f"Thời gian thực thi: {execution_time:.4f} giây")
                                                
                                                # Chuẩn bị cho việc giải từng bước
                                                self.solving = True
                                                self.step_count = 0
                                except Exception as e:
                                    print(f"Lỗi khi chạy thuật toán {name}: {e}")
            
            # Giải từng bước
            if self.solving and self.solution:
                if self.step_count < len(self.solution):
                    zero_idx, move_idx = self.solution[self.step_count]

                    # ⭐ Lưu lại bước đi hiện tại để highlight
                    self.current_move = (zero_idx, move_idx)

                    # Thực hiện di chuyển
                    self.start_state[zero_idx], self.start_state[move_idx] = self.start_state[move_idx], self.start_state[zero_idx]
                    self.step_count += 1
                    pygame.time.delay(self.step_delay)
                else:
                    self.solving = False
                    self.current_move = None  # ✅ Sau khi giải xong thì bỏ highlight

            # Cập nhật màn hình
            pygame.display.flip()
            self.clock.tick(100)

        # Thoát pygame
        pygame.quit()

def main():
    """Hàm chính để chạy ứng dụng"""
    solver = PuzzleSolver()
    solver.run()

if __name__ == "__main__":
    main()