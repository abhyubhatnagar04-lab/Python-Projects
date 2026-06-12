import streamlit as st

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Chess",
    page_icon="♟️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;500;600&display=swap');

/* ── Global ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #1a1a2e !important;
    color: #e8e0d0;
    font-family: 'Inter', sans-serif;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none; }
.block-container { padding-top: 1.5rem !important; max-width: 700px !important; }

/* ── Titles ── */
h1 { font-family: 'Playfair Display', serif; font-size: 2rem; color: #f0c040; margin: 0 0 0.2rem; }
.subtitle { font-size: 0.85rem; color: #a09880; letter-spacing: 0.08em; text-transform: uppercase; }

/* ── Board ── */
.board-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 1rem auto;
}
.board-row { display: flex; }
.coord-col {
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    width: 22px;
    text-align: center;
    font-size: 0.75rem;
    color: #a09880;
    user-select: none;
}
.coord-row {
    display: flex;
    justify-content: space-around;
    width: calc(8 * 64px);
    padding: 4px 0;
    font-size: 0.75rem;
    color: #a09880;
    user-select: none;
}
.square {
    width: 64px; height: 64px;
    display: flex; align-items: center; justify-content: center;
    font-size: 2.2rem;
    cursor: pointer;
    border: none;
    transition: filter 0.15s;
    user-select: none;
    line-height: 1;
}
.square:hover { filter: brightness(1.18); }
.sq-light  { background: #f0d9b5; }
.sq-dark   { background: #b58863; }
.sq-selected { outline: 3px inset #f0c040; outline-offset: -3px; filter: brightness(1.1); }
.sq-legal  { position: relative; }
.sq-legal::after {
    content: '';
    position: absolute;
    width: 24px; height: 24px;
    border-radius: 50%;
    background: rgba(20,200,80,0.45);
    pointer-events: none;
}
.sq-last   { background: #cdd16f !important; }
.sq-last.sq-dark { background: #aaa23a !important; }
.sq-check  { background: #e04040 !important; }

/* ── Status bar ── */
.status-bar {
    display: flex; align-items: center; gap: 0.7rem;
    background: #16213e;
    border: 1px solid #2a2a4a;
    border-radius: 8px;
    padding: 0.55rem 1rem;
    margin: 0.4rem 0;
    font-size: 0.92rem;
}
.dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.dot-white { background: #f0f0f0; border: 1px solid #888; }
.dot-black { background: #222; border: 1px solid #888; }
.dot-check { background: #e04040; }

/* ── Move history ── */
.move-table {
    width: 100%; border-collapse: collapse;
    font-size: 0.82rem; font-family: 'Inter', monospace;
}
.move-table th {
    color: #a09880; font-weight: 600;
    padding: 4px 8px; border-bottom: 1px solid #2a2a4a;
    text-align: left;
}
.move-table td { padding: 3px 8px; color: #c8c0b0; }
.move-table tr:last-child td { color: #f0c040; }

/* ── Buttons ── */
.stButton > button {
    background: #16213e;
    border: 1px solid #3a3a6a;
    color: #e8e0d0;
    border-radius: 6px;
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    padding: 0.4rem 1rem;
    transition: border-color 0.2s, background 0.2s;
}
.stButton > button:hover {
    border-color: #f0c040;
    background: #1e2a50;
    color: #f0c040;
}
/* ── Promotion modal ── */
.promo-box {
    background: #16213e; border: 1px solid #3a3a6a;
    border-radius: 10px; padding: 1rem;
    text-align: center;
}
.promo-box h4 { margin: 0 0 0.6rem; color: #f0c040; }
</style>
""", unsafe_allow_html=True)

# ── Piece unicode maps ────────────────────────────────────────────────────────
PIECES = {
    "wK": "♔", "wQ": "♕", "wR": "♖", "wB": "♗", "wN": "♘", "wP": "♙",
    "bK": "♚", "bQ": "♛", "bR": "♜", "bB": "♝", "bN": "♞", "bP": "♟",
}

INIT_BOARD = [
    ["bR","bN","bB","bQ","bK","bB","bN","bR"],
    ["bP","bP","bP","bP","bP","bP","bP","bP"],
    [None]*8, [None]*8, [None]*8, [None]*8,
    ["wP","wP","wP","wP","wP","wP","wP","wP"],
    ["wR","wN","wB","wQ","wK","wB","wN","wR"],
]

# ── Chess logic ───────────────────────────────────────────────────────────────

def copy_board(board):
    return [row[:] for row in board]

def color(piece):
    return piece[0] if piece else None

def kind(piece):
    return piece[1] if piece else None

def in_bounds(r, c):
    return 0 <= r < 8 and 0 <= c < 8

def raw_moves(board, r, c, en_passant_target, castling_rights):
    """Return list of (to_r, to_c) ignoring check."""
    piece = board[r][c]
    if not piece:
        return []
    col, typ = piece[0], piece[1]
    opp = "b" if col == "w" else "w"
    moves = []

    def slide(dr, dc):
        nr, nc = r+dr, c+dc
        while in_bounds(nr, nc):
            if board[nr][nc]:
                if color(board[nr][nc]) == opp:
                    moves.append((nr, nc))
                break
            moves.append((nr, nc))
            nr += dr; nc += dc

    if typ == "R":
        for d in [(1,0),(-1,0),(0,1),(0,-1)]: slide(*d)
    elif typ == "B":
        for d in [(1,1),(1,-1),(-1,1),(-1,-1)]: slide(*d)
    elif typ == "Q":
        for d in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]: slide(*d)
    elif typ == "N":
        for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            nr, nc = r+dr, c+dc
            if in_bounds(nr, nc) and color(board[nr][nc]) != col:
                moves.append((nr, nc))
    elif typ == "K":
        for dr in [-1,0,1]:
            for dc in [-1,0,1]:
                if dr == dc == 0: continue
                nr, nc = r+dr, c+dc
                if in_bounds(nr, nc) and color(board[nr][nc]) != col:
                    moves.append((nr, nc))
        # Castling
        row = 7 if col == "w" else 0
        if r == row and c == 4:
            # Kingside
            if castling_rights.get(col+"K") and not board[row][5] and not board[row][6]:
                moves.append((row, 6))
            # Queenside
            if castling_rights.get(col+"Q") and not board[row][3] and not board[row][2] and not board[row][1]:
                moves.append((row, 2))
    elif typ == "P":
        fwd = -1 if col == "w" else 1
        start_row = 6 if col == "w" else 1
        # Forward
        nr = r + fwd
        if in_bounds(nr, c) and not board[nr][c]:
            moves.append((nr, c))
            # Double push
            if r == start_row and not board[r+2*fwd][c]:
                moves.append((r+2*fwd, c))
        # Captures
        for dc in [-1, 1]:
            nc = c + dc
            if in_bounds(nr, c) and in_bounds(nr, nc):
                if color(board[nr][nc]) == opp:
                    moves.append((nr, nc))
                elif en_passant_target == (nr, nc):
                    moves.append((nr, nc))
    return moves

def find_king(board, col):
    for r in range(8):
        for c in range(8):
            if board[r][c] == col+"K":
                return r, c
    return None

def is_attacked(board, r, c, by_color, en_passant_target, castling_rights):
    """Is square (r,c) attacked by any piece of by_color?"""
    for rr in range(8):
        for cc in range(8):
            if color(board[rr][cc]) == by_color:
                if (r, c) in raw_moves(board, rr, cc, en_passant_target, castling_rights):
                    return True
    return False

def apply_move(board, r, c, nr, nc, castling_rights, en_passant_target):
    """Apply move, return (new_board, new_castling, new_ep_target, captured)."""
    b = copy_board(board)
    piece = b[r][c]
    col, typ = piece[0], piece[1]
    opp = "b" if col == "w" else "w"
    captured = b[nr][nc]
    new_ep = None

    # En passant capture
    if typ == "P" and (nr, nc) == en_passant_target:
        ep_r = r  # the captured pawn is on the same row as moving pawn
        b[ep_r][nc] = None
        captured = col == "w" and "bP" or "wP"

    # Castling move
    if typ == "K" and abs(nc - c) == 2:
        row = r
        if nc == 6:  # kingside
            b[row][5] = b[row][7]; b[row][7] = None
        else:        # queenside
            b[row][3] = b[row][0]; b[row][0] = None

    b[nr][nc] = piece
    b[r][c] = None

    # Double pawn push → en passant target
    if typ == "P" and abs(nr - r) == 2:
        new_ep = ((r + nr) // 2, c)

    # Update castling rights
    new_cr = dict(castling_rights)
    if piece == "wK": new_cr["wK"] = False; new_cr["wQ"] = False
    if piece == "bK": new_cr["bK"] = False; new_cr["bQ"] = False
    if (r, c) == (7, 0) or (nr, nc) == (7, 0): new_cr["wQ"] = False
    if (r, c) == (7, 7) or (nr, nc) == (7, 7): new_cr["wK"] = False
    if (r, c) == (0, 0) or (nr, nc) == (0, 0): new_cr["bQ"] = False
    if (r, c) == (0, 7) or (nr, nc) == (0, 7): new_cr["bK"] = False

    return b, new_cr, new_ep, captured

def legal_moves(board, r, c, en_passant_target, castling_rights):
    """Return legal moves for piece at (r,c)."""
    piece = board[r][c]
    if not piece: return []
    col = piece[0]
    opp = "b" if col == "w" else "w"
    result = []
    for (nr, nc) in raw_moves(board, r, c, en_passant_target, castling_rights):
        b2, cr2, ep2, _ = apply_move(board, r, c, nr, nc, castling_rights, en_passant_target)
        kr, kc = find_king(b2, col)
        if not is_attacked(b2, kr, kc, opp, ep2, cr2):
            # Castling: king must not pass through check
            if piece[1] == "K" and abs(nc - c) == 2:
                mid_c = (c + nc) // 2
                b_mid, _, _, _ = apply_move(board, r, c, r, mid_c, castling_rights, en_passant_target)
                if is_attacked(board, r, c, opp, en_passant_target, castling_rights): continue
                if is_attacked(b_mid, r, mid_c, opp, en_passant_target, castling_rights): continue
            result.append((nr, nc))
    return result

def all_legal_moves(board, col, en_passant_target, castling_rights):
    moves = []
    for r in range(8):
        for c in range(8):
            if color(board[r][c]) == col:
                for m in legal_moves(board, r, c, en_passant_target, castling_rights):
                    moves.append((r, c, m[0], m[1]))
    return moves

def is_in_check(board, col, en_passant_target, castling_rights):
    opp = "b" if col == "w" else "w"
    kr, kc = find_king(board, col)
    return is_attacked(board, kr, kc, opp, en_passant_target, castling_rights)

def move_to_san(board, r, c, nr, nc, en_passant_target, promo=None):
    """Minimal SAN-ish notation for the move history."""
    piece = board[r][c]
    if not piece: return "?"
    typ = piece[1]
    files = "abcdefgh"
    if typ == "K" and abs(nc - c) == 2:
        return "O-O" if nc == 6 else "O-O-O"
    cap = "x" if board[nr][nc] or (typ == "P" and (nr, nc) == en_passant_target) else ""
    if typ == "P":
        from_str = files[c] + cap if cap else ""
        to_str = files[nc] + str(8 - nr)
        s = from_str + to_str
        if promo: s += "=" + promo
        return s
    return typ + cap + files[nc] + str(8 - nr)

# ── Session state ─────────────────────────────────────────────────────────────

def init_state():
    st.session_state.board = copy_board(INIT_BOARD)
    st.session_state.turn = "w"
    st.session_state.selected = None
    st.session_state.legal = []
    st.session_state.last_move = None
    st.session_state.castling = {"wK": True, "wQ": True, "bK": True, "bQ": True}
    st.session_state.en_passant = None
    st.session_state.history = []          # list of SAN strings
    st.session_state.status = "white"      # "white","black","check","checkmate","stalemate","draw"
    st.session_state.promotion_pending = None  # (r,c,nr,nc) awaiting promo choice
    st.session_state.captured_w = []       # pieces white captured
    st.session_state.captured_b = []

if "board" not in st.session_state:
    init_state()

S = st.session_state

# ── Handle promotion ──────────────────────────────────────────────────────────

def finish_move(r, c, nr, nc, promo=None):
    board, castling, ep = S.board, S.castling, S.en_passant
    san = move_to_san(board, r, c, nr, nc, ep, promo)
    new_board, new_cr, new_ep, captured = apply_move(board, r, c, nr, nc, castling, ep)

    # Apply promotion
    if promo:
        new_board[nr][nc] = S.turn + promo

    if captured:
        if color(captured) == "w":
            S.captured_w.append(captured)
        else:
            S.captured_b.append(captured)

    S.board = new_board
    S.castling = new_cr
    S.en_passant = new_ep
    S.last_move = (r, c, nr, nc)
    S.history.append(san)
    S.selected = None
    S.legal = []
    S.promotion_pending = None

    # Switch turn
    next_col = "b" if S.turn == "w" else "w"
    S.turn = next_col

    # Determine status
    moves = all_legal_moves(new_board, next_col, new_ep, new_cr)
    in_check = is_in_check(new_board, next_col, new_ep, new_cr)
    if not moves:
        S.status = "checkmate" if in_check else "stalemate"
    elif in_check:
        S.status = "check"
    else:
        S.status = "white" if next_col == "w" else "black"

# ── Handle square click ───────────────────────────────────────────────────────

def on_square_click(r, c):
    if S.status in ("checkmate", "stalemate"):
        return
    if S.promotion_pending:
        return

    board = S.board
    piece = board[r][c]

    if S.selected is None:
        if piece and color(piece) == S.turn:
            S.selected = (r, c)
            S.legal = legal_moves(board, r, c, S.en_passant, S.castling)
    else:
        sr, sc = S.selected
        if (r, c) in S.legal:
            # Check promotion
            moving = board[sr][sc]
            if moving and moving[1] == "P" and (r == 0 or r == 7):
                S.promotion_pending = (sr, sc, r, c)
            else:
                finish_move(sr, sc, r, c)
        elif piece and color(piece) == S.turn and (r, c) != S.selected:
            S.selected = (r, c)
            S.legal = legal_moves(board, r, c, S.en_passant, S.castling)
        else:
            S.selected = None
            S.legal = []

# ── URL param buttons ─────────────────────────────────────────────────────────

for key in st.query_params:
    if key.startswith("sq_"):
        _, r, c = key.split("_")
        on_square_click(int(r), int(c))
        st.query_params.clear()
        st.rerun()

# ── Layout ────────────────────────────────────────────────────────────────────

st.markdown('<h1>♟ Chess</h1><div class="subtitle">Two-player · Classic rules</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

col_board, col_info = st.columns([3, 1.4], gap="medium")

with col_board:
    board = S.board
    legal_set = set(S.legal)
    lm = S.last_move  # (r,c,nr,nc) or None
    last_set = {(lm[0], lm[1]), (lm[2], lm[3])} if lm else set()

    # Check king square
    check_sq = None
    if S.status in ("check", "checkmate"):
        check_sq = find_king(board, S.turn)

    # Build board HTML
    files = "abcdefgh"
    ranks = "87654321"

    html = '<div class="board-wrapper">'
    # Rank coords left + board rows
    html += '<div style="display:flex; align-items:center;">'
    html += '<div class="coord-col">'
    for rk in ranks:
        html += f'<span>{rk}</span>'
    html += '</div>'
    html += '<div>'

    for r in range(8):
        html += '<div class="board-row">'
        for c in range(8):
            light = (r + c) % 2 == 0
            classes = ["square", "sq-light" if light else "sq-dark"]
            if S.selected == (r, c):
                classes.append("sq-selected")
            elif (r, c) in legal_set:
                classes.append("sq-legal")
            if (r, c) in last_set and S.selected != (r, c):
                classes.append("sq-last")
            if check_sq == (r, c):
                classes.append("sq-check")

            piece = board[r][c]
            sym = PIECES.get(piece, "") if piece else ""
            cls = " ".join(classes)
            # Use a form button approach via query params
            html += (
                f'<button class="{cls}" '
                f'onclick="window.location.search=\'?sq_{r}_{c}=1\'" '
                f'title="{files[c]}{ranks[r]}">{sym}</button>'
            )
        html += '</div>'

    html += '</div></div>'
    # File coords bottom
    html += '<div class="coord-row">'
    for f in files:
        html += f'<span>{f}</span>'
    html += '</div>'
    html += '</div>'

    st.markdown(html, unsafe_allow_html=True)

    # Promotion modal
    if S.promotion_pending:
        sr, sc, nr, nc = S.promotion_pending
        promo_col = S.turn
        pieces_to_choose = ["Q", "R", "B", "N"]
        st.markdown('<div class="promo-box"><h4>Promote pawn to:</h4></div>', unsafe_allow_html=True)
        pcols = st.columns(4)
        for i, p in enumerate(pieces_to_choose):
            with pcols[i]:
                sym = PIECES[promo_col + p]
                if st.button(sym, key=f"promo_{p}", use_container_width=True):
                    finish_move(sr, sc, nr, nc, promo=p)
                    st.rerun()

with col_info:
    # Status
    status_msgs = {
        "white":      ("dot-white", "White to move"),
        "black":      ("dot-black", "Black to move"),
        "check":      ("dot-check", f"{'White' if S.turn=='w' else 'Black'} in check!"),
        "checkmate":  ("dot-check", f"Checkmate! {'Black' if S.turn=='w' else 'White'} wins 🎉"),
        "stalemate":  ("dot-white", "Stalemate — Draw"),
        "draw":       ("dot-white", "Draw"),
    }
    dot_cls, msg = status_msgs.get(S.status, ("dot-white", ""))
    st.markdown(
        f'<div class="status-bar"><div class="dot {dot_cls}"></div><span>{msg}</span></div>',
        unsafe_allow_html=True,
    )

    # Captured pieces
    cap_b_str = " ".join(PIECES.get(p, "") for p in S.captured_b) or "—"
    cap_w_str = " ".join(PIECES.get(p, "") for p in S.captured_w) or "—"
    st.markdown(
        f'<div class="status-bar" style="flex-wrap:wrap;gap:4px;">'
        f'<span style="color:#a09880;font-size:0.78rem;">♙ took:</span> {cap_b_str}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="status-bar" style="flex-wrap:wrap;gap:4px;">'
        f'<span style="color:#a09880;font-size:0.78rem;">♟ took:</span> {cap_w_str}</div>',
        unsafe_allow_html=True,
    )

    # Move history
    st.markdown("<br>", unsafe_allow_html=True)
    if S.history:
        hist_html = '<table class="move-table"><tr><th>#</th><th>White</th><th>Black</th></tr>'
        for i in range(0, len(S.history), 2):
            move_num = i // 2 + 1
            w_move = S.history[i]
            b_move = S.history[i+1] if i+1 < len(S.history) else ""
            hist_html += f'<tr><td>{move_num}.</td><td>{w_move}</td><td>{b_move}</td></tr>'
        hist_html += '</table>'
        st.markdown(hist_html, unsafe_allow_html=True)
    else:
        st.markdown('<span style="color:#6a6a8a;font-size:0.82rem;">No moves yet</span>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("↺ New game", use_container_width=True):
        init_state()
        st.rerun()
