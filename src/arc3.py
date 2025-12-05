from collections import deque

GAME_SIZE = 9
 
def ac3(game_constrains: list[list[int]], domains: list[set[int]], queue: deque = None) -> bool:
    in_queue = [[False for _ in range(81)] for _ in range(81)]
    
    if queue is None:
        queue = deque()
        for i in range(len(game_constrains)):
            for neighbor in game_constrains[i]:
                queue.append((i, neighbor))
                in_queue[i][neighbor] = True

    while queue:
        xi, xj = queue.popleft()
        in_queue[xi][xj] = False
        
        if revise(xi, xj, domains):
            if len(domains[xi]) == 0: # domain size = 0 return false
                return False
            for xk in game_constrains[xi]:
                if xk != xj and not in_queue[xk][xi]:
                    queue.append((xk, xi))
                    in_queue[xk][xi] = True
    
    return True

def revise(xi: int, xj: int, domains: list[set[int]]) -> bool:
    revised = False

    for value in list(domains[xi]):
        if len(domains[xj]) == 1 and value in domains[xj]:
            domains[xi].discard(value)
            revised = True

    return revised