from Info import Randomized_Info, Sorted_Randomized_Info
import numpy as np
from Components import Node, Connection
from typing import List
class Genome:
    def __init__(self, neat, num_input_nodes: int, num_output_nodes: int):
        self.nodes = Randomized_Info()
        self.connections = Sorted_Randomized_Info()
        self.neat = neat
        self.num_input_nodes = num_input_nodes
        self.num_output_nodes = num_output_nodes
        self.fitness = None

        self.create_base_genome()
    
    def create_base_genome(self):
        for i in range(self.num_input_nodes):
            self.nodes.add(Node(i, act_func = lambda x: x, is_input= True))
        
        for i in range(self.num_input_nodes, self.num_input_nodes + self.num_output_nodes):
            self.nodes.add(Node(i, is_output=True))

    
    def get_distance(self, g2)-> float:
        c1 = self.neat.c1
        c2 = self.neat.c2
        c3 = self.neat.c3

        num_disjoint = 0
        num_excess = 0
        total_weight_difference = 0
        num_matching = 0

        N = max(len(self.connections), len(g2.connections))
        if N < 20:
            N = 1

        g1_pointer, g2_pointer = 0, 0
        while g1_pointer < len(self.connections) and g2_pointer < len(g2.connections):
            curr_g1_con, curr_g2_con = self.connections.get(g1_pointer), g2.connections.get(g2_pointer)
            if curr_g1_con == curr_g2_con:
                num_matching += 1
                total_weight_difference += abs(curr_g1_con.weight - curr_g2_con.weight)
                g1_pointer += 1
                g2_pointer += 1
            
            elif curr_g1_con < curr_g2_con:
                num_disjoint += 1
                g1_pointer += 1
            
            elif curr_g2_con < curr_g1_con:
                num_disjoint += 1
                g2_pointer += 1
        
        if g1_pointer < len(self.connections):
            num_excess = len(self.connections) - g1_pointer
        elif g2_pointer < len(g2.connections):
            num_excess = len(g2.connections) - g2_pointer
        
        return ((c1 * num_excess) / N) + ((c2 * num_disjoint) / N) + (c3 * (total_weight_difference / num_matching))

    def cross_over(self, g2):
        child_genome = Genome(self.neat, self.num_input_nodes, self.num_output_nodes)

        beta_genome, alpha_genome = None, None

        if self.fitness >= g2.fitness:
            beta_genome, alpha_genome = g2, self
        else:
            beta_genome, alpha_genome = self, g2
        beta_pointer, alpha_pointer = 0, 0

        inherited_nodes = Randomized_Info()
        inherited_connections = Sorted_Randomized_Info()
        
        while beta_pointer < len(beta_genome.connections) and alpha_pointer < len(alpha_genome.connections):
            curr_beta_con, curr_alpha_con = beta_genome.connections.get(beta_pointer), alpha_genome.connections.get(alpha_pointer)
            if curr_beta_con == curr_alpha_con:
                is_beta = np.random.choice((0, 1))
                if is_beta == 1:
                    inherited_connection = curr_beta_con.copy()
                else:
                    inherited_connection = curr_alpha_con.copy()

                inherited_connections.add(inherited_connection)
                left_node, right_node = inherited_connection.left, inherited_connection.right
                if not inherited_nodes.contains(left_node):
                    inherited_nodes.add(left_node)
                if not inherited_nodes.contains(right_node):
                    inherited_nodes.add(right_node)
                beta_pointer += 1
                alpha_pointer += 1
            
            elif curr_beta_con < curr_alpha_con:
                beta_pointer += 1
            
            elif curr_alpha_con < curr_beta_con:
                inherited_connection = curr_alpha_con.copy()

                inherited_connections.add(inherited_connection)
                left_node, right_node = inherited_connection.left, inherited_connection.right
                if not inherited_nodes.contains(left_node):
                    inherited_nodes.add(left_node)
                if not inherited_nodes.contains(right_node):
                    inherited_nodes.add(right_node)

                alpha_pointer += 1
        
        while alpha_pointer < len(alpha_genome.connections):
            curr_alpha_con = alpha_genome.connections.get(alpha_pointer)
            inherited_connection = curr_alpha_con.copy()

            inherited_connections.add(inherited_connection)
            left_node, right_node = inherited_connection.left, inherited_connection.right
            if not inherited_nodes.contains(left_node):
                inherited_nodes.add(left_node)
            if not inherited_nodes.contains(right_node):
                inherited_nodes.add(right_node)
            alpha_pointer += 1
        
        child_genome.connections = inherited_connections
        child_genome.nodes = inherited_nodes

        return child_genome
    
    def mutate(self)-> None:
        if np.random.random() <= self.neat.add_node_chance:
            self.add_node()
        if np.random.random() <= self.neat.add_link_chance:
            self.add_link()
        if np.random.random() <= self.neat.reset_chance:
            self.reset_weight()
        if np.random.random() <= self.neat.shift_chance:
            self.shift_weight()
        if np.random.random() <= self.neat.toggle_chance:
            self.toggle_enable()
        
    def add_node(self)-> None:
        rando_con = self.connections.get_random_element()

        split_node = self.neat.create_hidden_node(rando_con.left, rando_con.right)
        self.nodes.add(split_node)

        from_con = self.neat.create_hidden_connection(rando_con.left, split_node.node_id, 1, True)
        to_con = self.neat.create_hidden_connection(split_node.node_id, rando_con.right, rando_con.weight, True)

        rando_con.is_enabled = False

        self.connections.add(from_con)
        self.connections.add(to_con)
    
    def add_link(self)-> None:
        node_to_index = {self.nodes.datalist[i].node_id:i for i in range(len(self.nodes))}
        visited = [False for _ in range(len(self.nodes))]

        sorted_nodes = []
        incoming_counts = [0 for _ in range(len(self.nodes))]
        outgoing_edges = [[] for _ in range(len(self.nodes))]
        for con in self.connections.datalist:
            index_right = node_to_index[con.right]
            index_left = node_to_index[con.left]
            incoming_counts[index_right] += 1
            outgoing_edges[index_left].append(index_right)
        
        stack = [node_to_index[i] for i in range(self.num_input_nodes)]
        for i in range(self.num_input_nodes):
            visited[node_to_index[i]] = True
        
        curr_index = 0
        while curr_index < len(sorted_nodes):
            node = sorted_nodes[curr_index]
            for neighbor in outgoing_edges[node]:


            
    
    def reset_weight(self)-> None:
        rando_con = self.connections.get_random_element()
        rando_con.weight = (np.random.random() * 2 - 1) * self.neat.shift_reset_strength
    
    def shift_weight(self)-> None:
        rando_con = self.connections.get_random_element()
        rando_con.weight = rando_con.weight + (np.random.random() * 2 - 1) * self.neat.shift_weight_strength
    
    def toggle_enable(self)-> None:
        rando_con = self.connections.get_random_element()
        rando_con.is_enabled = not rando_con.is_enabled
    
    def conduct_fitness_test(self)-> None:
        # self.fitness = something
        return
    
    def get_output(self, input: List[float]) -> List[float]:
        return [0.0]





    
    