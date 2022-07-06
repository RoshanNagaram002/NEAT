import numpy as np
class Randomized_Info:
    def __init__(self):
        self.datalist = []
        self.dataset = set()
    
    def contains(self, key)-> bool:
        return key in self.dataset
    
    def get_random_element(self):
        return np.random.choice(self.datalist)
    
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
    
    def __len__(self):
        return len(self.datalist)
    
    def __str__(self):
        return str(self.datalist)
    
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