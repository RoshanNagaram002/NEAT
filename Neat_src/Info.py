import numpy as np
from typing import List, Tuple
from queue import Queue
class Randomized_Info:
    def __init__(self):
        self.datalist = []
        self.dataset = set()
    
    def contains(self, key)-> bool:
        return key in self.dataset
    
    def get_random_element(self, weights = None):
        if weights == None:
            return np.random.choice(self.datalist)
        weights[-1] = 1 - np.sum(weights[0:-1])
        return np.random.choice(self.datalist, p=weights)
    
    def add(self, key) -> None:
        if key not in self.dataset:
            self.datalist.append(key)
            self.dataset.add(key)
        else:
            print("Key is already in dataset")
    
    def clear(self) -> None:
        self.datalist = []
        self.dataset = set()
    
    def get(self, index: int):
        return self.datalist[index]
    
    def remove(self, key):
        self.datalist.remove(key)
        self.dataset.remove(key)
    
    def custom_pop(self, index = None):
        if index == None:
            index = -1
        key = self.datalist.pop(index)
        self.dataset.remove(key)
        return key
    
    def replace(self, index, new):
        old = self.datalist[index]
        self.dataset.remove(old)
        self.datalist[index] = new
        self.dataset.add(new)
    
    def __len__(self):
        return len(self.datalist)
    
    def __str__(self):
        return str(self.datalist)

    def __iter__(self):
        return iter(self.datalist)
    
class Sorted_Randomized_Info(Randomized_Info):
    def __init__(self):
        super().__init__()

    def add(self, key):
        if key not in self.dataset:
            self.dataset.add(key)
            i = 0
            while i < len(self.datalist) and key > self.datalist[i]:
                i += 1
            self.datalist.insert(i, key)
        else:
            print("Key is already in dataset")

class ListDict(object):
    def __init__(self):
        self.item_to_position = {}
        self.items = []

    def add_item(self, item):
        if item in self.item_to_position:
            return
        self.items.append(item)
        self.item_to_position[item] = len(self.items)-1

    def remove_item(self, item):
        position = self.item_to_position.pop(item)
        last_item = self.items.pop()
        if position != len(self.items):
            self.items[position] = last_item
            self.item_to_position[last_item] = position

    def choose_random_item(self):
        index = np.random.randint(len(self.items))
        return self.items[index]
    
    def __contains__(self, item):
        return item in self.item_to_position

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

# Assume a Network is all sigmoided for now, need to change this later
class Network():
    def __init__(self, nodes : List[int], edges : List[Tuple[int, int, float, bool]], input_size, output_size, hidden_act = lambda x: 1 / (1 + np.exp(-1 *  x))):
        self.nodes = nodes
        self.connections = edges
        self.num_input_nodes = input_size
        self.num_output_nodes = output_size
        self.hidden_act = hidden_act
    

    def get_output(self, input):
        assert len(input) == self.num_input_nodes

        adj_dict = {}
        incoming_counts = {}
        node_to_values = {}

        for node_id in self.nodes:
            adj_dict[node_id] = []
            incoming_counts[node_id] = 0
            node_to_values[node_id] = 0
                
        for con in self.connections:
            left, right, weight, is_enabled = con
            if is_enabled:
                adj_dict[left].append((right, weight))
                incoming_counts[right] += 1
        
        q = Queue()

        # Fill in the input_values and add into the stack
        for i in range(self.num_input_nodes):
            node_to_values[i] = input[i]
            q.put(i)
        
        for i in range(self.num_input_nodes, self.num_input_nodes + self.num_output_nodes):
            assert len(adj_dict[i]) == 0

        while not q.empty():
            node_id = q.get()
            assert node_id >= 0
            if node_id >= self.num_input_nodes:
                node_to_values[node_id] = self.hidden_act(node_to_values[node_id])
            
            for neighbor_id, weight in adj_dict[node_id]:
                incoming_counts[neighbor_id] -= 1
                node_to_values[neighbor_id] += (node_to_values[node_id] * weight)
                # If neighbor is fully visted and neighbor is not an ouptut node
                if incoming_counts[neighbor_id] == 0 and (not(neighbor_id >= self.num_input_nodes and neighbor_id < self.num_input_nodes + self.num_output_nodes)):
                    q.put(neighbor_id)
        
        # Apply the activation function to the outputs
        for output_id in range(self.num_input_nodes, self.num_input_nodes + self.num_output_nodes):
            node_to_values[output_id] = self.hidden_act(node_to_values[output_id])

        return [node_to_values[i] for i in range(self.num_input_nodes, self.num_input_nodes + self.num_output_nodes)]

