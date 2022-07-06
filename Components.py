import numpy as np
class Node:
    def __init__(self, node_id : int, act_func = lambda x: 1 / (1 + np.exp(-1 *  x)), is_input: bool = False, is_output: bool = False):
        self.node_id = node_id
        self.act_func = act_func
        self.is_input = is_input
        self.is_output = is_output

    def __eq__(self, other):
        return self.node_id == other.node_id
    
    def __ne__(self, other):
        return self.node_id != other.node_id
    
    def __lt__(self, other):
        return self.node_id < other.node_id
    
    def __gt__(self, other):
        return self.node_id > other.node_id
    
    def __le__(self, other):
        return self.node_id <= other.node_id
    
    def __ge__(self, other):
        return self.node_id >= other.node_id
    
    def __hash__(self):
        return self.node_id



class Connection:
    def __init__(self, innovation_id: int, left: int, right: int, weight: float, is_enabled: bool) -> None:
        self.innovation_id = innovation_id
        self.left = left
        self.right = right
        self.weight = weight
        self.is_enabled = is_enabled

        # Add eq, not_eq, lt, gt, and hashfunc 