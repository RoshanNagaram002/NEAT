from Info import Randomized_Info, Sorted_Randomized_Info, ListDict
import numpy as np
from Components import Node, Connection
from typing import List
from queue import Queue
class Genome:
    def __init__(self, neat, num_input_nodes: int, num_output_nodes: int):
        # Data
        self.nodes = Randomized_Info()
        self.connections = Sorted_Randomized_Info()
        self.unsplit_connections = ListDict()
        self.tup_to_connection = {}

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
        
        if num_matching == 0:
            return ((c1 * num_excess) / N) + ((c2 * num_disjoint) / N)
        
        return ((c1 * num_excess) / N) + ((c2 * num_disjoint) / N) + (c3 * (total_weight_difference / num_matching))

    def cross_over(self, g2):
        child_genome = Genome(self.neat, self.num_input_nodes, self.num_output_nodes)

        beta_genome, alpha_genome = None, None

        if self.fitness >= g2.fitness:
            beta_genome, alpha_genome = g2, self
        else:
            beta_genome, alpha_genome = self, g2
        beta_pointer, alpha_pointer = 0, 0
        
        while beta_pointer < len(beta_genome.connections) and alpha_pointer < len(alpha_genome.connections):
            curr_beta_con, curr_alpha_con = beta_genome.connections.get(beta_pointer), alpha_genome.connections.get(alpha_pointer)
            if curr_beta_con == curr_alpha_con:
                is_beta = np.random.choice((0, 1))
                if is_beta == 1:
                    inherited_connection = curr_beta_con.copy()
                else:
                    inherited_connection = curr_alpha_con.copy()

                child_genome.connections.add(inherited_connection)
                self._add_hidden_connection_node_to_data(inherited_connection, child_genome.nodes)
                
                beta_pointer += 1
                alpha_pointer += 1
            
            elif curr_beta_con < curr_alpha_con:
                beta_pointer += 1
            
            elif curr_alpha_con < curr_beta_con:
                inherited_connection = curr_alpha_con.copy()

                child_genome.connections.add(inherited_connection)
                self._add_hidden_connection_node_to_data(inherited_connection, child_genome.nodes)

                alpha_pointer += 1
        
        while alpha_pointer < len(alpha_genome.connections):
            curr_alpha_con = alpha_genome.connections.get(alpha_pointer)
            inherited_connection = curr_alpha_con.copy()

            child_genome.connections.add(inherited_connection)
            self._add_hidden_connection_node_to_data(inherited_connection, child_genome.nodes)

            alpha_pointer += 1
        
        set_child_data(child_genome)

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
        if len(self.connections) == 0:
            return
        rando_tup = self.unsplit_connections.choose_random_item()
        self.unsplit_connections.remove_item(rando_tup)

        rando_con = self.tup_to_connection[rando_tup]

        split_node = self.neat.create_hidden_node(rando_con.left, rando_con.right)
        self.nodes.add(split_node)

        from_con = self.neat.create_hidden_connection(rando_con.left, split_node.node_id, 1, True)
        to_con = self.neat.create_hidden_connection(split_node.node_id, rando_con.right, rando_con.weight, True)

        rando_con.is_enabled = False

        self._add_connection_to_genome(from_con)
        self._add_connection_to_genome(to_con)
    
    def add_link(self)-> None:
        sorted_nodes = self._get_topologically_sorted_nodes()
        connection_ids = set()

        for con in self.connections:
            connection_ids.add(con.innovation_id)
        
        for _ in range(100):
            left_index = np.random.randint(0, len(sorted_nodes) - self.num_output_nodes)

            right_index = np.random.randint(max(left_index + 1, self.num_input_nodes) , len(sorted_nodes))

            left, right = sorted_nodes[left_index].node_id, sorted_nodes[right_index].node_id
            id = self.neat.get_connection_id(left, right)
            if id == -1 or id not in connection_ids:
                new_weight = (np.random.random() * 2 - 1) * self.neat.shift_reset_strength
                new_con = self.neat.create_hidden_connection(left, right, new_weight, True)
                self._add_connection_to_genome(new_con)
                return

    
    def reset_weight(self)-> None:
        if len(self.connections) == 0:
            return
        rando_con = self.connections.get_random_element()
        rando_con.weight = (np.random.random() * 2 - 1) * self.neat.shift_reset_strength
    
    def shift_weight(self)-> None:
        if len(self.connections) == 0:
            return
        rando_con = self.connections.get_random_element()
        rando_con.weight = rando_con.weight + (np.random.random() * 2 - 1) * self.neat.shift_weight_strength
    
    def toggle_enable(self)-> None:
        if len(self.connections) == 0:
            return
        rando_con = self.connections.get_random_element()
        rando_con.is_enabled = not rando_con.is_enabled
    
    def conduct_fitness_test(self)-> None:
        # self.fitness = something
        return
    
    def get_output(self, input: List[float]) -> List[float]:
        assert len(input) == self.num_input_nodes

        adj_dict = {}
        incoming_counts = {}
        id_to_node = {}
        node_to_values = {}

        for node in self.nodes:
            adj_dict[node.node_id] = []
            incoming_counts[node.node_id] = 0
            id_to_node[node.node_id] = node
            node_to_values[node.node_id] = 0
                
        for con in self.connections:
            if con.is_enabled:
                adj_dict[con.left].append((con.right, con.weight))
                incoming_counts[con.right] += 1
        
        q = Queue()

        # Fill in the input_values and add into the stack
        for i in range(self.num_input_nodes):
            node_to_values[i] = input[i]
            q.put(id_to_node[i])
        
        visited_outputs = set()
        for i in range(self.num_input_nodes, self.num_input_nodes + self.num_output_nodes):
            visited_outputs.add(i)

        while not q.empty():
            node = q.get()
            node_to_values[node.node_id] = node.act_func(node_to_values[node.node_id])

            if node.node_id in visited_outputs:
                visited_outputs.remove(node.node_id)
            
            for neighbor, weight in adj_dict[node.node_id]:
                incoming_counts[neighbor] -= 1
                node_to_values[neighbor] += (node_to_values[node.node_id] * weight)
                if incoming_counts[neighbor] == 0:
                    neighbor_node = id_to_node[neighbor]
                    if not neighbor_node.is_output:
                        q.put(neighbor_node)
        
        # Apply the activation function to output that you did not reach
        for output_id in visited_outputs:
            output_node = id_to_node[output_id]
            node_to_values[output_id] = output_node.act_func(node_to_values[output_id])

        return [node_to_values[i] for i in range(self.num_input_nodes, self.num_input_nodes + self.num_output_nodes)]
        
    
    def _add_connection_to_genome(self, new_con: Connection) -> None:
        left, right = new_con.left, new_con.right
        self.tup_to_connection[(left, right)] = new_con
        self.connections.add(new_con)
        self.unsplit_connections.add_item((left, right))
    
    def _add_hidden_connection_node_to_data(self, con: Connection, node_data: Randomized_Info) -> None:
        # Use this only for hidden nodes
        left_node_id, right_node_id = con.left, con.right
        left_node, right_node = Node(left_node_id), Node(right_node_id)
        if left_node not in node_data:
            node_data.add(left_node)
        if right_node not in node_data:
            node_data.add(right_node)
    
    def _get_topologically_sorted_nodes(self) -> List[Node]:
        # Returns [input_nodes, topo sorted hidden nodes ..., output_nodes]
        adj_dict = {}
        incoming_counts = {}
        id_to_node = {}
        for node in self.nodes:
            adj_dict[node.node_id] = []
            incoming_counts[node.node_id] = 0
            id_to_node[node.node_id] = node

        for con in self.connections:
            adj_dict[con.left].append(con.right)
            incoming_counts[con.right] += 1
        
        sorted_nodes = []

        for i in range(self.num_input_nodes):
            sorted_nodes.append(id_to_node[i])
        
        curr_index = 0
        while curr_index < len(sorted_nodes):
            node = sorted_nodes[curr_index]
            
            for neighbor in adj_dict[node.node_id]:
                incoming_counts[neighbor] -= 1
                if incoming_counts[neighbor] == 0:
                    neighbor_node = id_to_node[neighbor]
                    if not neighbor_node.is_output:
                        sorted_nodes.append(neighbor_node)
            
            curr_index += 1

        for i in range(self.num_input_nodes, self.num_input_nodes + self.num_output_nodes):
            sorted_nodes.append(id_to_node[i])
        
        return sorted_nodes

    # Remove this Later
    def set_fitness(self, x: float) -> None:
        self.fitness = x

def set_child_data(child:Genome) -> None:
    # Call this assuming you have the inherited nodes and inherited connections
    # This is to set the unsplit connections and the tup to_connection

    for con in child.connections:
        child.tup_to_connection[(con.left, con.right)] = con
        child.unsplit_connections.add_item((con.left, con.right))
    
    # Filter the unsplit_connections

    for node in child.nodes:
        if node.is_input or node.is_output:
            continue
        origin_conn = child.neat.node_to_origin_conn[node.node_id]
        child.unsplit_connections.remove_item(origin_conn)








    
    