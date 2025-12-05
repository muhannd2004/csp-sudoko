import copy
from collections import deque
from arc3 import ac3

GAME_SIZE = 9

# the MRV
def select_unassigned_variable(game_state: list[int], domains: list[set[int]]) -> int:
    best_var = -1
    min_size = float('inf')
    
    for i in range(GAME_SIZE * GAME_SIZE):
        if game_state[i] == 0:
            size = len(domains[i])
            if size < min_size:
                min_size = size
                best_var = i
    return best_var

def is_consistent(var: int, value: int, game_state: list[int], game_constrains: list[list[int]]) -> bool:
    for neighbor in game_constrains[var]:
        if game_state[neighbor] != 0:
            if game_state[neighbor] == value:
                return False
    return True

def back_track(game_state: list[int], domains: list[set[int]], game_constrains: list[list[int]]) -> bool:
    var = select_unassigned_variable(game_state, domains)
    
    if var == -1:
        return True
    
    for value in sorted(list(domains[var])):
        
        if is_consistent(var, value, game_state, game_constrains): # is it valid

            new_domains = copy.deepcopy(domains)
            new_domains[var] = {value}
            
            mac_queue = deque()
            for neighbor in game_constrains[var]:
                mac_queue.append((neighbor, var))
            
            if ac3(game_constrains, new_domains, mac_queue):
                game_state[var] = value
                
                if back_track(game_state, new_domains, game_constrains):
                    return True
                
                game_state[var] = 0
            
    return False