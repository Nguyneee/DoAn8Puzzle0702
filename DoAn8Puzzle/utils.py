from typing import List, Tuple

def generate_fixed_puzzle() -> List[int]:
    return [2,3,6,1,5,0,4,7,8]
# [2,6,5,0,8,7,4,3,1]
# [2,3,6,1,5,0,4,7,8]
def manhattan_distance(state: List[int]) -> int:
    goal_pos = {val: (idx % 3, idx // 3) for idx, val in enumerate(range(1, 9))}
    goal_pos[0] = (2, 2)
    return sum(
        abs((state.index(val) % 3) - goal_pos[val][0]) +
        abs((state.index(val) // 3) - goal_pos[val][1])
        for val in state if val != 0
    )
import random

def generate_random_state():
    """Tạo trạng thái ngẫu nhiên hợp lệ cho 8-puzzle"""
    state = list(range(9))
    while True:
        random.shuffle(state)
        if is_solvable(state):
            return state
def get_next_states(state: List[int]) -> List[Tuple[List[int], Tuple[int, int]]]:
    zero_idx = state.index(0)
    moves = [-3, 3, -1, 1]
    next_states = []
    for move in moves:
        new_idx = zero_idx + move
        if 0 <= new_idx < 9 and (
            (move in [-1, 1] and zero_idx // 3 == new_idx // 3) or (move in [-3, 3])
        ):
            new_state = state.copy()
            new_state[zero_idx], new_state[new_idx] = new_state[new_idx], new_state[zero_idx]
            next_states.append((new_state, (zero_idx, new_idx)))
    return next_states

def is_solvable(state: List[int]) -> bool:
    inversions = 0
    for i in range(len(state)):
        if state[i] == 0:
            continue
        for j in range(i + 1, len(state)):
            if state[j] != 0 and state[i] > state[j]:
                inversions += 1
    return inversions % 2 == 0