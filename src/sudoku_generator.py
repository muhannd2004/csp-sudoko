import random
import copy
from back_track import back_track
from make_constrain import make_constrain

GAME_SIZE = 9

def get_difficulty(board: list[int]) -> str:
   
    givens = sum(1 for x in board if x != 0)
    if givens >= 36:
        return "Easy"
    elif givens >= 28:
        return "Medium"
    else:
        return "Hard"

def fill_box(board: list[int], row_start: int, col_start: int):
    """Fill a 3x3 box with random values 1-9"""
    nums = list(range(1, 10))
    random.shuffle(nums)
    for i in range(3):
        for j in range(3):
            board[(row_start + i) * 9 + (col_start + j)] = nums.pop()

def generate_sudoku(difficulty: str = "Medium") -> list[int]:

    board = [0] * 81
    
    for i in range(0, 9, 3):
        fill_box(board, i, i)

    game_constrains = [[] for _ in range(81)]
    make_constrain(game_constrains)
    
    domains = [set(range(1, 10)) for _ in range(81)]
    for i in range(81):
        if board[i] != 0:
            domains[i] = {board[i]}
    

    if not back_track(board, domains, game_constrains):
        # if if failed try again
        return generate_sudoku(difficulty)
    
    if difficulty == "Easy":
        cells_to_remove = 45  
    elif difficulty == "Medium":
        cells_to_remove = 53  
    else:  # Hard
        cells_to_remove = 58  
    
    positions = list(range(81))
    random.shuffle(positions)
    
    removed = 0
    for pos in positions:
        if removed >= cells_to_remove:
            break
        
        backup = board[pos]
        board[pos] = 0
        removed += 1
    
    return board
