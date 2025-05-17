
def generate_fixed_puzzle(self) -> List[int]:
        """Tạo trạng thái ban đầu của puzzle"""
        return [2,3,6,1,5,0,4,7,8]

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