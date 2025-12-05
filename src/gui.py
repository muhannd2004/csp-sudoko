import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time
import copy
from sudoku_generator import generate_sudoku, get_difficulty
from make_constrain import make_constrain
from back_track import back_track
from arc3 import ac3

GAME_SIZE = 9

class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🧩 CSP Sudoku Solver - AI Powered")
        self.root.geometry("800x900")
        self.root.configure(bg='#1a1a2e')
        
        # Make window resizable
        self.root.resizable(True, True)
        
        # Modern color scheme
        self.colors = {
            'bg': '#1a1a2e',
            'bg_light': '#16213e',
            'accent': '#0f3460',
            'highlight': '#e94560',
            'text': '#ffffff',
            'text_dim': '#a8b2d1',
            'grid_dark': '#0a2647',
            'grid_light': '#144272',
            'given': '#64ffda',
            'solving': '#ffd700',
            'button': '#e94560',
            'button_hover': '#ff6b81'
        }
        
        self.cells = []
        self.cell_frames = []
        self.game_state = [0] * 81
        self.initial_state = [0] * 81
        self.is_solving = False
        self.solving_speed = 0.05
        self.game_constrains = [[] for _ in range(81)]
        
        # Setup constraints once
        make_constrain(self.game_constrains)
        
        self.create_widgets()
        
    def create_widgets(self):
        # Create canvas with scrollbar for scrollable content
        canvas = tk.Canvas(self.root, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        
        # Main container inside canvas
        main_frame = tk.Frame(canvas, bg=self.colors['bg'])
        
        # Configure canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create window in canvas
        canvas_frame = canvas.create_window((0, 0), window=main_frame, anchor="nw")
        
        # Update scroll region when frame size changes
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def on_canvas_configure(event):
            # Center the frame if it's smaller than canvas
            canvas_width = event.width
            frame_width = main_frame.winfo_reqwidth()
            if frame_width < canvas_width:
                canvas.itemconfig(canvas_frame, width=canvas_width)
        
        main_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)
        
        # Enable mousewheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Add padding frame
        content_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title with styling
        title_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        title_frame.pack(pady=(0, 20))
        
        title_label = tk.Label(
            title_frame,
            text="🧩 SUDOKU SOLVER",
            font=("Helvetica", 28, "bold"),
            fg=self.colors['highlight'],
            bg=self.colors['bg']
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Powered by CSP & Arc Consistency Algorithm",
            font=("Helvetica", 11),
            fg=self.colors['text_dim'],
            bg=self.colors['bg']
        )
        subtitle_label.pack()
        
        # Grid container with border
        grid_container = tk.Frame(content_frame, bg=self.colors['highlight'], bd=3)
        grid_container.pack(pady=20)
        
        grid_frame = tk.Frame(grid_container, bg=self.colors['grid_dark'])
        grid_frame.pack(padx=3, pady=3)
        
        # Create 9x9 Sudoku grid
        for row in range(9):
            row_cells = []
            row_frames = []
            for col in range(9):
                # Determine background color (alternating 3x3 boxes)
                box_row = row // 3
                box_col = col // 3
                bg_color = self.colors['grid_dark'] if (box_row + box_col) % 2 == 0 else self.colors['grid_light']
                
                # Cell frame
                cell_frame = tk.Frame(
                    grid_frame,
                    bg=bg_color,
                    highlightbackground=self.colors['accent'],
                    highlightthickness=1
                )
                
                # Extra padding for 3x3 box separation
                padx = (4, 1) if col % 3 == 0 else (1, 1)
                pady = (4, 1) if row % 3 == 0 else (1, 1)
                
                cell_frame.grid(row=row, column=col, padx=padx, pady=pady)
                
                # Entry widget with modern styling
                entry = tk.Entry(
                    cell_frame,
                    width=2,
                    font=("Helvetica", 20, "bold"),
                    justify="center",
                    fg=self.colors['text'],
                    bg=bg_color,
                    relief=tk.FLAT,
                    insertbackground=self.colors['highlight'],
                    bd=0
                )
                entry.pack(padx=8, pady=8)
                
                # Validate input
                vcmd = (self.root.register(self.validate_input), '%P')
                entry.config(validate="key", validatecommand=vcmd)
                
                # Bind to check conflicts on every key release
                entry.bind('<KeyRelease>', lambda e, r=row, c=col: self.check_cell_conflict(r, c))
                
                row_cells.append(entry)
                row_frames.append(cell_frame)
                
            self.cells.append(row_cells)
            self.cell_frames.append(row_frames)
        
        # Controls container
        controls_container = tk.Frame(content_frame, bg=self.colors['bg'])
        controls_container.pack(pady=20, fill=tk.X)
        
        # Mode 1: Generate Puzzle
        gen_frame = tk.LabelFrame(
            controls_container,
            text="  🎲 Generate Puzzle (Mode 1)  ",
            font=("Helvetica", 12, "bold"),
            fg=self.colors['text'],
            bg=self.colors['bg_light'],
            bd=2,
            relief=tk.RAISED
        )
        gen_frame.pack(fill=tk.X, pady=5)
        
        buttons_frame = tk.Frame(gen_frame, bg=self.colors['bg_light'])
        buttons_frame.pack(pady=10)
        
        for difficulty in ["Easy", "Medium", "Hard"]:
            btn = tk.Button(
                buttons_frame,
                text=f"🎯 {difficulty}",
                command=lambda d=difficulty: self.generate(d),
                font=("Helvetica", 11, "bold"),
                fg=self.colors['text'],
                bg=self.colors['button'],
                activebackground=self.colors['button_hover'],
                activeforeground=self.colors['text'],
                bd=0,
                padx=20,
                pady=10,
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=5)
            self.add_hover_effect(btn)
        
        # Mode 2: Manual Input & Solve
        action_frame = tk.LabelFrame(
            controls_container,
            text="  🤖 AI Solver Actions (Mode 2)  ",
            font=("Helvetica", 12, "bold"),
            fg=self.colors['text'],
            bg=self.colors['bg_light'],
            bd=2,
            relief=tk.RAISED
        )
        action_frame.pack(fill=tk.X, pady=5)
        
        action_buttons_frame = tk.Frame(action_frame, bg=self.colors['bg_light'])
        action_buttons_frame.pack(pady=10)
        
        solve_btn = tk.Button(
            action_buttons_frame,
            text="▶️ Solve with AI",
            command=self.start_solve,
            font=("Helvetica", 11, "bold"),
            fg=self.colors['text'],
            bg='#2ecc71',
            activebackground='#27ae60',
            activeforeground=self.colors['text'],
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        solve_btn.pack(side=tk.LEFT, padx=5)
        self.add_hover_effect(solve_btn)
        
        check_btn = tk.Button(
            action_buttons_frame,
            text="✓ Validate Board",
            command=self.check_solvability,
            font=("Helvetica", 11, "bold"),
            fg=self.colors['text'],
            bg='#3498db',
            activebackground='#2980b9',
            activeforeground=self.colors['text'],
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        check_btn.pack(side=tk.LEFT, padx=5)
        self.add_hover_effect(check_btn)
        
        clear_btn = tk.Button(
            action_buttons_frame,
            text="🗑️ Clear Board",
            command=self.clear_board,
            font=("Helvetica", 11, "bold"),
            fg=self.colors['text'],
            bg='#e74c3c',
            activebackground='#c0392b',
            activeforeground=self.colors['text'],
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        self.add_hover_effect(clear_btn)
        
        # Speed control
        speed_frame = tk.Frame(controls_container, bg=self.colors['bg_light'], bd=2, relief=tk.RAISED)
        speed_frame.pack(fill=tk.X, pady=5, padx=5)
        
        speed_label = tk.Label(
            speed_frame,
            text="⚡ Solving Speed:",
            font=("Helvetica", 11, "bold"),
            fg=self.colors['text'],
            bg=self.colors['bg_light']
        )
        speed_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.speed_var = tk.DoubleVar(value=0.05)
        speed_scale = tk.Scale(
            speed_frame,
            from_=0.0,
            to=0.2,
            resolution=0.01,
            variable=self.speed_var,
            orient=tk.HORIZONTAL,
            length=300,
            font=("Helvetica", 9),
            fg=self.colors['text'],
            bg=self.colors['bg_light'],
            troughcolor=self.colors['accent'],
            highlightthickness=0,
            bd=0
        )
        speed_scale.pack(side=tk.LEFT, padx=10, pady=10)
        
        speed_info = tk.Label(
            speed_frame,
            text="(0 = Instant)",
            font=("Helvetica", 9),
            fg=self.colors['text_dim'],
            bg=self.colors['bg_light']
        )
        speed_info.pack(side=tk.LEFT, padx=5)
        
        # Status bar
        status_frame = tk.Frame(content_frame, bg=self.colors['accent'], bd=2, relief=tk.SUNKEN)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_var = tk.StringVar(value="Ready to solve puzzles! 🚀")
        status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Helvetica", 11),
            fg=self.colors['text'],
            bg=self.colors['accent'],
            anchor=tk.W
        )
        status_label.pack(padx=10, pady=8, fill=tk.X)
        
    def add_hover_effect(self, button):
        """Add hover effect to buttons"""
        original_bg = button.cget('bg')
        
        def on_enter(e):
            button['background'] = button['activebackground']
        
        def on_leave(e):
            button['background'] = original_bg
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    def validate_input(self, new_value):
        """Validate that input is a single digit 1-9 or empty"""
        if new_value == "":
            return True
        if new_value.isdigit() and len(new_value) == 1 and new_value != "0":
            return True
        return False
    
    def check_cell_conflict(self, row, col):
        """Check if current cell has conflicts and highlight in red"""
        idx = row * 9 + col
        val = self.cells[row][col].get()
        
        # Get background color for this cell
        box_row = row // 3
        box_col = col // 3
        bg_color = self.colors['grid_dark'] if (box_row + box_col) % 2 == 0 else self.colors['grid_light']
        
        if val == "" or not val.isdigit():
            # Empty cell - reset to default color
            if self.initial_state[idx] != 0:
                self.cells[row][col].config(fg=self.colors['given'])
            else:
                self.cells[row][col].config(fg=self.colors['text'])
            return
        
        current_value = int(val)
        has_conflict = False
        
        # Check all neighbors for conflicts
        for neighbor_idx in self.game_constrains[idx]:
            neighbor_row = neighbor_idx // 9
            neighbor_col = neighbor_idx % 9
            neighbor_val = self.cells[neighbor_row][neighbor_col].get()
            
            if neighbor_val.isdigit() and int(neighbor_val) == current_value:
                has_conflict = True
                break
        
        # Update color based on conflict
        if has_conflict:
            self.cells[row][col].config(fg='#ff3333')  # Bright red for conflicts
            self.status_var.set(f"⚠️ Conflict detected at row {row+1}, column {col+1}!")
        else:
            if self.initial_state[idx] != 0:
                self.cells[row][col].config(fg=self.colors['given'])
            else:
                self.cells[row][col].config(fg=self.colors['text'])
            # Clear conflict status if no conflicts exist anywhere
            board = self.get_board_from_ui()
            if not self.has_any_conflicts(board):
                self.status_var.set("✅ No conflicts detected!")
    
    def has_any_conflicts(self, board):
        """Check if board has any conflicts"""
        for i in range(81):
            if board[i] != 0:
                for neighbor in self.game_constrains[i]:
                    if board[neighbor] == board[i]:
                        return True
        return False
    
    def get_board_from_ui(self):
        """Extract board state from UI as flat list"""
        board = [0] * 81
        for r in range(9):
            for c in range(9):
                val = self.cells[r][c].get()
                if val.isdigit() and val != "":
                    board[r * 9 + c] = int(val)
        return board
    
    def update_ui_from_board(self, board, highlight_new=False):
        """Update UI from board state"""
        for r in range(9):
            for c in range(9):
                idx = r * 9 + c
                val = board[idx]
                current_val = self.cells[r][c].get()
                str_val = str(val) if val != 0 else ""
                
                if current_val != str_val:
                    self.cells[r][c].delete(0, tk.END)
                    if val != 0:
                        self.cells[r][c].insert(0, str_val)
                        
                        # Color coding
                        if self.initial_state[idx] != 0:
                            # Given number
                            self.cells[r][c].config(fg=self.colors['given'])
                        elif highlight_new:
                            # Newly solved
                            self.cells[r][c].config(fg=self.colors['solving'])
                
        self.root.update()
    
    def clear_board(self):
        """Clear all cells"""
        for r in range(9):
            for c in range(9):
                self.cells[r][c].delete(0, tk.END)
                self.cells[r][c].config(state=tk.NORMAL, fg=self.colors['text'])
        self.initial_state = [0] * 81
        self.status_var.set("Board cleared! Ready for new puzzle. 🎯")
    
    def generate(self, difficulty):
        """Generate a random puzzle of specified difficulty"""
        self.clear_board()
        self.status_var.set(f"Generating {difficulty} puzzle... ⏳")
        self.root.update()
        
        board = generate_sudoku(difficulty)
        self.initial_state = board.copy()
        self.update_ui_from_board(board)
        
        # Lock given cells
        for r in range(9):
            for c in range(9):
                if board[r * 9 + c] != 0:
                    self.cells[r][c].config(fg=self.colors['given'])
        
        givens = sum(1 for x in board if x != 0)
        self.status_var.set(f"✅ {difficulty} puzzle generated! ({givens} given numbers)")
    
    def check_solvability(self):
        """Validate board and check difficulty"""
        board = self.get_board_from_ui()
        
        # Setup constraints
        game_constrains = [[] for _ in range(81)]
        make_constrain(game_constrains)
        
        # Check for conflicts
        for i in range(81):
            if board[i] != 0:
                for neighbor in game_constrains[i]:
                    if board[neighbor] == board[i]:
                        self.status_var.set("❌ Invalid board: Conflict detected!")
                        messagebox.showerror("Invalid Board", "There is a conflict in the board!\nSame number appears in row/column/box.")
                        return
        
        difficulty = get_difficulty(board)
        givens = sum(1 for x in board if x != 0)
        
        self.status_var.set(f"✅ Board is valid! Difficulty: {difficulty} ({givens} numbers)")
        messagebox.showinfo(
            "Board Validation",
            f"✅ Board appears valid!\n\n"
            f"📊 Difficulty: {difficulty}\n"
            f"🔢 Given numbers: {givens}/81\n"
            f"📝 Empty cells: {81 - givens}"
        )
    
    def start_solve(self):
        """Start solving in a separate thread"""
        if self.is_solving:
            messagebox.showwarning("Already Solving", "Solver is already running!")
            return
        
        board = self.get_board_from_ui()
        self.initial_state = board.copy()
        
        self.is_solving = True
        self.status_var.set("🤖 AI Solver running... Applying Arc Consistency!")
        
        # Run in separate thread
        threading.Thread(target=self.solve_logic, args=(board,), daemon=True).start()
    
    def solve_logic(self, initial_board):
        """Main solving logic using your algorithms"""
        game_constrains = [[] for _ in range(81)]
        make_constrain(game_constrains)
        
        # Setup domains
        domains = []
        for val in initial_board:
            if val != 0:
                domains.append({val})
            else:
                domains.append(set(range(1, 10)))
        
        # Apply initial AC3
        self.root.after(0, lambda: self.status_var.set("🔄 Applying Arc Consistency (AC-3)..."))
        
        if not ac3(game_constrains, domains):
            self.root.after(0, lambda: self.finish_solve(False, "❌ Puzzle is unsolvable (detected by AC-3)"))
            return
        
        self.root.after(0, lambda: self.status_var.set("🔍 Backtracking with MAC..."))
        
        # Backtracking with visualization
        solution_found = back_track(initial_board, domains, game_constrains)
        
        if solution_found:
            # Update final board
            self.root.after(0, lambda: self.update_ui_from_board(initial_board))
            self.root.after(0, lambda: self.finish_solve(True, "✅ Puzzle solved successfully! 🎉"))
        else:
            self.root.after(0, lambda: self.finish_solve(False, "❌ No solution found!"))
    
    def finish_solve(self, success, message):
        """Finish solving and update UI"""
        self.is_solving = False
        self.status_var.set(message)
        
        if success:
            messagebox.showinfo("Success! 🎉", "Puzzle solved successfully using CSP + AC-3!")
        else:
            messagebox.showwarning("No Solution", message)

def main():
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
