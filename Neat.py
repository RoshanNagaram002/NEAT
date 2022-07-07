from Components import Node, Connection
import Genome
class Neat:
    def __init__(self, input_size: int, output_size: int, num_organisms: int, c1: float = 1, c2: float = 1, c3: float = 1, shift_weight_strength = 0.3, shift_reset_strength = 1, survival_percentage = 0.8):
        self.input_size = input_size
        self.output_size = output_size
        self.max_organisms = num_organisms
        self.c1 = c1
        self.c2 = c2
        self.c3 = c3

        self.shift_weight_strength = shift_weight_strength
        self.shift_reset_strength = shift_reset_strength
        self.survival_percentage = survival_percentage

        self.global_connections = {}
        self.global_nodes = {}

        # Populate global_nodes with the input and output nodes
        # -1 Means None
        for i in range(self.input_size):
            self.global_nodes[(i, -1)] = i
        
        for i in range(self.input_size, self.input_size + self.output_size):
            self.global_nodes[(i, -1)] = i
    
    def create_hidden_node(self, left: int, right: int, act_func = None):
        node_id = None
        if (left, right) in self.global_nodes:
            node_id = self.global_nodes[(left, right)]
        else:
            node_id = len(self.global_nodes)
            self.global_nodes[(left, right)] = node_id
        
        new_node = Node(node_id)
        if act_func != None:
            new_node.act_func = act_func
        
        return new_node
    
    def create_hidden_connection(self, left: int, right: int, weight: float, is_enabled: bool):
        innovation_id = None
        if (left, right) in self.global_connections:
            innovation_id = self.global_connections[(left, right)]
        else:
            innovation_id = len(self.global_connections)
            self.global_connections[(left, right)] = innovation_id
        
        return Connection(innovation_id, left, right, weight, is_enabled)
    
myneat = Neat(3, 2, 100)
g = Genome.Genome(myneat, 3, 2)

from graphviz import Digraph

dot = Digraph(comment = 'Genome')

for node in g.nodes.datalist:
    dot.node(str(node.node_id), str(node.node_id))

for con in g.connections.datalist:
    start, end = str(con.left), str(con.right)
    dot.edge(start, end, label = str(con.weight))

dot.format= 'png'
dot.render(directory='visualizaions', view = True)



        