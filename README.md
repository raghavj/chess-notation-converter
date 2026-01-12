# Chess Notation Converter

Converts old descriptive chess notation (P-K4, N-KB3) to modern algebraic notation (e4, Nf3).

## Usage

```bash
python3 chess_notation_converter.py
```

Enter moves line by line, then press Enter on a blank line when done.

## Example

**Input:**
```
1. P-K4 P-K4
2. N-KB3 N-QB3
3. B-QB4 B-QB4
4. P-QN4 BxQN5
```

**Output:**
```
1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. b4 Bxb4
```

## Tips

- Use full square names: `QB4`, `KB3`, `QN5` (not just `B4`)
- For captures, include target square: `BxQN5` rather than `BxP`
- Knight disambiguation: `KN-K2` (King's Knight) vs `QN-K2` (Queen's Knight)

## Supported Features

- Basic moves: `P-K4`, `N-KB3`, `B-QB4`
- Captures: `BxQN5`, `PxK4`
- Castling: `O-O`, `O-O-O`
- Check/Checkmate: `+`, `++`
- Promotions: `P-K8(Q)`
- Disambiguation: `KN-K2`, `R(1)-Q1`
