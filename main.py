#!/usr/local/bin/python3.12

import tkinter as tk
from itertools import cycle
from tkinter import font
from typing import NamedTuple

# Définition d'une classe Player pour représenter un joueur avec une étiquette et une couleur
class Player(NamedTuple):
    label: str
    color: str

# Définition d'une classe Move pour représenter un mouvement avec des coordonnées et une étiquette
class Move(NamedTuple):
    row: int
    col: int
    label: str = ""

# Classe principale représentant le jeu Tic-Tac-Toe
class TicTacToeGame:
    def __init__(self, players=None, board_size=3):
        self.players = players or [
            Player(label="X", color="blue"),
            Player(label="O", color="green"),
        ]
        self.current_player_cycle = cycle(self.players)
        self.current_player = next(self.current_player_cycle)
        self.board_size = board_size
        self.winner_combo = []
        self._current_moves = [[Move(row, col) for col in range(self.board_size)] for row in range(self.board_size)]
        self._has_winner = False
        self._winning_combos = self._get_winning_combos()

    # Méthode pour obtenir les combinaisons gagnantes possibles sur le plateau
    def _get_winning_combos(self):
        rows = [[(move.row, move.col) for move in row] for row in self._current_moves]
        columns = [list(col) for col in zip(*rows)]
        first_diagonal = [row[i] for i, row in enumerate(rows)]
        second_diagonal = [col[j] for j, col in enumerate(reversed(columns))]
        return rows + columns + [first_diagonal, second_diagonal]

    # Méthode pour passer au joueur suivant dans le cycle
    def toggle_player(self):
        self.current_player = next(self.current_player_cycle)

    # Méthode pour vérifier si un mouvement est valide
    def is_valid_move(self, move):
        row, col = move.row, move.col
        move_was_not_played = self._current_moves[row][col].label == ""
        no_winner = not self._has_winner
        return no_winner and move_was_not_played

    # Méthode pour traiter un mouvement et vérifier s'il entraîne une victoire
    def process_move(self, move):
        row, col = move.row, move.col
        self._current_moves[row][col] = move
        for combo in self._winning_combos:
            results = set(self._current_moves[n][m].label for n, m in combo)
            is_win = (len(results) == 1) and ("" not in results)
            if is_win:
                self._has_winner = True
                self.winner_combo = combo
                break

    # Méthode pour vérifier s'il y a un gagnant
    def has_winner(self):
        return self._has_winner

    # Méthode pour vérifier s'il y a une égalité
    def is_tied(self):
        no_winner = not self._has_winner
        played_moves = (move.label for row in self._current_moves for move in row)
        return no_winner and all(played_moves)

    # Méthode pour réinitialiser le jeu
    def reset_game(self):
        for row, row_content in enumerate(self._current_moves):
            for col, _ in enumerate(row_content):
                row_content[col] = Move(row, col)
        self._has_winner = False
        self.winner_combo = []

# Classe principale représentant l'interface graphique du plateau Tic-Tac-Toe
class TicTacToeBoard(tk.Tk):
    def __init__(self, game):
        super().__init__()
        self.title("Tic-Tac-Toe Game")
        self._cells = {}
        self._game = game
        self._create_menu()
        self._create_board_display()
        self._create_board_grid()

    # Méthode pour créer le menu
    def _create_menu(self):
        menu_bar = tk.Menu(master=self)
        self.config(menu=menu_bar)
        file_menu = tk.Menu(master=menu_bar)
        file_menu.add_command(label="Rejouer !", command=self.reset_board)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=quit)
        menu_bar.add_cascade(label="Options", menu=file_menu)

    # Méthode pour créer l'affichage du plateau
    def _create_board_display(self):
        display_frame = tk.Frame(master=self)
        display_frame.pack(fill=tk.X)
        self.display = tk.Label(
            master=display_frame,
            text="Prêt à jouer ?",
            font=font.Font(size=28, weight="bold"),
        )
        self.display.pack()

    # Méthode pour créer la grille du plateau
    def _create_board_grid(self):
        grid_frame = tk.Frame(master=self)
        grid_frame.pack()
        for row in range(self._game.board_size):
            self.rowconfigure(row, weight=1, minsize=50)
            self.columnconfigure(row, weight=1, minsize=75)
            for col in range(self._game.board_size):
                button = tk.Button(
                    master=grid_frame,
                    text="",
                    font=font.Font(size=36, weight="bold"),
                    fg="black",
                    width=3,
                    height=2,
                    highlightbackground="lightblue",
                )
                self._cells[button] = (row, col)
                button.bind("<ButtonPress-1>", self.play)
                button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

    # Méthode appelée lorsqu'un bouton est pressé
    def play(self, event):
        clicked_btn = event.widget
        row, col = self._cells[clicked_btn]
        move = Move(row, col, self._game.current_player.label)
        if self._game.is_valid_move(move):
            self._update_button(clicked_btn)
            self._game.process_move(move)
            if self._game.is_tied():
                self._update_display(msg="Partie à égalité !", color="red")
            elif self._game.has_winner():
                self._highlight_cells()
                msg = f'Joueur "{self._game.current_player.label}" à gagné !'
                color = self._game.current_player.color
                self._update_display(msg, color)
            else:
                self._game.toggle_player()
                msg = f"Au tour de : {self._game.current_player.label}"
                self._update_display(msg)

    # Méthode pour mettre à jour l'apparence d'un bouton après un mouvement
    def _update_button(self, clicked_btn):
        clicked_btn.config(text=self._game.current_player.label)
        clicked_btn.config(fg=self._game.current_player.color)

    # Méthode pour mettre à jour l'affichage en bas du plateau
    def _update_display(self, msg, color="black"):
        self.display["text"] = msg
        self.display["fg"] = color

    # Méthode pour mettre en surbrillance les cellules gagnantes
    def _highlight_cells(self):
        for button, coordinates in self._cells.items():
            if coordinates in self._game.winner_combo:
                button.config(highlightbackground="red")

    # Méthode pour réinitialiser le plateau
    def reset_board(self):
        self._game.reset_game()
        self._update_display(msg="Prêt ?")
        for button in self._cells.keys():
            button.config(highlightbackground="lightblue")
            button.config(text="")
            button.config(fg="black")

# Fonction principale pour lancer le jeu
def main():
    game = TicTacToeGame()
    board = TicTacToeBoard(game)
    board.mainloop()

# Point d'entrée du programme
if __name__ == "__main__":
    main()
    