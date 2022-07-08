from typing import List
from Genome import Genome
class Organism():
    
    def __init__(self):
        self.genome : Genome = None # type: ignore
        self.fitness : float = 0.0
        self.species = None # type: ignore
    
    def mutate(self) -> None:
        self.genome.mutate()
    
    def get_output(self, input : List[float]) -> List[float]:
        return self.genome.get_output(input)
    
    def crossover(self, other_organism) -> Genome:
        return self.genome.cross_over(other_organism.genome, self.fitness, other_organism.fitness)
    
    def distance_from(self, other_organism) -> float:
        return self.genome.get_distance(other_organism.genome)
    
    # This is just temporary, just try to max the output
    def conduct_fitness_exam(self):
        input = [1.0 for _ in range(self.genome.num_input_nodes)]
        self.fitness = min(self.get_output(input))
