from collections import deque
import heapq
import random
import math
import time
from .utils import generate_random_state, manhattan_distance
from heapq import heappop, heappush
from .utils import is_solvable
import pygame

# Hàm giải thuật BFS (Breadth-First Search): tìm kiếm theo chiều rộng, mở rộng tất cả các trạng thái cùng một mức độ trước khi chuyển sang mức độ tiếp theo
def bfs_solve(start_state):
    return generic_solve(start_state, queue=deque([(start_state, [])]), pop_method='popleft')

# Hàm giải thuật DFS (Depth-First Search): tìm kiếm theo chiều sâu, mở rộng các trạng thái theo chiều sâu trước khi quay lại
def dfs_solve(start_state, max_depth=100):
    stack = [(start_state, [], 0)]  # Thêm một giá trị depth vào mỗi phần tử
    visited = set()
    visited.add(tuple(start_state))

    while stack:
        state, path, depth = stack.pop()

        if state == list(range(1, 9)) + [0]:
            return path

        if depth >= max_depth:  # Nếu chiều sâu vượt quá max_depth thì tiếp tục
            continue

        zero_idx = state.index(0)  
        moves = [-3, 3, -1, 1]  

        # Generate next states
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
                    stack.append((new_state, path + [(zero_idx, new_idx)], depth + 1))  # Cập nhật chiều sâu

    return None


# Hàm giải thuật Generic Solve: hàm tổng quát cho các thuật toán tìm kiếm khác nhau
def generic_solve(start_state, queue, pop_method='pop', is_priority=False):
    goal_state = list(range(1, 9)) + [0]
    visited = set()
    visited.add(tuple(start_state))

    while queue:
        if is_priority:
            _, g, state, path = heapq.heappop(queue)
        elif pop_method == 'heappop':
            _, state, path = heapq.heappop(queue)
        else:
            if pop_method == 'pop':
                state, path = queue.pop()
            else:
                state, path = queue.popleft()

        if state == goal_state:
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

                    if is_priority:
                        h = manhattan_distance(new_state)
                        new_g = g + 1
                        f = new_g + h
                        heapq.heappush(queue, (f, new_g, new_state, path + [(zero_idx, new_idx)]))
                    elif pop_method == 'heappop':
                        heapq.heappush(queue, (manhattan_distance(new_state), new_state, path + [(zero_idx, new_idx)]))
                    else:
                        queue.append((new_state, path + [(zero_idx, new_idx)]))

    return None

# Hàm giải thuật UCS (Uniform Cost Search): mở rộng các trạng thái theo thứ tự tổng chi phí nhỏ nhất từ trạng thái ban đầu đến trạng thái hiện tại.
def ucs_solve(start_state):
    # Sử dụng generic_solve với hàng đợi ưu tiên theo chi phí
    goal_state = list(range(1, 9)) + [0]
    visited = set()
    visited.add(tuple(start_state))  # Thêm trạng thái ban đầu vào tập đã duyệt
    queue = [(0, start_state, [])]  # (chi phí, trạng thái, đường đi)
    
    while queue:
        cost, state, path = heapq.heappop(queue)
        
        if state == goal_state:
            return path
        
        zero_idx = state.index(0)
        moves = [-3, 3, -1, 1]
        
        for move in moves:
            new_idx = zero_idx + move
            if 0 <= new_idx < 9 and ((move in [-1, 1] and zero_idx // 3 == new_idx // 3) or (move in [-3, 3])):
                new_state = state[:]
                new_state[zero_idx], new_state[new_idx] = new_state[new_idx], new_state[zero_idx]
                
                if tuple(new_state) not in visited:
                    visited.add(tuple(new_state))
                    # Trong UCS, chi phí là số bước đã đi
                    heapq.heappush(queue, (cost + 1, new_state, path + [(zero_idx, new_idx)]))
    
    return None

# Hàm giải thuật Greedy: mở rộng các trạng thái theo thứ tự ưu tiên dựa trên heuristic (ở đây là khoảng cách Manhattan)
def greedy_solve(start_state):
    return generic_solve(start_state, queue=[(manhattan_distance(start_state), start_state, [])], pop_method='heappop')

# Hàm giải thuật tìm kiếm sâu dần lặp IDDFS (Iterative Deepening Depth-First Search): tìm kiếm theo chiều sâu với giới hạn độ sâu tăng dần
def iddfs_solve(start_state):
    goal_state = list(range(1, 9)) + [0] # Trạng thái đích (1,2,3,4,5,6,7,8,0)

    # Hàm dls (Depth-Limited Search): tìm kiếm theo chiều sâu với giới hạn độ sâu
    def dls(state, path, depth_limit, visited):
        if state == goal_state:
            return path
        if len(path) >= depth_limit:
            return None

        zero_idx = state.index(0)
        moves = [-3, 3, -1, 1]  # Lên, Xuống, Trái, Phải
        next_states = []

        for move in moves:
            new_idx = zero_idx + move
            if 0 <= new_idx < 9 and (
                (move in [-1, 1] and zero_idx // 3 == new_idx // 3) or
                (move in [-3, 3])
            ):
                new_state = state[:]
                new_state[zero_idx], new_state[new_idx] = new_state[new_idx], new_state[zero_idx]

                if tuple(new_state) not in visited:
                    next_states.append((new_state, path + [(zero_idx, new_idx)]))

        # Ưu tiên trạng thái gần lời giải hơn bằng Manhattan Distance để giảm số bước lặp không cần thiết
        next_states.sort(key=lambda x: manhattan_distance(x[0]))
        # Duyệt qua từng trạng thái tiếp theo
        for new_state, new_path in next_states:
            visited.add(tuple(new_state)) # Đánh dấu trạng thái đã duyệt
            result = dls(new_state, new_path, depth_limit, visited) # Gọi đệ quy với trạng thái mới
            if result is not None:
                return result
            visited.remove(tuple(new_state))  # Bỏ đánh dấu nếu không tìm thấy lời giải

        return None

    # Dùng Iterative Deepening với nhiều độ sâu khác nhau
    for depth_limit in range(5, 50, 5):  # Tăng dần giới hạn độ sâu
        visited = set([tuple(start_state)])
        solution = dls(start_state, [], depth_limit, visited)
        if solution is not None:
            return solution  # Nếu tìm thấy lời giải, trả về ngay

    return None  # Không tìm thấy lời giải

# Hàm giải thuật A* (A Star Search)
def astar_solve(start_state):
    return generic_solve(start_state, queue=[(manhattan_distance(start_state), 0, start_state, [])], pop_method='heappop', is_priority=True)

# Hàm giải thuật IDA* (Iterative Deepening A* Search)
def idastar_solve(start_state):
    goal_state = list(range(1, 9)) + [0]  # Trạng thái đích

    def search(state, path, g, threshold, visited):
        f = g + manhattan_distance(state)  # f(n) = g(n) + h(n)
        # Nếu f vượt ngưỡng, trả về ngưỡng mới
        if f > threshold:
            return f, None 
        if state == goal_state:
            return f, path  # Tìm thấy lời giải

        min_threshold = float('inf') # Ngưỡng nhỏ nhất
        zero_idx = state.index(0)
        moves = [-3, 3, -1, 1]

        for move in moves:
            new_idx = zero_idx + move
            if 0 <= new_idx < 9 and ((move in [-1, 1] and zero_idx // 3 == new_idx // 3) or (move in [-3, 3])):
                new_state = state[:]
                new_state[zero_idx], new_state[new_idx] = new_state[new_idx], new_state[zero_idx]

                if tuple(new_state) not in visited:
                    visited.add(tuple(new_state))
                    new_threshold, result = search(new_state, path + [(zero_idx, new_idx)], g + 1, threshold, visited)
                    visited.remove(tuple(new_state))
                    
                    if result is not None:
                        return new_threshold, result  # Nếu tìm thấy lời giải, trả về ngay
                    min_threshold = min(min_threshold, new_threshold)

        return min_threshold, None  # Trả về giá trị ngưỡng mới
     
    # Bắt đầu với ngưỡng ban đầu là heuristic của trạng thái ban đầu
    threshold = manhattan_distance(start_state)  # Bắt đầu với h(n)
    
    while True:
        visited = set([tuple(start_state)])
        threshold, solution = search(start_state, [], 0, threshold, visited) # Lặp lại tìm kiếm, tăng dần ngưỡng
        if solution is not None:
            return solution  # Nếu tìm thấy lời giải, trả về
        if threshold == float('inf'):
            return None  # Không tìm thấy lời giải

# Hàm giải thuật Hill Climbing: tìm kiếm theo chiều cao, mở rộng trạng thái tốt nhất tại mỗi bước
def hill_climbing_solve(start_state):
    goal_state = list(range(1, 9)) + [0]
    current_state = start_state[:]
    path = []
    
    while current_state != goal_state:
        # Tìm vị trí ô trống
        zero_idx = current_state.index(0)
        
        # Khởi tạo giá trị heuristic tốt nhất
        best_heuristic = manhattan_distance(current_state) # Tính toán heuristic cho trạng thái hiện tại
        best_move = None # Tìm bước đi tốt nhất
        
        # Các hướng di chuyển
        moves = [-3, 3, -1, 1]
        
        for move in moves:
            new_idx = zero_idx + move
            # Kiểm tra di chuyển hợp lệ
            if 0 <= new_idx < 9 and ((move in [-1, 1] and zero_idx // 3 == new_idx // 3) or (move in [-3, 3])):
                # Tạo trạng thái mới
                new_state = current_state[:]
                new_state[zero_idx], new_state[new_idx] = new_state[new_idx], new_state[zero_idx]
                
                # Tính heuristic của trạng thái mới
                new_heuristic = manhattan_distance(new_state)
                
                # Chọn trạng thái có heuristic tốt hơn (nhỏ hơn)
                if new_heuristic < best_heuristic:
                    best_heuristic = new_heuristic
                    best_move = (zero_idx, new_idx)
        
        # Nếu không tìm được bước đi tốt hơn, kết thúc
        if best_move is None:
            return None
        
        # Thực hiện di chuyển   
        zero_idx, new_idx = best_move
        current_state[zero_idx], current_state[new_idx] = current_state[new_idx], current_state[zero_idx]
        path.append(best_move)
    
    return path

# Hàm giải thuật Steepest Ascent Hill Climbing: tìm kiếm theo chiều cao với bước đi tốt nhất tại mỗi bước
def steepest_ascent_hill_climbing_solve(start_state):
    goal_state = list(range(1, 9)) + [0]
    current_state = start_state[:]
    path = []
    
    while current_state != goal_state:
        # Tìm vị trí ô trống
        zero_idx = current_state.index(0)
        
        # Khởi tạo giá trị heuristic tốt nhất
        best_heuristic = manhattan_distance(current_state)
        best_moves = []
        
        # Các hướng di chuyển
        moves = [-3, 3, -1, 1]
        
        for move in moves:
            new_idx = zero_idx + move
            # Kiểm tra di chuyển hợp lệ
            if 0 <= new_idx < 9 and ((move in [-1, 1] and zero_idx // 3 == new_idx // 3) or (move in [-3, 3])):
                # Tạo trạng thái mới
                new_state = current_state[:]
                new_state[zero_idx], new_state[new_idx] = new_state[new_idx], new_state[zero_idx]
                
                # Tính heuristic của trạng thái mới
                new_heuristic = manhattan_distance(new_state)
                
                # Lưu tất cả các bước đi có heuristic tốt nhất
                if new_heuristic < best_heuristic:
                    best_heuristic = new_heuristic
                    best_moves = [(zero_idx, new_idx)]
                elif new_heuristic == best_heuristic:
                    best_moves.append((zero_idx, new_idx))
        
        # Nếu không tìm được bước đi tốt hơn, kết thúc
        if not best_moves:
            return None
        
        # Chọn ngẫu nhiên một trong các bước đi tốt nhất nếu có nhiều hơn một
        zero_idx, new_idx = best_moves[0] if len(best_moves) == 1 else best_moves[len(best_moves) // 2]  
        
        # Thực hiện di chuyển   
        current_state[zero_idx], current_state[new_idx] = current_state[new_idx], current_state[zero_idx]
        path.append((zero_idx, new_idx))
    
    return path

# Hàm giải thuật Hill Climbing với ngẫu nhiên
def stochastic_hill_climbing_solve(start_state):
    goal_state = list(range(1, 9)) + [0]
    current_state = start_state[:]
    path = []

    while current_state != goal_state:
        # Tìm vị trí ô trống
        zero_idx = current_state.index(0)

        # Tạo danh sách các trạng thái lân cận
        neighbors = []
        moves = [-3, 3, -1, 1]  # Lên, Xuống, Trái, Phải

        for move in moves:
            new_idx = zero_idx + move
            # Kiểm tra di chuyển hợp lệ
            if 0 <= new_idx < 9 and ((move in [-1, 1] and zero_idx // 3 == new_idx // 3) or (move in [-3, 3])):
                # Tạo trạng thái mới
                new_state = current_state[:]
                new_state[zero_idx], new_state[new_idx] = new_state[new_idx], new_state[zero_idx]
                neighbors.append((new_state, (zero_idx, new_idx)))

        # Lọc các trạng thái lân cận tốt hơn
        better_neighbors = [
            (state, move) for state, move in neighbors if manhattan_distance(state) < manhattan_distance(current_state)
        ]

        # Nếu không có trạng thái tốt hơn, dừng lại
        if not better_neighbors:
            return None

        # Chọn ngẫu nhiên một trạng thái tốt hơn
        next_state, move = random.choice(better_neighbors)

        # Cập nhật trạng thái hiện tại
        current_state = next_state
        path.append(move)

    return path

# Hàm giải thuật Simulated Annealing
def simulated_annealing_solve(start_state):
    state = start_state[:]
    path = []
    goal = list(range(1, 9)) + [0]
    T = 150.0 # Nhiệt độ ban đầu
    alpha = 0.99 # Hệ số làm mát
    min_temp = 0.1 # Nhiệt độ tối thiểu

    while True:
        if state == goal:
            return path

        zero_idx = state.index(0)
        moves = [-3, 3, -1, 1]
        best_h = manhattan_distance(state)
        best_move = None
        best_state = None

        neighbors = []

        for move in moves:
            new_idx = zero_idx + move
            if 0 <= new_idx < 9 and (
                (move in [-1, 1] and zero_idx // 3 == new_idx // 3) or (move in [-3, 3])
            ):
                temp = state[:]
                temp[zero_idx], temp[new_idx] = temp[new_idx], temp[zero_idx]
                h = manhattan_distance(temp)
                neighbors.append((temp, (zero_idx, new_idx), h))

                if h < best_h:
                    best_h = h
                    best_move = move
                    best_state = temp

        if best_move:
            # Có hướng tốt hơn → đi theo HC
            state = best_state
            path.append((zero_idx, zero_idx + best_move))
        else:
            # Không có hướng đi tốt hơn → dùng SA để thoát
            if not neighbors:
                break
            next_state, move, h = random.choice(neighbors)
            delta_e = manhattan_distance(state) - h # Tính toán độ thay đổi heuristic
            if delta_e > 0 or random.random() < math.exp(delta_e / T): # Xác suất chấp nhận trạng thái xấu hơn
                state = next_state
                path.append(move)

            T *= alpha # Giảm nhiệt độ dần theo thời gia/n
            if T < min_temp:
                break

    return path if state == goal else None

# Hàm giải thuật Beam Search
def beam_search_solve(start_state, beam_width=2):
    goal_state = list(range(1, 9)) + [0]
    queue = [(manhattan_distance(start_state), start_state, [])]
    visited = set()

    while queue:
        # Giữ lại beam_width trạng thái tốt nhất
        next_level = []

        for _, state, path in queue: #_ là giá trị heuristic cần dùng đến
            if state == goal_state:
                return path

            visited.add(tuple(state))
            zero_idx = state.index(0)
            moves = [-3, 3, -1, 1]

            for move in moves:
                new_idx = zero_idx + move
                if 0 <= new_idx < 9 and (
                    (move in [-1, 1] and zero_idx // 3 == new_idx // 3) or (move in [-3, 3])
                ):
                    new_state = state[:]
                    new_state[zero_idx], new_state[new_idx] = new_state[new_idx], new_state[zero_idx]

                    if tuple(new_state) not in visited:
                        new_path = path + [(zero_idx, new_idx)]
                        h = manhattan_distance(new_state)
                        heappush(next_level, (h, new_state, new_path))

        # Chọn beam_width trạng thái tốt nhất để tiếp tục
        queue = [heappop(next_level) for _ in range(min(beam_width, len(next_level)))]

    return None  # Không tìm thấy lời giải

def and_or_search(max_depth=20):
    """
    AND-OR Search: Một thuật toán tìm kiếm cho môi trường phức tạp trong 8-puzzle.
    Thuật toán sẽ tạo một kế hoạch có thể giải quyết mọi khả năng xảy ra trong môi trường.
    """
    import random
    import sys
    from .utils import is_solvable, manhattan_distance
    
    # Tăng giới hạn đệ quy để tránh lỗi stack overflow
    sys.setrecursionlimit(10000)

    # Trạng thái đích
    goal_state = list(range(1, 9)) + [0]
    
    # Tạo một trạng thái ban đầu ngẫu nhiên có thể giải được
    while True:
        start_state = list(random.sample(range(9), 9))
        if is_solvable(start_state) and start_state != goal_state:
            break
    
    # Lưu tất cả các trạng thái đã thăm để tránh lặp vô hạn
    visited = set()
    visited.add(tuple(start_state))
    
    # Lưu đường đi để hiển thị
    solution_path = [start_state]
    best_path = None
    best_path_length = float('inf')
    
    def get_valid_moves(state):
        """Tìm các nước đi hợp lệ từ trạng thái hiện tại"""
        zero_idx = state.index(0)
        valid_moves = []
        
        # Kiểm tra 4 hướng di chuyển: lên, xuống, trái, phải
        if zero_idx >= 3:  # Có thể đi lên
            valid_moves.append((zero_idx, zero_idx - 3))
        if zero_idx < 6:  # Có thể đi xuống
            valid_moves.append((zero_idx, zero_idx + 3))
        if zero_idx % 3 > 0:  # Có thể đi trái
            valid_moves.append((zero_idx, zero_idx - 1))
        if zero_idx % 3 < 2:  # Có thể đi phải
            valid_moves.append((zero_idx, zero_idx + 1))
            
        return valid_moves
    
    def apply_move(state, move):
        """Áp dụng nước đi và trả về trạng thái mới"""
        zero_idx, swap_idx = move
        new_state = state.copy()
        new_state[zero_idx], new_state[swap_idx] = new_state[swap_idx], new_state[zero_idx]
        return new_state
    
    def dfs_with_limit(state, depth, path):
        """Tìm kiếm theo chiều sâu với giới hạn độ sâu"""
        nonlocal best_path, best_path_length
        
        # Nếu đạt trạng thái đích
        if state == goal_state:
            if len(path) < best_path_length:
                best_path = path.copy()
                best_path_length = len(path)
            return True
        
        # Nếu vượt quá độ sâu tối đa
        if depth >= max_depth:
            return False
        
        # Lấy các nước đi hợp lệ và sắp xếp theo heuristic (tốt nhất trước)
        valid_moves = get_valid_moves(state)
        
        # Thử từng nước đi
        for move in valid_moves:
            new_state = apply_move(state, move)
            tuple_state = tuple(new_state)
            
            # Nếu trạng thái mới chưa thăm
            if tuple_state not in visited:
                visited.add(tuple_state)
                
                # Thêm vào đường đi
                path.append(move)
                solution_path.append(new_state)
                
                # Tiếp tục tìm kiếm từ trạng thái mới
                if dfs_with_limit(new_state, depth + 1, path):
                    return True
                
                # Quay lui nếu không tìm thấy đường đi
                path.pop()
                solution_path.pop()
        
        return False
    
    # Bắt đầu tìm kiếm với chiều sâu tăng dần để đảm bảo tìm được đường đi ngắn nhất
    found = False
    for limit in range(5, max_depth + 5, 5):
        # Reset để thử với độ sâu mới
        visited = set()
        visited.add(tuple(start_state))
        solution_path = [start_state]
        
        # Thử tìm kiếm với giới hạn mới
        if dfs_with_limit(start_state, 0, []):
            found = True
            print(f"Tìm thấy đường đi với độ sâu {limit}")
            break
    
    if found and best_path:
        return {
            "start": start_state,
            "path": solution_path,
            "moves": best_path
        }
    else:
        return {
            "start": start_state,
            "path": [start_state],
            "moves": None
        }
    

from itertools import permutations
from collections import deque

def no_observation_search(start_state=None):
    goal_state = tuple([1, 2, 3, 4, 5, 6, 7, 8, 0])
    print("📥 Bắt đầu no_observation_search()")

    # --- Kiểm tra solvability ---
    def is_solvable(state):
        inv = 0
        for i in range(8):
            for j in range(i+1, 9):
                if state[i] and state[j] and state[i] > state[j]:
                    inv += 1
        return inv % 2 == 0

    # --- 1) Tạo belief ban đầu ---
    if start_state:
        belief0 = {tuple(start_state)}
        print(f"🔍 Trạng thái đầu vào: {start_state}")

    else:
        belief0 = set(filter(is_solvable, permutations(range(9))))
        print(f"🔁 Khởi tạo belief với {len(belief0)} trạng thái có thể giải được")


    queue = deque([(belief0, [])])
    visited = set()
    expansions = 0

    moves = {
        'UP':    (-1,  0),
        'DOWN':  ( 1,  0),
        'LEFT':  ( 0, -1),
        'RIGHT': ( 0,  1)
    }

    while queue:
        belief, path = queue.popleft()
        key = frozenset(belief)
        if key in visited:
            continue
        visited.add(key)
        expansions += 1

        if all(state == goal_state for state in belief):
            print("✅ Tìm thấy lời giải!")
            print(f"🪜 Hành động: {path}")
            return path

        for action, (dr, dc) in moves.items():
            new_belief = set()
            ok = True
            for st in belief:
                zero = st.index(0)
                r, c = divmod(zero, 3)
                nr, nc = r+dr, c+dc
                if 0 <= nr < 3 and 0 <= nc < 3:
                    idx2 = nr*3 + nc
                    lst  = list(st)
                    lst[zero], lst[idx2] = lst[idx2], lst[zero]
                    new_belief.add(tuple(lst))
                else:
                    ok = False
                    break
            if ok and new_belief:
                queue.append((new_belief, path + [(zero, idx2)]))

    return None


# Hàm giải thuật Partial Observable Search (Belief State Search): tìm kiếm với trạng thái "quan sát được" một số ô trên bảng (1,2,3)
def partial_observable_search(start_state):
    from collections import deque
    goal_state = list(range(1, 9)) + [0]
    observed_indices = [0, 1, 2]  # Các ô 0,1,2 đã biết chắc

    # Hàm kiểm tra trạng thái có thể giải được hay không - số nghịch thể là chẵn thì có thể giải được và ngược lại
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

    visited = set() # Tập hợp các trạng thái đã duyệt để tránh lặp lại
    queue = deque([(start_state, [])]) # Hàng đợi lưu trữ các trạng thái cần duyệt

    while queue:
        current_state, path = queue.popleft() # Lấy trạng thái đầu tiên trong hàng đợi

        # Kiểm tra nếu đã đạt đích
        if current_state == goal_state:
            return path

        zero_idx = current_state.index(0)
        moves = [-3, 3, -1, 1]  # Lên, Xuống, Trái, Phải

        for move in moves:
            new_idx = zero_idx + move

            # Kiểm tra nước đi hợp lệ
            if 0 <= new_idx < 9 and (
                (move in [-1, 1] and zero_idx // 3 == new_idx // 3) or
                (move in [-3, 3])
            ):
                # Không cho swap làm ảnh hưởng đến ô 0,1,2
                if new_idx in observed_indices:
                    continue  # Bỏ qua nước đi nếu làm thay đổi ô 1,2,3 cố định

                # Thêm trạng thái mới vào hàng đợi
                new_state = current_state[:]
                new_state[zero_idx], new_state[new_idx] = new_state[new_idx], new_state[zero_idx]

                if tuple(new_state) not in visited:
                    visited.add(tuple(new_state))
                    queue.append((new_state, path + [(zero_idx, new_idx)]))

    return None

# Danh sách các bước di chuyển hợp lệ
def get_next_states(state):
    moves = [-3, 3, -1, 1]  # Các di chuyển: lên (-3), xuống (3), trái (-1), phải (1)
    next_states = []
    zero_idx = state.index(0)  # Tìm vị trí của ô 0

    for move in moves:
        new_idx = zero_idx + move

        # Kiểm tra xem ô mới có hợp lệ không (không ra ngoài ma trận 3x3)
        if 0 <= new_idx < 9 and (
            (move in [-1, 1] and zero_idx // 3 == new_idx // 3) or  # Không di chuyển sang ô ngoài cùng hàng
            (move in [-3, 3])  # Di chuyển lên xuống
        ):
            new_state = state[:]
            new_state[zero_idx], new_state[new_idx] = new_state[new_idx], new_state[zero_idx]  # Hoán đổi ô 0 với ô kế tiếp
            next_states.append((new_state, (zero_idx, new_idx)))

    return next_states
def find_solution_path(start_state, goal_state=[1, 2, 3, 4, 5, 6, 7, 8, 0]):
    """
    Tìm đường đi từ trạng thái bắt đầu đến trạng thái đích bằng thuật toán A*
    Trả về danh sách các tuple (zero_idx, swap_idx) biểu diễn các bước di chuyển
    """
    from heapq import heappush, heappop
    from DoAn8Puzzle.utils import manhattan_distance, is_solvable
    
    # Kiểm tra xem có thể giải được không
    from DoAn8Puzzle.utils import is_solvable
    if not is_solvable(start_state) and is_solvable(goal_state):
        print("Trạng thái không thể giải được")
        return []

    visited = set()
    queue = [(manhattan_distance(start_state), 0, start_state, [])]  # (f, g, state, path)
    
    while queue:
        _, g, state, path = heappop(queue)
        
        if state == goal_state:
            return path
        
        state_tuple = tuple(state)
        if state_tuple in visited:
            continue
            
        visited.add(state_tuple)
        zero_idx = state.index(0)
        
        # Các nước đi có thể: lên, xuống, trái, phải
        moves = [
            (-3, "up"),    # Lên
            (3, "down"),   # Xuống
            (-1, "left"),  # Trái
            (1, "right")   # Phải
        ]
        
        for move, _ in moves:
            new_idx = zero_idx + move
            
            # Kiểm tra nước đi hợp lệ
            if (
                0 <= new_idx < 9 and  # Trong phạm vi bảng 3x3
                (move != -1 or zero_idx % 3 != 0) and  # Không vượt trái khi ở cột trái nhất
                (move != 1 or zero_idx % 3 != 2) and   # Không vượt phải khi ở cột phải nhất
                (move != -3 or zero_idx >= 3) and      # Không vượt lên khi ở hàng trên cùng
                (move != 3 or zero_idx < 6)            # Không vượt xuống khi ở hàng dưới cùng
            ):
                new_state = state.copy()
                # Hoán đổi vị trí
                new_state[zero_idx], new_state[new_idx] = new_state[new_idx], new_state[zero_idx]
                
                # Chỉ thêm vào hàng đợi nếu trạng thái mới chưa được duyệt
                if tuple(new_state) not in visited:
                    # Tính toán f = g + h với g là số bước đi và h là khoảng cách Manhattan
                    new_g = g + 1
                    new_f = new_g + manhattan_distance(new_state)
                    heappush(queue, (new_f, new_g, new_state, path + [(zero_idx, new_idx)]))
    
    # Nếu không tìm thấy giải pháp
    return []

#n
def genetic_algorithm_solve(start_state, population_size=200, max_generations=500, mutation_rate=0.1, timeout=50):
    goal_state = list(range(1, 9)) + [0]
    if start_state == goal_state:
        return []

    if not is_solvable(start_state):
        print("Trạng thái không thể giải được!")
        return None

    # Các bước di chuyển: lên, xuống, trái, phải
    move_map = [-3, 3, -1, 1]

    # Hàm tạo cá thể mới bằng cách sinh ngẫu nhiên lengthh bước đi
    def create_individual(length=100):
        return [random.randint(0, 3) for _ in range(length)]

    # Áp dụng chuỗi bước đi lên trạng thái
    def apply_moves(state, moves):
        s = state[:]
        valid_path = [] # Lưu lại các bước đi hợp lệ
        last_move = None # Tránh lặp lại hướng ngược

        for move in moves:
            zero = s.index(0)
            new_zero = zero + move_map[move]

            # Không đi ngược lại bước trước
            if last_move is not None and abs(move_map[move]) == abs(move_map[last_move]):
                continue

            if 0 <= new_zero < 9:
                if move in [2, 3] and zero // 3 != new_zero // 3:
                    continue  # Tránh đi trái/phải mà vượt ra khỏi hàng
                s[zero], s[new_zero] = s[new_zero], s[zero]
                valid_path.append((zero, new_zero))
                last_move = move
        return s, valid_path
    # Hàm tính điểm fitness cho cá thể dựa vào hàm Manhattan
    # Càng gần goal(khoảng cách Manhattan càng nhỏ) thì điểm càng cao
    # Càng ngắn thì tốt hơn -> trừ điểm 0.1 cho mỗi bước đi
    def fitness(state, path):
        dist = manhattan_distance(state) 
        return 1000 - dist - 0.1 * len(path) # Trừ điểm cho mỗi bước đi
    
    # Hàm lai ghép 2 cá thể để tạo ra cá thể mới
    def crossover(p1, p2):
        point = random.randint(1, min(len(p1), len(p2)) - 1) # Chọn ngẫu nhiên điểm cắt của p1 để trộn với p2
        return p1[:point] + p2[point:]

    # Hàm đột biến cá thể với xác suất rate - tức thay đổi ngẫu nhiên một bước đi trong cá thể
    def mutate(ind, rate):
        return [random.randint(0, 3) if random.random() < rate else m for m in ind]

    # Khởi tạo quần thể ban đầu
    population = [create_individual() for _ in range(population_size)]
    # Biến theo dõi cá thể tốt nhất
    best_score = float('-inf')
    best_path = []

    start = time.time()
    for gen in range(max_generations):
        if time.time() - start > timeout:
            print("Hết thời gian!")
            break

        scored = []
        # Chạy mỗi bước lên start state, tính điểm và lưu lại -> đánh giá tất cả cá thể
        for ind in population:
            final_state, path = apply_moves(start_state, ind)
            score = fitness(final_state, path)
            scored.append((score, ind, path, final_state))
            if final_state == goal_state:
                print(f"Tìm thấy lời giải tại thế hệ {gen}")
                return path

        scored.sort(reverse=True)
        population = [ind for _, ind, _, _ in scored[:population_size // 4]]  #Giữ lại top 25% cá thể tốt nhất

        # Lai ghép và đột biến để tạo child
        while len(population) < population_size:
            p1 = random.choice(scored)[1]
            p2 = random.choice(scored)[1]
            child = mutate(crossover(p1, p2), mutation_rate)
            population.append(child)

        # Cập nhật cá thể tốt nhất
        if scored[0][0] > best_score:
            best_score = scored[0][0]
            best_path = scored[0][2]

        if gen % 10 == 0:
            print(f"🔁 Thế hệ {gen}, điểm tốt nhất: {int(best_score)}")

    print("Không tìm được trạng thái goal. Trả về đường đi tốt nhất.")
    return best_path if best_path else None

# Hàm giải thuật Q-Learning: giải 8-puzzle sử dụng thuật toán học tăng cường
def q_learning_solve(start_state, episodes=5000, alpha=0.1, gamma=0.9, epsilon=0.2):
    import random
    from collections import defaultdict

    goal_state = tuple([1, 2, 3, 4, 5, 6, 7, 8, 0])
    # Bước 1: Khởi tạo Q-table và điền các giá trị ban đầu
    Q = defaultdict(lambda: [0, 0, 0, 0])  # Q(s,a) với 4 hành động: up, down, left, right
    actions = [(-3, 0), (3, 1), (-1, 2), (1, 3)]  # (di chuyển, chỉ số hành động)

    # Hàm xác định hành động hợp lệ từ trạng thái hiện tại
    def get_valid_actions(state):
        zero = state.index(0)
        valid = []
        for move, idx in actions:
            new_zero = zero + move
            if 0 <= new_zero < 9:
                if abs(zero % 3 - new_zero % 3) + abs(zero // 3 - new_zero // 3) == 1:
                    valid.append((move, idx))
        return valid

    # Hàm hoán đổi vị trí của ô trống (0) với ô bên cạnh -> trả về trạng thái mới
    def step(state, move):
        zero = state.index(0)
        new_zero = zero + move
        new_state = list(state)
        new_state[zero], new_state[new_zero] = new_state[new_zero], new_state[zero]
        return tuple(new_state)

    # Bước 2: Vòng lặp học theo số lượng episode
    for ep in range(episodes):
        state = tuple(start_state)

        for _ in range(100):  # Tối đa 50 bước mỗi episode
            # Bước 3: Chọn tác nhân thực hiện hành động lên trạng thái s(k)
            valid = get_valid_actions(state)
            if not valid:
                break

            if random.random() < epsilon:
                move, a = random.choice(valid)
            else:
                best = max(valid, key=lambda m: Q[state][m[1]]) # Chọn hành động tốt nhất dựa trên Q-value
                move, a = best

            # Bước 5: chuyển sang trạng thái mới
            next_state = step(state, move)

            # Bước 4: tính phần thưởng
            reward = 100 if next_state == goal_state else -1

            # Bước 6: cập nhật Q-value theo công thức
            max_q_next = max(Q[next_state])
            Q[state][a] += alpha * (reward + gamma * max_q_next - Q[state][a])

            state = next_state

            # Bước 7: kết thúc nếu đến goal
            if state == goal_state:
                break

        # Bước 8: reset môi trường là implicit khi bắt đầu vòng lặp mới

    # Sau khi học xong, giải bằng cách dùng Q-value
    path = []
    state = tuple(start_state)
    visited = set()
    for _ in range(50):
        visited.add(state)
        valid = get_valid_actions(state)
        if not valid:
            break

        best = max(valid, key=lambda m: Q[state][m[1]])
        move, a = best
        zero = state.index(0)
        new_zero = zero + move
        path.append((zero, new_zero))
        state = step(state, move)
        if state in visited:
            break
        if state == goal_state:
            return path

    return path if state == goal_state else None



# # Hàm giải thuật TD Learning: giải 8-puzzle sử dụng thuật toán học tăng cường Temporal Difference
def td_learning_solve(start_state, episodes=5000, alpha=0.2, gamma=0.9, epsilon=0.3):
    import random
    from collections import defaultdict

    goal_state = tuple([1, 2, 3, 4, 5, 6, 7, 8, 0])
    
    # Khởi tạo bảng giá trị trạng thái V(s)
    V = defaultdict(float)
    # Trạng thái đích có giá trị cao nhất
    V[goal_state] = 100.0
    
    # Hàm xác định hành động hợp lệ từ trạng thái hiện tại
    def get_valid_actions(state):
        zero = state.index(0)
        valid = []
        # Các hướng di chuyển: lên (-3), xuống (3), trái (-1), phải (1)
        actions = [(-3, "up"), (3, "down"), (-1, "left"), (1, "right")]
        
        for move, direction in actions:
            new_idx = zero + move
            if 0 <= new_idx < 9:
                # Kiểm tra nước đi hợp lệ
                if (move == -1 and zero % 3 == 0) or (move == 1 and zero % 3 == 2):
                    continue  # Không đi ra ngoài hàng
                if (move == -3 and zero < 3) or (move == 3 and zero > 5):
                    continue  # Không đi ra ngoài cột
                valid.append((zero, new_idx, direction))
                
        return valid

    # Hàm áp dụng nước đi và tạo trạng thái mới
    def apply_move(state, move):
        zero_idx, new_idx, _ = move
        new_state = list(state)
        new_state[zero_idx], new_state[new_idx] = new_state[new_idx], new_state[zero_idx]
        return tuple(new_state)

    # Hàm chọn nước đi dựa trên epsilon-greedy
    def choose_action(state, epsilon):
        valid_moves = get_valid_actions(state)
        
        # Không có nước đi hợp lệ
        if not valid_moves:
            return None
        
        # Epsilon-greedy: khám phá vs khai thác
        if random.random() < epsilon:
            # Khám phá: chọn ngẫu nhiên một nước đi
            return random.choice(valid_moves)
        else:
            # Khai thác: chọn nước đi có giá trị cao nhất
            best_value = -float('inf')
            best_moves = []
            
            for move in valid_moves:
                next_state = apply_move(state, move)
                if V[next_state] > best_value:
                    best_value = V[next_state]
                    best_moves = [move]
                elif V[next_state] == best_value:
                    best_moves.append(move)
            
            # Chọn ngẫu nhiên trong số các nước đi tốt nhất
            return random.choice(best_moves)

    print(f"TD Learning: training with {episodes} episodes...")
    
    # Huấn luyện qua nhiều tập dữ liệu
    for episode in range(episodes):
        # Giảm dần epsilon để ưu tiên khai thác hơn khám phá
        current_epsilon = max(0.05, epsilon * (1 - episode / episodes))
        
        state = tuple(start_state)
        step_count = 0
        max_steps = 100  # Giới hạn số bước mỗi episode
        
        while state != goal_state and step_count < max_steps:
            # Chọn nước đi 
            move = choose_action(state, current_epsilon)
            if not move:
                break
                
            # Áp dụng nước đi để có trạng thái mới
            next_state = apply_move(state, move)
            
            # Tính toán phần thưởng: -1 cho mỗi bước, 100 nếu đạt đích
            reward = 100 if next_state == goal_state else -1
            
            # Cập nhật V(s) theo công thức TD(0): V(s) = V(s) + alpha * [R + gamma * V(s') - V(s)]
            td_target = reward + gamma * V[next_state]
            td_error = td_target - V[state]
            V[state] += alpha * td_error
            
            # Chuyển sang trạng thái kế tiếp
            state = next_state
            step_count += 1
        
        # In thông tin tiến độ
        if (episode + 1) % 500 == 0:
            print(f"Episode {episode + 1}/{episodes} completed")

    # Sau khi huấn luyện, sử dụng các giá trị đã học để tìm giải pháp
    print("Training complete. Finding solution path...")
    state = tuple(start_state)
    path = []
    visited = set([state])
    max_solution_steps = 50
    
    # Giảm epsilon xuống thấp để ưu tiên khai thác hơn khám phá
    solution_epsilon = 0.05
    
    for _ in range(max_solution_steps):
        if state == goal_state:
            print(f"Goal reached in {len(path)} steps!")
            return path
            
        # Chọn nước đi tốt nhất từ trạng thái hiện tại
        move = choose_action(state, solution_epsilon)
        if not move:
            print("No valid moves available")
            break
            
        # Lưu vào đường đi và cập nhật trạng thái
        zero_idx, new_idx, _ = move
        path.append((zero_idx, new_idx))
        
        # Cập nhật trạng thái
        state = apply_move(state, move)
        
        # Kiểm tra lặp vòng
        if state in visited:
            print("Loop detected, breaking")
            break
            
        visited.add(state)
    
    # Trả về đường đi nếu có hoặc None nếu không tìm được
    return path if path else None
def backtracking_search_solve( start_state, max_depth=30):
        goal = list(range(1, 9)) + [0]

        def is_complete(state):
            return state == goal

        def select_unassigned_variable(state):
            return [i for i in range(9) if state[i] != goal[i]]

        def order_domain_values(index):
            domain = list(range(9))
            random.shuffle(domain)
            return [i for i in domain if i != index]

        def recursive_backtracking(state, path, visited, depth):
            if depth > max_depth:
                return None
            if is_complete(state):
                return path

            key = tuple(state)
            if key in visited:
                return None
            visited.add(key)

            unassigned = select_unassigned_variable(state)
            if not unassigned:
                return None

            var = unassigned[0]
            for value in order_domain_values(var):
                new_state = state[:]
                new_state[var], new_state[value] = new_state[value], new_state[var]
                if new_state != state:
                    result = recursive_backtracking(new_state, path + [(var, value)], visited, depth + 1)
                    if result:
                        return result
            return None

        return recursive_backtracking(start_state[:], [], set(), 0)
def constraint_checking_solve( start_state):
        from collections import deque
        goal = list(range(1, 9)) + [0]
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
def ac3_solve( start_state):
        from collections import deque
        goal = list(range(1, 9)) + [0]
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