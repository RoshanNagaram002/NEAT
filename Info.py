import numpy as np
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