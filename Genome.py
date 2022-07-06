from Info import Randomized_Info, Sorted_Randomized_Info
import Neat
import numpy as np
from Components import Node, Connection
class Genome:
    def __init__(self, neat: Neat.Neat, num_input_nodes: int, num_output_nodes: int):
        self.nodes = Randomized_Info()
        self.connections = Sorted_Randomized_Info()
        self.layers = []
        self.neat = neat
        self.num_input_nodes = num_input_nodes
        self.num_output_nodes = num_output_nodes

        self.create_base_genome()
    
    def create_base_genome(self):
        input_layer = []
        for i in range(self.num_input_nodes):
            self.nodes.add(Node(i, act_func = lambda x: x, is_input= True))
            input_layer.append(i)
        
        output_layer = []
        for i in range(self.num_input_nodes, self.num_input_nodes + self.num_output_nodes):
            self.nodes.add(Node(i, is_output=True))
            output_layer.append(i)
        
        self.layers.append(input_layer)
        self.layers.append(output_layer)

    
    def get_distance(self, g2)-> float:
        return 0.0
    
    def mutate(self)-> None:
        return
    
    def cross_over(self, g2):
        return None
    
    def add_node(self)-> None:
        return
    
    def add_link(self)-> None:
        return
    
    def change_weight(self)-> None:
        return
    
    def shift_weight(self)-> None:
        return 
    
    def toggle_enable(self)-> None:
        return




    
    