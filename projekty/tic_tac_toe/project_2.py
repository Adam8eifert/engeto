"""
projekt_2.py: druhý projekt do Engeto Online Python Akademie
author: Adam Seifert
email: seifert.promotion@gmail.com
"""

from typing import List
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)

# Constants
PLAYER_X = "X"
PLAYER_O = "O"
EMPTY_CELL = " "
SEPARATOR = f"{Fore.CYAN}{'=' * 40}"


class TicTacToe:
    """Class representing the game logic of Tic Tac Toe."""

    def __init__(self) -> None:
        """Initialize a new Tic Tac Toe game."""
        self.board: List[str] = [EMPTY_CELL] * 9
        self.current_player: str = PLAYER_X

    def display_board(self) -> None:
        """Display the current state of the board."""
        print(f"{Fore.MAGENTA}+---+---+---+")
        for i in range(0, 9, 3):
            print(
                f"{Fore.MAGENTA}| {self.colorize_mark(self.board[i])} "
                f"{Fore.MAGENTA}| {self.colorize_mark(self.board[i+1])} "
                f"{Fore.MAGENTA}| {self.colorize_mark(self.board[i+2])} {Fore.MAGENTA}|"
            )
            print(f"{Fore.MAGENTA}+---+---+---+")

    @staticmethod
    def colorize_mark(mark: str) -> str:
        """Colorize the player's mark for display."""
        if mark == PLAYER_X:
            return f"{Fore.RED}{mark}"
        elif mark == PLAYER_O:
            return f"{Fore.BLUE}{mark}"
        return mark

    def is_valid_move(self, move: int) -> bool:
        """Check if the move is valid.

        Args:
            move: The player's move as an integer (1-9).

        Returns:
            True if the move is valid, False otherwise.
        """
        return 1 <= move <= 9 and self.board[move - 1] == EMPTY_CELL

    def make_move(self, move: int) -> None:
        """Place the current player's mark on the board.

        Args:
            move: The player's move as an integer (1-9).
        """
        self.board[move - 1] = self.current_player

    def switch_player(self) -> None:
        """Switch to the other player."""
        self.current_player = PLAYER_O if self.current_player == PLAYER_X else PLAYER_X

    def check_winner(self) -> bool:
        """Check if the current player has won the game.

        Returns:
            True if the current player has won, False otherwise.
        """
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Horizontal
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Vertical
            [0, 4, 8], [2, 4, 6],             # Diagonal
        ]
        return any(all(self.board[i] == self.current_player for i in condition) for condition in win_conditions)

    def is_draw(self) -> bool:
        """Check if the game is a draw.

        Returns:
            True if the board is full and there is no winner, False otherwise.
        """
        return all(cell != EMPTY_CELL for cell in self.board)


def display_welcome() -> None:
    """Display the welcome message and game rules."""
    print(f"{Fore.BLUE}Welcome to Tic Tac Toe")
    print(SEPARATOR)
    print(f"{Fore.MAGENTA}GAME RULES:")
    print(f"{Fore.WHITE}Each player can place one mark ({Fore.RED}X{Fore.WHITE} or {Fore.BLUE}O{Fore.WHITE})")
    print(f"per turn on the {Fore.MAGENTA}3x3 grid.{Fore.WHITE} The {Fore.GREEN}WINNER {Fore.WHITE}is")
    print(f"who {Fore.GREEN}succeeds {Fore.WHITE}in placing three of their")
    print(f"marks in a:")
    print(f"{Fore.GREEN}* {Fore.MAGENTA}Horizontal row")
    print(f"{Fore.GREEN}* {Fore.MAGENTA}Vertical row")
    print(f"{Fore.GREEN}* {Fore.MAGENTA}Diagonal row")
    print(SEPARATOR)
    print(f"{Fore.BLUE}Let's start the game!")
    print(SEPARATOR)


def play_game() -> None:
    """Main function to play Tic Tac Toe."""
    display_welcome()
    game = TicTacToe()

    while True:
        game.display_board()
        print(SEPARATOR)

        try:
            move = int(input(f"Player {Fore.GREEN}{game.current_player}{Fore.WHITE}, please enter your move {Fore.GREEN}(1-9): "))
            if not game.is_valid_move(move):
                raise ValueError("Invalid move. The cell is occupied or out of range.")
        except ValueError as e:
            print(f"{Fore.RED}{e} Please try again.")
            continue

        game.make_move(move)

        if game.check_winner():
            game.display_board()
            print(f"{Fore.GREEN}Congratulations! Player {game.colorize_mark(game.current_player)} wins!")
            break

        if game.is_draw():
            game.display_board()
            print(f"{Fore.GREEN}It's a draw!")
            break

        game.switch_player()


if __name__ == "__main__":
    play_game()
