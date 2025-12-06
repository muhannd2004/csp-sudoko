import random
import copy
from back_track import back_track
from make_constrain import make_constrain
from arc3 import ac3

GAME_SIZE = 9

def get_difficulty(board: list[int]) -> str:
   
    givens = sum(1 for x in board if x != 0)
    if givens >= 40:
        return "Easy"
    elif givens >= 32:
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

def has_unique_solution_ac3(board: list[int]) -> bool:
    """Check if board has unique solution using AC-3 only"""
    game_constrains = [[] for _ in range(81)]
    make_constrain(game_constrains)
    
    # Setup domains
    domains = []
    for val in board:
        if val != 0:
            domains.append({val})
        else:
            domains.append(set(range(1, 10)))
    
    # Apply AC-3
    if not ac3(game_constrains, domains):
        return False
    
    # Check if all domains reduced to single values (unique solution)
    return all(len(d) == 1 for d in domains)

def generate_sudoku(difficulty: str = "Medium") -> list[int]:
    """Generate a Sudoku puzzle with unique solution verifiable by AC-3"""
    max_attempts = 50  # Reduced from 100 to prevent long hangs
    
    for attempt in range(max_attempts):
        try:
            board = [0] * 81
            
            # Fill diagonal boxes
            for i in range(0, 9, 3):
                fill_box(board, i, i)

            game_constrains = [[] for _ in range(81)]
            make_constrain(game_constrains)
            
            domains = [set(range(1, 10)) for _ in range(81)]
            for i in range(81):
                if board[i] != 0:
                    domains[i] = {board[i]}
            
            # Solve the complete board
            if not back_track(board, domains, game_constrains):
                continue
            
            # Determine number of cells to keep based on difficulty
            # More clues = easier = unique solution by AC-3
            if difficulty == "Easy":
                cells_to_keep = 42  # Keep more clues
            elif difficulty == "Medium":
                cells_to_keep = 36  # Keep moderate clues
            else:  # Hard
                cells_to_keep = 32  # Keep fewer clues but still AC-3 solvable
            
            # Try to create puzzle by removing cells
            filled_positions = [i for i in range(81)]
            random.shuffle(filled_positions)
            
            puzzle = board.copy()
            removed_count = 0
            target_removals = 81 - cells_to_keep
            
            # Limit checks to prevent infinite loops
            max_checks = min(81, target_removals + 10)
            checks = 0
            
            for pos in filled_positions:
                if removed_count >= target_removals or checks >= max_checks:
                    break
                
                checks += 1
                
                # Try removing this cell
                backup = puzzle[pos]
                puzzle[pos] = 0
                
                # Check if still has unique solution by AC-3
                if has_unique_solution_ac3(puzzle):
                    removed_count += 1
                else:
                    # Restore the cell
                    puzzle[pos] = backup
            
            # Verify final puzzle has unique solution by AC-3
            if has_unique_solution_ac3(puzzle):
                # Clear references to help garbage collection
                del board, domains, game_constrains
                return puzzle
                
        except Exception as e:
            print(f"Error in generation attempt {attempt + 1}: {e}")
            continue
    
    # If we couldn't generate a valid puzzle, return a simpler fallback
    print(f"Warning: Could not generate {difficulty} puzzle with AC-3 unique solution after {max_attempts} attempts")
    # Return the last attempt if it exists
    if 'puzzle' in locals():
        return puzzle
    else:
        # Return empty board as last resort
        return [0] * 81
