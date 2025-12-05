GAME_SIZE = 9

def make_constrain(game_constrains: list[list[int]]) -> None:
    
    # add row constrain
    for pos in range(GAME_SIZE * GAME_SIZE): # current pos
        pos_row = pos // GAME_SIZE
        pos_col = pos % GAME_SIZE
        added = set()  
        added.add(pos)
        for i in range(GAME_SIZE): # row constrains
            pos_alpha = i + pos_row * GAME_SIZE

            if pos_alpha == pos or pos_alpha in added:
                continue
            game_constrains[pos].append(pos_alpha)
            added.add(pos_alpha)
        
        for i in range(GAME_SIZE): # column constrains
            pos_alpha = pos_col + i * GAME_SIZE

            if pos_alpha == pos or pos_alpha in added:
                continue
            game_constrains[pos].append(pos_alpha)
            added.add(pos_alpha)
       
           
        start_row = (pos_row // 3) * 3
        start_col = (pos_col // 3) * 3
        
        for r in range(start_row, start_row + 3):
            for c in range(start_col, start_col + 3):
                idx = r * GAME_SIZE + c
                if idx not in added:
                    game_constrains[pos].append(idx)
                    added.add(idx)
   