import tkinter as tk
from tkinter import messagebox, ttk
import threading

from sudoku_generator import generate_sudoku, get_difficulty
from make_constrain import make_constrain
from back_track import back_track
from arc3 import ac3

GAME_SIZE = 9

class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🧩 CSP Sudoku Solver - AI Powered")
        self.root.geometry("750x800")
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
        self.domain_labels = []  # New: labels to show domains
        self.game_state = [0] * 81
        self.initial_state = [0] * 81
        self.is_solving = False
        self.game_constrains = [[] for _ in range(81)]
        self.show_domains = False  # Toggle for domain display
        self.domain_mode = "simple"  # "simple" or "ac3"
        
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
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title with styling
        title_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        title_frame.pack(pady=(0, 10))
        
        title_label = tk.Label(
            title_frame,
            text="🧩 SUDOKU SOLVER",
            font=("Helvetica", 22, "bold"),
            fg=self.colors['highlight'],
            bg=self.colors['bg']
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Powered by CSP & Arc Consistency Algorithm",
            font=("Helvetica", 9),
            fg=self.colors['text_dim'],
            bg=self.colors['bg']
        )
        subtitle_label.pack()
        
        # Grid container with border
        grid_container = tk.Frame(content_frame, bg=self.colors['highlight'], bd=2)
        grid_container.pack(pady=10)
        
        grid_frame = tk.Frame(grid_container, bg=self.colors['grid_dark'])
        grid_frame.pack(padx=2, pady=2)
        
        # Create 9x9 Sudoku grid
        for row in range(9):
            row_cells = []
            row_frames = []
            row_domain_labels = []
            for col in range(9):
                # Determine background color (alternating 3x3 boxes)
                box_row = row // 3
                box_col = col // 3
                bg_color = self.colors['grid_dark'] if (box_row + box_col) % 2 == 0 else self.colors['grid_light']
                
                # Cell container frame
                cell_container = tk.Frame(
                    grid_frame,
                    bg=bg_color,
                    highlightbackground=self.colors['accent'],
                    highlightthickness=1
                )
                
                # Extra padding for 3x3 box separation
                padx = (4, 1) if col % 3 == 0 else (1, 1)
                pady = (4, 1) if row % 3 == 0 else (1, 1)
                
                cell_container.grid(row=row, column=col, padx=padx, pady=pady)
                
                # Entry widget with modern styling
                entry = tk.Entry(
                    cell_container,
                    width=3,
                    font=("Helvetica", 20, "bold"),
                    justify="center",
                    fg=self.colors['text'],
                    bg=bg_color,
                    relief=tk.FLAT,
                    insertbackground=self.colors['highlight'],
                    bd=0
                )
                entry.pack(padx=10, pady=(8, 2))
                
                # Domain label (initially hidden)
                domain_label = tk.Label(
                    cell_container,
                    text="",
                    font=("Courier", 6),
                    fg=self.colors['text_dim'],
                    bg=bg_color,
                    justify="center",
                    wraplength=50  # Allow text wrapping for long domains
                )
                domain_label.pack(padx=2, pady=(0, 4))
                
                # Validate input
                vcmd = (self.root.register(self.validate_input), '%P')
                entry.config(validate="key", validatecommand=vcmd)
                
                # Bind to check conflicts and update domains on every key release
                entry.bind('<KeyRelease>', lambda e, r=row, c=col: self.on_cell_change(r, c))
                
                row_cells.append(entry)
                row_frames.append(cell_container)
                row_domain_labels.append(domain_label)
                
            self.cells.append(row_cells)
            self.cell_frames.append(row_frames)
            self.domain_labels.append(row_domain_labels)
        
        # Controls container
        controls_container = tk.Frame(content_frame, bg=self.colors['bg'])
        controls_container.pack(pady=10, fill=tk.X)
        
        # Mode 1: Generate Puzzle
        gen_frame = tk.LabelFrame(
            controls_container,
            text="  🎲 Generate Puzzle (Mode 1)  ",
            font=("Helvetica", 10, "bold"),
            fg=self.colors['text'],
            bg=self.colors['bg_light'],
            bd=2,
            relief=tk.RAISED
        )
        gen_frame.pack(fill=tk.X, pady=3)
        
        buttons_frame = tk.Frame(gen_frame, bg=self.colors['bg_light'])
        buttons_frame.pack(pady=6)
        
        for difficulty in ["Easy", "Medium", "Hard"]:
            btn = tk.Button(
                buttons_frame,
                text=f"🎯 {difficulty}",
                command=lambda d=difficulty: self.generate(d),
                font=("Helvetica", 9, "bold"),
                fg=self.colors['text'],
                bg=self.colors['button'],
                activebackground=self.colors['button_hover'],
                activeforeground=self.colors['text'],
                bd=0,
                padx=15,
                pady=6,
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=3)
            self.add_hover_effect(btn)
        
        # Mode 2: Manual Input & Solve
        action_frame = tk.LabelFrame(
            controls_container,
            text="  🤖 AI Solver Actions (Mode 2)  ",
            font=("Helvetica", 10, "bold"),
            fg=self.colors['text'],
            bg=self.colors['bg_light'],
            bd=2,
            relief=tk.RAISED
        )
        action_frame.pack(fill=tk.X, pady=3)
        
        action_buttons_frame = tk.Frame(action_frame, bg=self.colors['bg_light'])
        action_buttons_frame.pack(pady=6)
        
        solve_btn = tk.Button(
            action_buttons_frame,
            text="▶️ Solve with AI",
            command=self.start_solve,
            font=("Helvetica", 9, "bold"),
            fg=self.colors['text'],
            bg='#2ecc71',
            activebackground='#27ae60',
            activeforeground=self.colors['text'],
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2"
        )
        solve_btn.pack(side=tk.LEFT, padx=2)
        self.add_hover_effect(solve_btn)
        
        check_btn = tk.Button(
            action_buttons_frame,
            text="✓ Validate",
            command=self.check_solvability,
            font=("Helvetica", 9, "bold"),
            fg=self.colors['text'],
            bg='#3498db',
            activebackground='#2980b9',
            activeforeground=self.colors['text'],
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2"
        )
        check_btn.pack(side=tk.LEFT, padx=2)
        self.add_hover_effect(check_btn)
        
        # Toggle domains button
        domains_btn = tk.Button(
            action_buttons_frame,
            text="👁️ Domains",
            command=self.toggle_domains,
            font=("Helvetica", 9, "bold"),
            fg=self.colors['text'],
            bg='#9b59b6',
            activebackground='#8e44ad',
            activeforeground=self.colors['text'],
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2"
        )
        domains_btn.pack(side=tk.LEFT, padx=2)
        self.add_hover_effect(domains_btn)
        self.domains_btn = domains_btn  # Store reference
        
        # Toggle domain mode button (Simple vs AC-3)
        mode_btn = tk.Button(
            action_buttons_frame,
            text="🔄 Mode: Simple",
            command=self.toggle_domain_mode,
            font=("Helvetica", 9, "bold"),
            fg=self.colors['text'],
            bg='#f39c12',
            activebackground='#e67e22',
            activeforeground=self.colors['text'],
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2"
        )
        mode_btn.pack(side=tk.LEFT, padx=2)
        self.add_hover_effect(mode_btn)
        self.mode_btn = mode_btn  # Store reference
        
        clear_btn = tk.Button(
            action_buttons_frame,
            text="🗑️ Clear",
            command=self.clear_board,
            font=("Helvetica", 9, "bold"),
            fg=self.colors['text'],
            bg='#e74c3c',
            activebackground='#c0392b',
            activeforeground=self.colors['text'],
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2"
        )
        clear_btn.pack(side=tk.LEFT, padx=2)
        self.add_hover_effect(clear_btn)
        
        # Status bar
        status_frame = tk.Frame(content_frame, bg=self.colors['accent'], bd=2, relief=tk.SUNKEN)
        status_frame.pack(fill=tk.X, pady=(8, 0))
        
        self.status_var = tk.StringVar(value="Ready to solve puzzles! 🚀")
        status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Helvetica", 9),
            fg=self.colors['text'],
            bg=self.colors['accent'],
            anchor=tk.W
        )
        status_label.pack(padx=8, pady=5, fill=tk.X)
        
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
    
    def on_cell_change(self, row, col):
        """Handle cell value change - check conflicts and update domains"""
        # Check for conflicts
        self.check_cell_conflict(row, col)
        
        # Update domains if enabled
        if self.show_domains:
            self.update_domain_display()
    
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
                self.domain_labels[r][c].config(text="")
        self.initial_state = [0] * 81
        self.show_domains = False
        self.domains_btn.config(text="👁️ Domains")
        self.status_var.set("Board cleared! Ready for new puzzle. 🎯")
    
    def toggle_domains(self):
        """Toggle domain display on/off"""
        self.show_domains = not self.show_domains
        
        if self.show_domains:
            self.domains_btn.config(text="👁️ Hide")
            self.update_domain_display()
        else:
            self.domains_btn.config(text="👁️ Domains")
            # Clear all domain labels
            for r in range(9):
                for c in range(9):
                    self.domain_labels[r][c].config(text="")
    
    def toggle_domain_mode(self):
        """Toggle between simple and AC-3 domain modes"""
        if self.domain_mode == "simple":
            self.domain_mode = "ac3"
            self.mode_btn.config(text="🔄 Mode: AC-3")
        else:
            self.domain_mode = "simple"
            self.mode_btn.config(text="🔄 Mode: Simple")
        
        # Update display if domains are currently shown
        if self.show_domains:
            self.update_domain_display()
    
    def update_domain_display(self):
        """Calculate and display domains based on current mode"""
        if self.domain_mode == "simple":
            self.update_domain_display_simple()
        else:
            self.update_domain_display_ac3()
    
    def update_domain_display_simple(self):
        """Calculate and display current available values for each empty cell (Simple Mode)"""
        try:
            board = self.get_board_from_ui()
            
            # For each empty cell, calculate which values are NOT used by its neighbors
            for r in range(9):
                for c in range(9):
                    idx = r * 9 + c
                    
                    if board[idx] == 0:  # Only show for empty cells
                        # Start with all possible values
                        available_values = set(range(1, 10))
                        
                        # Remove values used by neighbors (same row, column, or box)
                        for neighbor_idx in self.game_constrains[idx]:
                            neighbor_value = board[neighbor_idx]
                            if neighbor_value != 0:
                                available_values.discard(neighbor_value)
                        
                        # Display the available values
                        if len(available_values) == 0:
                            domain_text = "✗"
                            color = '#ff3333'  # Red - no valid values (conflict)
                        elif len(available_values) == 1:
                            domain_text = str(list(available_values)[0])
                            color = '#2ecc71'  # Green - only one choice
                        else:
                            # Format domain - show all available values
                            domain_list = sorted(list(available_values))
                            if len(domain_list) <= 3:
                                # Short domain: show in one line
                                domain_text = ''.join(str(d) for d in domain_list)
                            elif len(domain_list) <= 6:
                                # Medium domain: show in two lines
                                mid = (len(domain_list) + 1) // 2
                                line1 = ''.join(str(d) for d in domain_list[:mid])
                                line2 = ''.join(str(d) for d in domain_list[mid:])
                                domain_text = f"{line1}\n{line2}"
                            else:
                                # Long domain: show in three lines (max 9 digits: 123/456/789)
                                domain_text = ''.join(str(d) for d in domain_list[:3]) + '\n'
                                domain_text += ''.join(str(d) for d in domain_list[3:6]) + '\n'
                                domain_text += ''.join(str(d) for d in domain_list[6:])
                            color = self.colors['text_dim']  # Gray - multiple choices
                        
                        self.domain_labels[r][c].config(text=domain_text, fg=color)
                    else:
                        # Filled cells don't show domains
                        self.domain_labels[r][c].config(text="")
            
            self.root.update()
            
        except Exception as e:
            print(f"Error updating domain display (simple): {e}")
            import traceback
            traceback.print_exc()
            # Clear domains on error
            for r in range(9):
                for c in range(9):
                    self.domain_labels[r][c].config(text="")
    
    def update_domain_display_ac3(self):
        """Calculate and display AC-3 reduced domains (AC-3 Mode)"""
        try:
            board = self.get_board_from_ui()
            
            # Setup constraints
            game_constrains = [[] for _ in range(81)]
            make_constrain(game_constrains)
            
            # Setup initial domains based on CURRENT board state
            domains = []
            for val in board:
                if val != 0:
                    domains.append({val})  # Filled cells get singleton domain
                else:
                    domains.append(set(range(1, 10)))  # Empty cells get full domain
            
            # Apply AC-3 to get reduced domains
            ac3_result = ac3(game_constrains, domains)
            
            # Display domains
            for r in range(9):
                for c in range(9):
                    idx = r * 9 + c
                    if board[idx] == 0:  # Only show for empty cells
                        domain = domains[idx]
                        if len(domain) == 0:
                            domain_text = "✗"
                            color = '#ff3333'  # Red - no valid values (conflict)
                        elif len(domain) == 1:
                            domain_text = str(list(domain)[0])
                            color = '#2ecc71'  # Green - AC-3 solved this cell
                        else:
                            # Format domain - show all AC-3 reduced values
                            domain_list = sorted(list(domain))
                            if len(domain_list) <= 3:
                                # Short domain: show in one line
                                domain_text = ''.join(str(d) for d in domain_list)
                            elif len(domain_list) <= 6:
                                # Medium domain: show in two lines
                                mid = (len(domain_list) + 1) // 2
                                line1 = ''.join(str(d) for d in domain_list[:mid])
                                line2 = ''.join(str(d) for d in domain_list[mid:])
                                domain_text = f"{line1}\n{line2}"
                            else:
                                # Long domain: show in three lines (max 9 digits: 123/456/789)
                                domain_text = ''.join(str(d) for d in domain_list[:3]) + '\n'
                                domain_text += ''.join(str(d) for d in domain_list[3:6]) + '\n'
                                domain_text += ''.join(str(d) for d in domain_list[6:])
                            color = self.colors['text_dim']  # Gray - multiple choices after AC-3
                        
                        self.domain_labels[r][c].config(text=domain_text, fg=color)
                    else:
                        # Filled cells don't show domains
                        self.domain_labels[r][c].config(text="")
            
            # Clear references to help garbage collection
            del domains, game_constrains, board
            
            self.root.update()
            
        except Exception as e:
            print(f"Error updating domain display (AC-3): {e}")
            import traceback
            traceback.print_exc()
            # Clear domains on error
            for r in range(9):
                for c in range(9):
                    self.domain_labels[r][c].config(text="")
    
    def generate(self, difficulty):
        """Generate a random puzzle of specified difficulty"""
        # Prevent multiple generations at once
        if self.is_solving:
            messagebox.showwarning("Busy", "Please wait for current operation to complete!")
            return
            
        self.clear_board()
        self.status_var.set(f"Generating {difficulty} puzzle... ⏳")
        self.root.update()
        
        try:
            board = generate_sudoku(difficulty)
            
            # Check if generation succeeded
            if board is None or sum(1 for x in board if x != 0) < 17:
                messagebox.showerror("Generation Failed", "Failed to generate a valid puzzle. Please try again.")
                self.status_var.set("❌ Generation failed. Try again.")
                return
                
            self.initial_state = board.copy()
            self.update_ui_from_board(board)
            
            # Lock given cells
            for r in range(9):
                for c in range(9):
                    if board[r * 9 + c] != 0:
                        self.cells[r][c].config(fg=self.colors['given'])
            
            givens = sum(1 for x in board if x != 0)
            self.status_var.set(f"✅ {difficulty} puzzle generated! ({givens} given numbers)")
            
            # Update domains if domain view is enabled
            if self.show_domains:
                self.update_domain_display()
                
        except Exception as e:
            print(f"Error generating puzzle: {e}")
            messagebox.showerror("Error", f"Failed to generate puzzle: {str(e)}")
            self.status_var.set("❌ Error generating puzzle")
            self.clear_board()
    
    def check_solvability(self):
        """Validate board and check if it has a unique solution using AC-3 only"""
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
        
        # Setup domains for AC-3
        domains = []
        for val in board:
            if val != 0:
                domains.append({val})
            else:
                domains.append(set(range(1, 10)))
        
        # Apply AC-3
        domains_copy = [d.copy() for d in domains]
        if not ac3(game_constrains, domains_copy):
            self.status_var.set("❌ Board is unsolvable!")
            messagebox.showerror("Unsolvable Board", "This board has no solution!\nAC-3 detected inconsistency.")
            return
        
        # Check if AC-3 alone gives a unique solution (all domains have size 1)
        unsolved_cells = sum(1 for d in domains_copy if len(d) > 1)
        
        if unsolved_cells == 0:
            # AC-3 solved it completely - unique solution
            difficulty = get_difficulty(board)
            givens = sum(1 for x in board if x != 0)
            self.status_var.set(f"✅ Board has unique solution! Difficulty: {difficulty}")
            messagebox.showinfo(
                "✅ Valid & Unique Solution",
                f"✅ Board is valid and has a UNIQUE solution!\n"
                f"(Verified by Arc Consistency only)\n\n"
                f"📊 Difficulty: {difficulty}\n"
                f"🔢 Given numbers: {givens}/81\n"
                f"📝 Empty cells: {81 - givens}"
            )
        else:
            # AC-3 didn't solve it completely - may have multiple solutions
            difficulty = get_difficulty(board)
            givens = sum(1 for x in board if x != 0)
            self.status_var.set(f"⚠️ Board may have multiple solutions! ({unsolved_cells} cells unsolved by AC-3)")
            messagebox.showwarning(
                "⚠️ Multiple Solutions Possible",
                f"⚠️ Board is valid but may have MULTIPLE solutions!\n"
                f"(Arc Consistency alone couldn't solve it)\n\n"
                f"📊 Difficulty: {difficulty}\n"
                f"🔢 Given numbers: {givens}/81\n"
                f"📝 Unsolved cells after AC-3: {unsolved_cells}\n\n"
                f"Note: Use 'Solve with AI' to find a solution using backtracking."
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
