from arc3 import ac3
from back_track import back_track

GAME_SIZE = 9
game_state: list[list[int]] = [[0 for _ in range(GAME_SIZE)] for _ in range(GAME_SIZE)]
game_constrains: list[list[int]] = [[] for _ in range(GAME_SIZE * GAME_SIZE)]

def solve_puzzle(initial_board):
    # Setup domains
    domains = []
    for val in initial_board:
        if val != 0:
            domains.append({val})
        else:
            domains.append(set(range(1, 10)))
            
    if not ac3(game_constrains, domains):
        print("Unsolvable detected by initial AC-3")
        return

    if back_track(initial_board, domains, game_constrains):
        print("Solved!")
        # Print 'initial_board' which now contains the solution
    else:
        print("No solution found.")