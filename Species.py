from Info import Randomized_Info
from Organism import Organism
class Species:
    
    def __init__(self, rep: Organism, threshold: float):
        self.rep = rep
        self.organisms = Randomized_Info()
        self.organisms.add(rep)
        self.rep.species = self # type: ignore
        self.threshold = threshold
        self.score = 0.0
    
    def update_score(self) -> None:
        total = 0
        for organism in self.organisms:
            total += organism.fitness
        self.score = total / len(self.organisms)
    
    def categorize(self, organism : Organism) -> bool:

        if self.rep.distance_from(organism) <= self.threshold:
            self.add_organism(organism)
            return True
        
        return False
    
    def add_organism(self, organism: Organism) -> None:
        self.organisms.add(organism)
        organism.species = self # type: ignore
    
    def go_Extinct(self):
        for organism in self.organisms:
            organism.species = None
    
    def breed(self) -> Organism:
        p1 = self.organisms.get_random_element()
        p2 = self.organisms.get_random_element()

        child = Organism()
        child.genome = p1.genome.cross_over(p2.genome, p1.fitness, p2.fitness)
        child.fitness = 0.0
        
        self.add_organism(child)

        return child
    
    def reset(self) -> None:
        new_rep = self.organisms.get_random_element()
        for organism in self.organisms:
            organism.species = None
        
        self.organisms.clear()
        self.add_organism(new_rep)
        self.rep = new_rep
        self.score = 0
    
    def kill(self, kill_percentage : float) -> None:
        num_to_kill = int(kill_percentage * len(self.organisms))
        
        # sort orgnisms form highest to lowest so we can pop the ends off in constant time
        self.organisms.datalist.sort(key = lambda x: x.fitness, reverse=True)
        for _ in range(num_to_kill):
            killed_organism = self.organisms.custom_pop()
            killed_organism.species = None

    
    
