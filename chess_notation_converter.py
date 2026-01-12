#!/usr/bin/env python3
"""
Chess Notation Converter: Descriptive to Algebraic Notation
Converts old descriptive notation (P-K4, N-KB3) to algebraic (e4, Nf3)
"""

import re

# Piece mappings (base pieces)
PIECES = {
    'K': 'K', 'Q': 'Q', 'R': 'R', 'B': 'B', 'N': 'N', 'Kt': 'N', 'P': ''
}

# Extended piece mappings with side prefixes (for disambiguation)
# KN = King's Knight, QN = Queen's Knight, KB = King's Bishop, etc.
EXTENDED_PIECES = {
    'KN': ('N', 'g'), 'QN': ('N', 'b'),  # Knights with file disambiguation
    'KKt': ('N', 'g'), 'QKt': ('N', 'b'),
    'KB': ('B', 'f'), 'QB': ('B', 'c'),  # Bishops with file disambiguation
    'KR': ('R', 'h'), 'QR': ('R', 'a'),  # Rooks with file disambiguation
}

# File mappings from descriptive to algebraic
# In descriptive notation, files are the same for both players
# QR=a, QN=b, QB=c, Q=d, K=e, KB=f, KN=g, KR=h
FILES = {
    'QR': 'a', 'QN': 'b', 'QKt': 'b', 'QB': 'c', 'Q': 'd',
    'K': 'e', 'KB': 'f', 'KN': 'g', 'KKt': 'g', 'KR': 'h'
}

def parse_descriptive_square(square_str, is_white):
    """Parse a descriptive square like 'K4', 'QB3', 'B4' to algebraic."""
    square_str = square_str.strip()

    # Match patterns: QR1-8, QN1-8, QB1-8, Q1-8, K1-8, KB1-8, KN1-8, KR1-8
    # Also handle short forms like B4 (assume KB)
    patterns = [
        (r'^(QR|QKt|QN|QB|KR|KKt|KN|KB)(\d)$', lambda m: (m.group(1), m.group(2))),
        (r'^(Q|K)(\d)$', lambda m: (m.group(1), m.group(2))),
        # Short forms - B4 typically means KB4
        (r'^(R)(\d)$', lambda m: ('KR', m.group(2))),
        (r'^(N)(\d)$', lambda m: ('KN', m.group(2))),
        (r'^(B)(\d)$', lambda m: ('KB', m.group(2))),
    ]

    file_desc = None
    rank_desc = None

    for pattern, extractor in patterns:
        match = re.match(pattern, square_str)
        if match:
            file_desc, rank_desc = extractor(match)
            break

    if file_desc is None:
        return None

    file_alg = FILES.get(file_desc)
    if file_alg is None:
        return None

    # Rank conversion: each player counts from their own side
    # White's rank 4 = algebraic rank 4
    # Black's rank 4 = algebraic rank 5 (9 - 4 = 5)
    rank_num = int(rank_desc)
    if is_white:
        rank_alg = str(rank_num)
    else:
        rank_alg = str(9 - rank_num)

    return file_alg + rank_alg

def convert_move(move_str, is_white):
    """Convert a single descriptive move to algebraic notation."""
    move_str = move_str.strip()
    original = move_str

    # Handle castling
    if move_str.upper() in ['O-O', '0-0'] or 'CASTLES KR' in move_str.upper() or move_str.upper() == 'CASTLES K':
        return 'O-O'
    if move_str.upper() in ['O-O-O', '0-0-0'] or 'CASTLES QR' in move_str.upper() or move_str.upper() == 'CASTLES Q':
        return 'O-O-O'

    # Handle check/checkmate symbols
    check_suffix = ''
    if move_str.endswith('++') or move_str.endswith(' mate'):
        check_suffix = '#'
        move_str = move_str.replace(' mate', '').rstrip('+#')
    elif move_str.endswith('+') or move_str.endswith('ch') or move_str.endswith(' ch'):
        check_suffix = '+'
        move_str = move_str.replace(' ch', '').rstrip('+')
        if move_str.endswith('ch'):
            move_str = move_str[:-2]

    # Handle 'e.p.' for en passant
    move_str = re.sub(r'\s*e\.?p\.?', '', move_str)

    # Handle promotion: (Q), =Q, /Q, etc.
    promotion = ''
    promo_match = re.search(r'\(([QRBN])\)$|=([QRBN])$|/([QRBN])$', move_str)
    if promo_match:
        promotion = '=' + (promo_match.group(1) or promo_match.group(2) or promo_match.group(3))
        move_str = re.sub(r'\([QRBN]\)$|=[QRBN]$|/[QRBN]$', '', move_str)

    # Determine if capture
    is_capture = 'x' in move_str.lower()
    move_str = re.sub(r'[xX]', '-', move_str)

    # Split on hyphen
    parts = move_str.split('-')
    if len(parts) != 2:
        return f"{original}[?]"

    piece_part = parts[0].strip()
    dest_part = parts[1].strip()

    # Extract piece and any disambiguation
    piece = ''
    disambig = ''

    # Check for disambiguation: R(1), R(QR), N(Q), etc.
    disambig_match = re.match(r'^(K|Q|R|B|N|Kt|P)\((.+)\)$', piece_part)
    if disambig_match:
        piece_char = disambig_match.group(1)
        disambig_hint = disambig_match.group(2)
        piece = PIECES.get(piece_char, piece_char)

        if disambig_hint.isdigit():
            if is_white:
                disambig = disambig_hint
            else:
                disambig = str(9 - int(disambig_hint))
        else:
            d = FILES.get(disambig_hint)
            if d:
                disambig = d
    elif piece_part in EXTENDED_PIECES:
        # Handle KN, QN, KB, QB, KR, QR prefixes
        piece, disambig = EXTENDED_PIECES[piece_part]
    else:
        piece = PIECES.get(piece_part, piece_part if len(piece_part) == 1 else '')

    # Parse destination square
    dest_square = parse_descriptive_square(dest_part, is_white)

    # If dest couldn't be parsed as square, might be capturing a piece (PxP, BxN)
    if dest_square is None:
        # This is "capturing piece by name" notation - ambiguous without board state
        if dest_part in PIECES or dest_part in ['P', 'N', 'B', 'R', 'Q', 'Kt', 'NP', 'BP', 'RP', 'QP', 'KP',
                                                   'QRP', 'QNP', 'QBP', 'KBP', 'KNP', 'KRP']:
            # Mark as needing square - user may need to fill in
            captured = PIECES.get(dest_part, dest_part)
            return f"{piece}x{captured}?"
        return f"{original}[?]"

    # Build algebraic notation
    capture_sym = 'x' if is_capture else ''

    # For pawn captures, we need the source file in algebraic
    if piece == '' and is_capture:
        # Try to get source file from piece_part like "QBP", "KP", etc.
        pawn_files = {
            'QRP': 'a', 'QNP': 'b', 'QBP': 'c', 'QP': 'd',
            'KP': 'e', 'KBP': 'f', 'KNP': 'g', 'KRP': 'h',
            'P': ''  # Generic pawn - can't determine file
        }
        piece = pawn_files.get(piece_part, '')

    result = piece + disambig + capture_sym + dest_square + promotion + check_suffix
    return result

def convert_game(game_text):
    """Convert a full game from descriptive to algebraic notation."""
    lines = game_text.strip().split('\n')
    algebraic_moves = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        # Try to parse "1. P-K4 P-K4" format (move number with both moves)
        match = re.match(r'^(\d+)\.\s*([^\s]+)\s+([^\s]+)$', line)
        if match:
            num, white_move, black_move = match.groups()
            white_alg = convert_move(white_move, is_white=True)
            black_alg = convert_move(black_move, is_white=False)
            algebraic_moves.append(f"{num}. {white_alg} {black_alg}")
            continue

        # Try "1. P-K4" format (white only)
        white_match = re.match(r'^(\d+)\.\s*([^\s]+)$', line)
        if white_match:
            num, white_move = white_match.groups()
            white_alg = convert_move(white_move, is_white=True)
            algebraic_moves.append(f"{num}. {white_alg}")
            continue

        # Try "1... P-K4" (black only)
        black_match = re.match(r'^(\d+)\.\.\.\s*([^\s]+)$', line)
        if black_match:
            num, black_move = black_match.groups()
            black_alg = convert_move(black_move, is_white=False)
            algebraic_moves.append(f"{num}... {black_alg}")
            continue

        # Fallback: space/comma separated moves
        moves = re.split(r'[,\s]+', line)
        moves = [m for m in moves if m and not re.match(r'^\d+\.?$', m)]

        for i, m in enumerate(moves):
            is_white = (i % 2 == 0)
            alg = convert_move(m, is_white=is_white)
            move_num = (len(algebraic_moves)) + 1
            if is_white:
                algebraic_moves.append(f"{move_num}. {alg}")
            else:
                if algebraic_moves:
                    algebraic_moves[-1] += f" {alg}"
                else:
                    algebraic_moves.append(f"1... {alg}")

    return algebraic_moves

def main():
    print("Chess Notation Converter: Descriptive -> Algebraic")
    print("=" * 50)
    print("Enter moves in descriptive notation.")
    print("Format: '1. P-K4 P-K4' (one move pair per line)")
    print()
    print("Tips for best results:")
    print("  - Use full squares: QB4, KB3, QN5 (not just B4, N5)")
    print("  - Captures like 'BxP' need target squares: 'BxQB7'")
    print()
    print("Enter blank line when done.\n")

    lines = []
    while True:
        try:
            line = input()
            if line.strip().lower() in ['', 'done']:
                break
            lines.append(line)
        except EOFError:
            break

    if not lines:
        print("No moves entered.")
        return

    game_text = '\n'.join(lines)
    result = convert_game(game_text)

    print("\n" + "=" * 50)
    print("ALGEBRAIC NOTATION (copy-paste ready):")
    print("=" * 50 + "\n")

    # Single line format
    moves_inline = ' '.join(result)
    print(moves_inline)

    print("\n" + "-" * 50)
    print("One move per line:")
    print("-" * 50)
    for move in result:
        print(move)

if __name__ == '__main__':
    main()
