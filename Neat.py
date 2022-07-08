from turtle import color
from Components import Node, Connection
from Genome import Genome
from Info import Randomized_Info
from Organism import Organism
from Species import Species
class Neat:
    def __init__(self, input_size: int, output_size: int, num_organisms: int, c1: float = 1, c2: float = 1, c3: float = 1, 
                shift_weight_strength = 1, shift_reset_strength = 2, survival_percentage = 0.2,
                add_node_chance = 0.2, add_link_chance = 0.3, reset_chance = 0.6, shift_chance = 0.6, toggle_chance = 0.01, species_thresh = 2.0):
        self.input_size = input_size
        self.output_size = output_size
        self.max_organisms = num_organisms
        self.c1 = c1
        self.c2 = c2
        self.c3 = c3
        self.species_thresh = species_thresh

        self.shift_weight_strength = shift_weight_strength
        self.shift_reset_strength = shift_reset_strength
        self.survival_percentage = survival_percentage

        self.add_node_chance = add_node_chance
        self.add_link_chance = add_link_chance
        self.reset_chance = reset_chance
        self.shift_chance = shift_chance
        self.toggle_chance = toggle_chance

        self.global_connections = {}
        self.global_nodes = {}
        self.node_to_origin_conn = {}

        self.organisms = Randomized_Info()
        self.species = Randomized_Info()

        # Populate global_nodes with the input and output nodes
        # -1 Means None
        for i in range(self.input_size):
            self.global_nodes[(i, -1)] = i
        
        for i in range(self.input_size, self.input_size + self.output_size):
            self.global_nodes[(i, -1)] = i
        
        for _ in range(self.max_organisms):
            organism = Organism()
            organism.genome = Genome(self, self.input_size, self.output_size)
            self.organisms.add(organism)
    
    def create_hidden_node(self, left: int, right: int, act_func = None):
        node_id = None
        if (left, right) in self.global_nodes:
            node_id = self.global_nodes[(left, right)]
        else:
            node_id = len(self.global_nodes)
            self.global_nodes[(left, right)] = node_id
            self.node_to_origin_conn[node_id] = (left, right)
        
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
    
    def get_connection_id(self, left: int, right: int):
        id = -1
        if (left, right) in self.global_connections:
            id = self.global_connections[(left, right)]
        return id
    
    def conduct_evolution(self) -> None:
        self._update_organism_fitness()
        self._generate_species()
        self._kill()
        self._remove_extinct_species()
        self._repopulate()
        self._mutate()
    
    def _update_organism_fitness(self):
        for organism in self.organisms:
            organism.conduct_fitness_exam()
    
    def _generate_species(self) -> None:
        for species in self.species:
            species.reset()
        
        for organism in self.organisms:
            if organism.species == None:
                is_new_species = True
                for species in self.species:
                    if species.categorize(organism):
                        is_new_species = False
                        break
                
                if is_new_species:
                    new_species = Species(organism, self.species_thresh)
                    self.species.add(new_species)

        for species in self.species:
            species.update_score()

    def _kill(self):
        for species in self.species:
            species.kill(1- self.survival_percentage)

    def _remove_extinct_species(self):
        for i in range(len(self.species) - 1, -1, -1):
            species = self.species.get(i)
            if species.get_num_of_organisms() <= 1:
                species.go_extinct()
                self.species.custom_pop(i)
    
    def _repopulate(self):
        total_score = sum([species.score for species in self.species])
        weights = [species.score/total_score for species in self.species]

        for i in range(len(self.organisms)):
            organism = self.organisms.get(i)
            if organism.species == None:
                weighted_random_species : Species = self.species.get_random_element(weights = weights)
                new_organism = weighted_random_species.breed()
                self.organisms.replace(i, new_organism)

    
    def _mutate(self):
        for organism in self.organisms:
            organism.mutate()

myneat = Neat(2, 1, 150)

for i in range(500):
    myneat.conduct_evolution()
    # myneat.species_thresh *= .9
    print("--------------------------------------", "Generation " + str(i))
    for species in myneat.species:
        total = species.get_num_of_organisms()
        score = species.score
        print(species, total, score)

best_organism : Organism = None
best_score = float('-inf')
myneat._update_organism_fitness()
for species in myneat.species:
    for organism in species.organisms:
        if organism.fitness > best_score:
            best_organism = organism
            best_score = organism.fitness

print(best_organism.fitness)
best_genome = best_organism.genome

from graphviz import Digraph
dot = Digraph(comment = "Genoming!")
for g, curr in [(best_genome, '')]:
    
    for node in g.nodes.datalist:
        dot.node(curr + str(node.node_id), curr + str(node.node_id))

    for con in g.connections.datalist:
        start, end = str(con.left), str(con.right)
        if con.is_enabled:
            dot.edge(curr + start, curr + end, label = str(con.weight), color = 'green')
        else:
            dot.edge(curr + start, curr + end, label = str(con.weight), color = 'red')
    print(curr)
    print("Edges", [con.innovation_id for con in g.connections.datalist])
    print("Nodes", [node.node_id for node in g._get_topologically_sorted_nodes()])
    print("Unsplit Edges", [con for con in g.unsplit_connections])
    print("Tup_to_conn", [(tup[0] == con.left, tup[1] == con.right) for tup, con in g.tup_to_connection.items()])

dot.format= 'png'
dot.render(directory='visualizaions', view = True)


