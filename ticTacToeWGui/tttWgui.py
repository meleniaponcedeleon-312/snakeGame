#!/usr/bin/env python3
"""
Tic-Tac-Toe GUI (Tkinter)
- Modes: Two-player local OR Single-player vs Computer
- Computer difficulties: Random (easy) or Unbeatable (Minimax)
Save as tictactoe_gui.py and run with python3.
"""

import tkinter as tk
from tkinter import messagebox
import random
import math

WIN_COMBINATIONS = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6)
]


class TicTacToeApp:
    def __init__(self, root):
        self.root = root
        root.title("Tic-Tac-Toe")

        # Options (bound to UI)
        self.mode = tk.StringVar(value="1p")          # '1p' or '2p'
        self.human_symbol = tk.StringVar(value="X")  # 'X' or 'O' (when playing vs computer)
        self.ai_difficulty = tk.StringVar(value="unbeatable")  # 'random' or 'unbeatable'

        # Game state
        self.board = [' '] * 9
        self.buttons = []         # 9 buttons for the grid
        self.current_player = 'X' # whose turn it is now ('X' always starts)
        self.game_over = False

        self.build_ui()
        self.new_game()

    def build_ui(self):
        # Title / status
        header = tk.Label(self.root, text="Tic-Tac-Toe", font=("Helvetica", 18, "bold"))
        header.grid(row=0, column=0, columnspan=2, pady=(8, 0))

        # Board frame
        board_frame = tk.Frame(self.root)
        board_frame.grid(row=1, column=0, padx=10, pady=10)

        btn_font = ("Helvetica", 28, "bold")
        for i in range(9):
            b = tk.Button(board_frame, text="", font=btn_font, width=4, height=2,
                          command=lambda i=i: self.on_cell_clicked(i))
            b.grid(row=i // 3, column=i % 3, sticky="nsew", padx=3, pady=3)
            self.buttons.append(b)

        # Make grid cells expand (optional, helpful if window is resized)
        for r in range(3):
            board_frame.rowconfigure(r, weight=1)
        for c in range(3):
            board_frame.columnconfigure(c, weight=1)

        # Controls frame
        ctrl = tk.Frame(self.root)
        ctrl.grid(row=1, column=1, sticky="n", padx=(0, 10), pady=10)

        # Mode selection
        tk.Label(ctrl, text="Mode:", font=("Helvetica", 10, "bold")).pack(anchor="w")
        tk.Radiobutton(ctrl, text="Single player (vs Computer)", variable=self.mode, value="1p",
                       command=self.new_game).pack(anchor="w")
        tk.Radiobutton(ctrl, text="Two players (local)", variable=self.mode, value="2p",
                       command=self.new_game).pack(anchor="w")

        tk.Label(ctrl, text="").pack()  # spacer

        # Human symbol selection (affects who goes first if human picks 'O')
        tk.Label(ctrl, text="Your symbol (vs Computer):").pack(anchor="w")
        sym_frame = tk.Frame(ctrl)
        sym_frame.pack(anchor="w", pady=(0, 6))
        tk.Radiobutton(sym_frame, text="X (goes first)", variable=self.human_symbol, value="X",
                       state="normal", command=self.new_game).pack(side="left")
        tk.Radiobutton(sym_frame, text="O", variable=self.human_symbol, value="O",
                       state="normal", command=self.new_game).pack(side="left")

        # Difficulty
        tk.Label(ctrl, text="Computer difficulty:").pack(anchor="w")
        tk.Radiobutton(ctrl, text="Easy (random)", variable=self.ai_difficulty, value="random",
                       command=self.new_game).pack(anchor="w")
        tk.Radiobutton(ctrl, text="Unbeatable (Minimax)", variable=self.ai_difficulty, value="unbeatable",
                       command=self.new_game).pack(anchor="w")

        tk.Label(ctrl, text="").pack()  # spacer

        # Action buttons
        tk.Button(ctrl, text="Start New Game", command=self.new_game).pack(fill="x", pady=(4, 2))
        tk.Button(ctrl, text="Quit", command=self.root.quit).pack(fill="x")

        # Status label
        self.status_label = tk.Label(self.root, text="", font=("Helvetica", 12))
        self.status_label.grid(row=2, column=0, columnspan=2, pady=(6, 10))

    def new_game(self):
        """Reset board and possibly let the AI play first if it's X and human chose O."""
        self.board = [' '] * 9
        self.current_player = 'X'  # X always starts
        self.game_over = False
        for b in self.buttons:
            b.config(text="", state="normal")
        self.update_status()

        # If single-player and the human chose O, computer (X) should move first
        if self.mode.get() == "1p" and self.human_symbol.get() == "O":
            # schedule AI move a touch later so UI updates cleanly
            self.root.after(150, self.ai_move)

    def on_cell_clicked(self, index):
        if self.game_over:
            return

        # If playing vs computer, ignore clicks when it's the AI's turn
        if self.mode.get() == "1p" and self.current_player != self.human_symbol.get():
            return

        if self.board[index] != ' ':
            return

        self.make_move(index, self.current_player)

        winner = self.check_winner(self.board)
        if winner:
            self.end_game(winner)
            return
        if self.is_draw(self.board):
            self.end_game(None)
            return

        # switch player
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        self.update_status()

        # If single-player and it's now the AI's turn, run AI move
        if self.mode.get() == "1p" and self.current_player != self.human_symbol.get():
            # small delay so the click appears responsive before the AI calculates
            self.root.after(150, self.ai_move)

    def make_move(self, index, player):
        """Apply a move to the internal board and update the button."""
        self.board[index] = player
        self.buttons[index].config(text=player, state="disabled")
        self.update_status()

    def ai_move(self):
        if self.game_over:
            return
        ai_player = 'O' if self.human_symbol.get() == 'X' else 'X'
        human = self.human_symbol.get()

        moves = [i for i, c in enumerate(self.board) if c == ' ']
        if not moves:
            return

        if self.ai_difficulty.get() == 'random':
            chosen = random.choice(moves)
        else:
            # Unbeatable: use Minimax
            _, chosen = self.minimax(self.board[:], 0, True, ai_player, human)

            # If minimax returned None for some reason, fallback to random
            if chosen is None:
                chosen = random.choice(moves)

        # Make the move
        self.make_move(chosen, ai_player)

        # Check end conditions
        winner = self.check_winner(self.board)
        if winner:
            self.end_game(winner)
            return
        if self.is_draw(self.board):
            self.end_game(None)
            return

        # Switch back to human
        self.current_player = human
        self.update_status()

    def update_status(self):
        if self.game_over:
            return
        mode_text = "Two players" if self.mode.get() == "2p" else "Single player"
        self.status_label.config(
            text=f"Mode: {mode_text} — Turn: {self.current_player}"
        )

    def end_game(self, winner):
        self.game_over = True
        for b in self.buttons:
            b.config(state="disabled")

        if winner is None:
            self.status_label.config(text="It's a draw!")
            messagebox.showinfo("Game over", "It's a draw!")
        else:
            self.status_label.config(text=f"Player {winner} wins!")
            messagebox.showinfo("Game over", f"Player {winner} wins!")

    @staticmethod
    def check_winner(board):
        for a, b, c in WIN_COMBINATIONS:
            if board[a] != ' ' and board[a] == board[b] == board[c]:
                return board[a]
        return None

    @staticmethod
    def is_draw(board):
        return all(cell != ' ' for cell in board) and TicTacToeApp.check_winner(board) is None

    def minimax(self, board, depth, is_maximizing, ai_player, human_player):
        """
        Minimax with depth scoring:
         - If ai wins: 10 - depth  (prefer fast wins)
         - If human wins: depth - 10 (prefer slow losses)
         - Draw: 0
        Returns (score, best_move_index)
        """
        winner = TicTacToeApp.check_winner(board)
        if winner == ai_player:
            return 10 - depth, None
        if winner == human_player:
            return depth - 10, None
        if all(cell != ' ' for cell in board):
            return 0, None

        moves = [i for i, c in enumerate(board) if c == ' ']

        if is_maximizing:
            best_score = -math.inf
            best_move = None
            for m in moves:
                board[m] = ai_player
                score, _ = self.minimax(board, depth + 1, False, ai_player, human_player)
                board[m] = ' '
                if score > best_score:
                    best_score = score
                    best_move = m
            return best_score, best_move
        else:
            best_score = math.inf
            best_move = None
            for m in moves:
                board[m] = human_player
                score, _ = self.minimax(board, depth + 1, True, ai_player, human_player)
                board[m] = ' '
                if score < best_score:
                    best_score = score
                    best_move = m
            return best_score, best_move


if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeApp(root)
    root.mainloop()
