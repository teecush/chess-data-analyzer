"""
PGN analyzer utilities for Chess Analytics Dashboard
"""

import pandas as pd
import re
import chess.pgn
import io

def parse_pgn_game(pgn_text):
    """Parse a single PGN game and extract metadata"""
    try:
        game = chess.pgn.read_game(io.StringIO(pgn_text))
        if game is None:
            return None
        
        # Extract game headers
        headers = game.headers
        
        # Extract moves
        moves = []
        board = game.board()
        for move in game.mainline_moves():
            moves.append(board.san(move))
            board.push(move)
        
        return {
            'event': headers.get('Event', ''),
            'site': headers.get('Site', ''),
            'date': headers.get('Date', ''),
            'white': headers.get('White', ''),
            'black': headers.get('Black', ''),
            'result': headers.get('Result', ''),
            'opening': headers.get('Opening', ''),
            'variation': headers.get('Variation', ''),
            'moves': moves,
            'move_count': len(moves)
        }
    except Exception as e:
        print(f"Error parsing PGN: {e}")
        return None

def extract_opening_from_pgn(pgn_text):
    """Extract opening information from PGN text"""
    if not pgn_text:
        return None, None
    
    # Try to extract from headers first
    opening_match = re.search(r'\[Opening\s+"([^"]+)"\]', pgn_text)
    variation_match = re.search(r'\[Variation\s+"([^"]+)"\]', pgn_text)
    
    opening = opening_match.group(1) if opening_match else None
    variation = variation_match.group(1) if variation_match else None
    
    return opening, variation

def analyze_game_quality(pgn_text):
    """Analyze game quality from PGN"""
    game_data = parse_pgn_game(pgn_text)
    if not game_data:
        return None
    
    # Basic quality metrics
    move_count = game_data['move_count']
    
    # Categorize game length
    if move_count < 20:
        game_length = "Short"
    elif move_count < 40:
        game_length = "Medium"
    else:
        game_length = "Long"
    
    return {
        'move_count': move_count,
        'game_length': game_length,
        'opening': game_data['opening'],
        'variation': game_data['variation']
    }
