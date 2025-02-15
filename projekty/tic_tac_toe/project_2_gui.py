import tkinter as tk
from tkinter import messagebox
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)

# Constants
PLAYER_X = "X"
PLAYER_O = "O"
EMPTY_CELL = " "
BG_COLOR = "#f0f0f0"

class TicTacToeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe")
        self.root.configure(bg=BG_COLOR)
        
        self.current_player = PLAYER_X
        self.board = [EMPTY_CELL] * 9
        
        self.buttons = []
        self.create_board()
        
    def create_board(self):
        """Create the game board with buttons."""
        for i in range(9):
            btn = tk.Button(self.root, text=EMPTY_CELL, font=("Arial", 20), height=2, width=5, 
                            bg="white", fg="black",
                            command=lambda i=i: self.on_click(i))
            btn.grid(row=i//3, column=i%3, padx=5, pady=5)
            self.buttons.append(btn)
        
    def on_click(self, index):
        """Handle button click for player moves."""
        if self.board[index] == EMPTY_CELL:
            self.board[index] = self.current_player
            color = Fore.RED if self.current_player == PLAYER_X else Fore.BLUE
            self.buttons[index].config(text=self.current_player, state=tk.DISABLED, fg="red" if self.current_player == PLAYER_X else "blue")
            
            if self.check_winner():
                messagebox.showinfo("Game Over", f"{color}Player {self.current_player} wins!")
                self.reset_board()
            elif self.is_draw():
                messagebox.showinfo("Game Over", "It's a draw!")
                self.reset_board()
            else:
                self.switch_player()
    
    def switch_player(self):
        """Switch to the other player."""
        self.current_player = PLAYER_O if self.current_player == PLAYER_X else PLAYER_X
    
    def check_winner(self):
        """Check if the current player has won the game."""
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Horizontal
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Vertical
            [0, 4, 8], [2, 4, 6],             # Diagonal
        ]
        return any(all(self.board[i] == self.current_player for i in condition) for condition in win_conditions)
    
    def is_draw(self):
        """Check if the game is a draw."""
        return all(cell != EMPTY_CELL for cell in self.board)
    
    def reset_board(self):
        """Reset the game board."""
        self.board = [EMPTY_CELL] * 9
        self.current_player = PLAYER_X
        for btn in self.buttons:
            btn.config(text=EMPTY_CELL, state=tk.NORMAL, fg="black", bg="white")

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToeGUI(root)
    root.mainloop()
