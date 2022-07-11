import sys
import os
from dino import *
sys.path.append('Neat_src')
from Neat_src.Neat import Neat
from Neat_src.Info import Network
import pickle


def save_network(net : Network, name_of_file : str, folder : str):
    folder_path = os.path.join(os.getcwd(), folder)
    file_path = os.path.join(os.getcwd(), folder, name_of_file)
    if not os.path.isdir(folder_path):
        os.mkdir(folder_path)
    
    net_info = [net.nodes, net.connections, net.num_input_nodes, net.num_output_nodes]
    with open(file_path, 'wb') as f:
        pickle.dump(net_info, f) # type: ignore

def replay(file_path : str):
    if not os.path.exists(file_path):
        print("Does not Exist")
        return
    with open(file_path, 'rb') as f:
        nodes, edges, num_input, num_output = pickle.load(f) # type: ignore
        net = Network(nodes, edges, num_input, num_output)
        print(gameplay(net))


def train():
    num_inputs, num_outputs = 7, 2
    num_players = 300
    c1 = 1
    c2 = 1
    c3 = 1
    c1: float = 1
    c2: float = 1
    c3: float = 1 
    shift_weight_strength = .5
    shift_reset_strength = 1
    survival_percentage = 0.2
    add_node_chance = 0.2
    add_link_chance = 0.5
    reset_chance = 0.1
    shift_chance = 0.8
    toggle_chance = 0.01
    species_thresh = 3.0
    
    dino_neat = Neat(num_inputs, num_outputs, num_players, gameplay, c1 = c1, c2 = c2, c3 = c3, shift_weight_strength=shift_weight_strength,
                shift_reset_strength = shift_reset_strength, survival_percentage= survival_percentage, add_node_chance=add_node_chance,
                add_link_chance = add_link_chance, reset_chance=reset_chance, shift_chance= shift_chance, 
                toggle_chance= toggle_chance, species_thresh=species_thresh)

    best_score = 0.0
    folder = 'Dino_models'
    gen_num = 1
    while best_score < 100:
        gen_best_net, gen_best_score = dino_neat.conduct_evolution()
        print(best_score, gen_best_score)
        best_score = max(best_score, gen_best_score)
        save_network(gen_best_net, 'gen_' + str(gen_num), folder)
        gen_num += 1

train()