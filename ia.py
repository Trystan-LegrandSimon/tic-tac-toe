#!/usr/local/bin/python3.12

import random

def ia(board, signe):
    # Fonction d'IA simple : Choix aléatoire parmi les positions non occupées
    positions_libres = [i for i, cell in enumerate(board) if cell == 0]
    
    if positions_libres:
        return random.choice(positions_libres)
    else:
        return False
