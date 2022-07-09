from typing import List
from Genome import Genome
from Info import Network
class Organism:
    
    def __init__(self):
        self.genome : Genome = None # type: ignore
        self.fitness : float = 0.0
        self.species = None # type: ignore
    
    def mutate(self) -> None:
        self.genome.mutate()
    
    def extract_network(self) -> Network:
        return self.genome._extract_network()
    
    def crossover(self, other_organism) -> Genome:
        return self.genome.cross_over(other_organism.genome, self.fitness, other_organism.fitness)
    
    def distance_from(self, other_organism) -> float:
        return self.genome.get_distance(other_organism.genome)
