import streamlit as st

st.set_page_config(page_title="Chess", page_icon="♟️", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;500;600&display=swap');
html, body, [data-testid="stAppViewContainer"] {
    background: #1a1a2e !important; color: #e8e0d0;
    font-family: 'Inter', sans-serif;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none; }
.block-container { padding-top: 1.2rem !important; max-width: 780px !important; }
h1 { font-family:'Playfair Display',serif; font-size:2rem; color:#f0c040; margin:0 0 0.1rem; }
.subtitle { font-size:0.8rem; color:#a09880; letter-spacing:.08em; text-transform:uppercase; }
.status-bar {
    display:flex; align-items:center; gap:.7rem;
    background:#16213e; border:1px solid #2a2a4a;
    border-radius:8px; padding:.5rem .9rem; margin:.3rem 0; font-size:.88rem;
}
.dot { width:10px; height:10px; border-radius:50%; flex-shrink:0; }
.dot-white { background:#f0f0f0; border:1px solid #888; }
.dot-black { background:#222; border:1px solid #888; }
.dot-check { background:#e04040; }
.move-table { width:100%; border-collapse:collapse; font-size:.8rem; }
.move-table th { color:#a09880; font-weight:600; padding:3px 6px; border-bottom:1px solid #2a2a4a; text-align:left; }
.move-table td { padding:2px 6px; color:#c8c0b0; }
.move-table tr:last-child td { color:#f0c040; }

/* Square buttons – override Streamlit defaults */
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button {
    width:64px !important; height:64px !important;
    min-width:0 !important; padding:0 !important;
    font-size:2rem !important; line-height:1 !important;
    border-radius:0 !important; border:none !important;
    cursor:pointer !important;
}
/* Coord labels */
.coord-file { display:flex; justify-content:space-around; width:512px; font-size:.72rem; color:#a09880; padding:2px 0; }
.coord-rank-col { display:flex; flex-direction:column; justify-content:space-around; height:512px; font-size:.72rem; color:#a09880; text-align:center; width:18px; padding:0; }
</style>
""", unsafe_allow_html=True)

# ── Pieces ────────────────────────────────────────────────────────────────────
PIECES = {
    "wK":"♔","wQ":"♕","wR":"♖","wB":"♗","wN":"♘","wP":"♙",
    "bK":"♚","bQ":"♛","bR":"♜","bB":"♝","bN":"♞","bP":"♟",
}
INIT_BOARD = [
    ["bR","bN","bB","bQ","bK","bB","bN","bR"],
    ["bP","bP","bP","bP","bP","bP","bP","bP"],
    [None]*8,[None]*8,[None]*8,[None]*8,
    ["wP","wP","wP","wP","wP","wP","wP","wP"],
    ["wR","wN","wB","wQ","wK","wB","wN","wR"],
]

# ── Chess logic ───────────────────────────────────────────────────────────────
def copy_board(b): return [row[:] for row in b]
def color(p): return p[0] if p else None
def kind(p):  return p[1] if p else None
def in_bounds(r,c): return 0<=r<8 and 0<=c<8

def raw_moves(board, r, c, ep, cr):
    piece = board[r][c]
    if not piece: return []
    col,typ = piece[0],piece[1]
    opp = "b" if col=="w" else "w"
    moves=[]
    def slide(dr,dc):
        nr,nc=r+dr,c+dc
        while in_bounds(nr,nc):
            if board[nr][nc]:
                if color(board[nr][nc])==opp: moves.append((nr,nc))
                break
            moves.append((nr,nc)); nr+=dr; nc+=dc
    if typ=="R":
        for d in [(1,0),(-1,0),(0,1),(0,-1)]: slide(*d)
    elif typ=="B":
        for d in [(1,1),(1,-1),(-1,1),(-1,-1)]: slide(*d)
    elif typ=="Q":
        for d in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]: slide(*d)
    elif typ=="N":
        for dr,dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            nr,nc=r+dr,c+dc
            if in_bounds(nr,nc) and color(board[nr][nc])!=col: moves.append((nr,nc))
    elif typ=="K":
        for dr in [-1,0,1]:
            for dc in [-1,0,1]:
                if dr==dc==0: continue
                nr,nc=r+dr,c+dc
                if in_bounds(nr,nc) and color(board[nr][nc])!=col: moves.append((nr,nc))
        row=7 if col=="w" else 0
        if r==row and c==4:
            if cr.get(col+"K") and not board[row][5] and not board[row][6]: moves.append((row,6))
            if cr.get(col+"Q") and not board[row][3] and not board[row][2] and not board[row][1]: moves.append((row,2))
    elif typ=="P":
        fwd=-1 if col=="w" else 1
        start=6 if col=="w" else 1
        nr=r+fwd
        if in_bounds(nr,c) and not board[nr][c]:
            moves.append((nr,c))
            if r==start and not board[r+2*fwd][c]: moves.append((r+2*fwd,c))
        for dc in [-1,1]:
            nc=c+dc
            if in_bounds(nr,nc):
                if color(board[nr][nc])==opp or ep==(nr,nc): moves.append((nr,nc))
    return moves

def find_king(board,col):
    for r in range(8):
        for c in range(8):
            if board[r][c]==col+"K": return r,c

def is_attacked(board,r,c,by,ep,cr):
    for rr in range(8):
        for cc in range(8):
            if color(board[rr][cc])==by:
                if (r,c) in raw_moves(board,rr,cc,ep,cr): return True
    return False

def apply_move(board,r,c,nr,nc,cr,ep):
    b=copy_board(board); piece=b[r][c]
    col,typ=piece[0],piece[1]; opp="b" if col=="w" else "w"
    captured=b[nr][nc]; new_ep=None
    if typ=="P" and (nr,nc)==ep:
        b[r][nc]=None; captured=opp+"P"
    if typ=="K" and abs(nc-c)==2:
        row=r
        if nc==6: b[row][5]=b[row][7]; b[row][7]=None
        else:     b[row][3]=b[row][0]; b[row][0]=None
    b[nr][nc]=piece; b[r][c]=None
    if typ=="P" and abs(nr-r)==2: new_ep=((r+nr)//2,c)
    new_cr=dict(cr)
    if piece=="wK": new_cr["wK"]=False; new_cr["wQ"]=False
    if piece=="bK": new_cr["bK"]=False; new_cr["bQ"]=False
    if (r,c)==(7,0) or (nr,nc)==(7,0): new_cr["wQ"]=False
    if (r,c)==(7,7) or (nr,nc)==(7,7): new_cr["wK"]=False
    if (r,c)==(0,0) or (nr,nc)==(0,0): new_cr["bQ"]=False
    if (r,c)==(0,7) or (nr,nc)==(0,7): new_cr["bK"]=False
    return b,new_cr,new_ep,captured

def legal_moves(board,r,c,ep,cr):
    piece=board[r][c]
    if not piece: return []
    col=piece[0]; opp="b" if col=="w" else "w"; result=[]
    for (nr,nc) in raw_moves(board,r,c,ep,cr):
        b2,cr2,ep2,_=apply_move(board,r,c,nr,nc,cr,ep)
        kr,kc=find_king(b2,col)
        if not is_attacked(b2,kr,kc,opp,ep2,cr2):
            if piece[1]=="K" and abs(nc-c)==2:
                mid=(c+nc)//2
                bm,_,_,_=apply_move(board,r,c,r,mid,cr,ep)
                if is_attacked(board,r,c,opp,ep,cr): continue
                if is_attacked(bm,r,mid,opp,ep,cr): continue
            result.append((nr,nc))
    return result

def all_legal_moves(board,col,ep,cr):
    moves=[]
    for r in range(8):
        for c in range(8):
            if color(board[r][c])==col:
                for m in legal_moves(board,r,c,ep,cr): moves.append((r,c,m[0],m[1]))
    return moves

def is_in_check(board,col,ep,cr):
    opp="b" if col=="w" else "w"
    kr,kc=find_king(board,col)
    return is_attacked(board,kr,kc,opp,ep,cr)

def move_san(board,r,c,nr,nc,ep,promo=None):
    piece=board[r][c]
    if not piece: return "?"
    typ=piece[1]; files="abcdefgh"
    if typ=="K" and abs(nc-c)==2: return "O-O" if nc==6 else "O-O-O"
    cap="x" if board[nr][nc] or (typ=="P" and (nr,nc)==ep) else ""
    if typ=="P":
        s=(files[c]+cap if cap else "")+files[nc]+str(8-nr)
        if promo: s+="="+promo
        return s
    return typ+cap+files[nc]+str(8-nr)

# ── Session state ─────────────────────────────────────────────────────────────
def init_state():
    st.session_state.update(
        board=copy_board(INIT_BOARD), turn="w",
        selected=None, legal=[], last_move=None,
        castling={"wK":True,"wQ":True,"bK":True,"bQ":True},
        en_passant=None, history=[], status="white",
        promotion_pending=None, captured_w=[], captured_b=[],
    )

if "board" not in st.session_state:
    init_state()
S = st.session_state

# ── Move execution ────────────────────────────────────────────────────────────
def finish_move(r,c,nr,nc,promo=None):
    san=move_san(S.board,r,c,nr,nc,S.en_passant,promo)
    nb,ncr,nep,cap=apply_move(S.board,r,c,nr,nc,S.castling,S.en_passant)
    if promo: nb[nr][nc]=S.turn+promo
    if cap:
        (S.captured_b if color(cap)=="b" else S.captured_w).append(cap)
    S.board=nb; S.castling=ncr; S.en_passant=nep
    S.last_move=(r,c,nr,nc); S.history.append(san)
    S.selected=None; S.legal=[]; S.promotion_pending=None
    next_col="b" if S.turn=="w" else "w"; S.turn=next_col
    moves=all_legal_moves(nb,next_col,nep,ncr)
    chk=is_in_check(nb,next_col,nep,ncr)
    if not moves: S.status="checkmate" if chk else "stalemate"
    elif chk:     S.status="check"
    else:         S.status="white" if next_col=="w" else "black"

def on_click(r,c):
    if S.status in ("checkmate","stalemate") or S.promotion_pending: return
    piece=S.board[r][c]
    if S.selected is None:
        if piece and color(piece)==S.turn:
            S.selected=(r,c); S.legal=legal_moves(S.board,r,c,S.en_passant,S.castling)
    else:
        sr,sc=S.selected
        if (r,c) in S.legal:
            moving=S.board[sr][sc]
            if moving[1]=="P" and (r==0 or r==7):
                S.promotion_pending=(sr,sc,r,c)
            else:
                finish_move(sr,sc,r,c)
        elif piece and color(piece)==S.turn and (r,c)!=S.selected:
            S.selected=(r,c); S.legal=legal_moves(S.board,r,c,S.en_passant,S.castling)
        else:
            S.selected=None; S.legal=[]

# ── Square colours ────────────────────────────────────────────────────────────
# We inject per-button background via CSS nth-child trick – but since Streamlit
# wraps each button separately we use a custom HTML overlay + st.button grid.

# We'll render the board as an 8x8 grid of st.button calls, and colour them
# by injecting a <style> block that targets each button by its unique key.

def sq_bg(r, c):
    lm = S.last_move
    last_set = {(lm[0],lm[1]),(lm[2],lm[3])} if lm else set()
    chk_sq = find_king(S.board, S.turn) if S.status in ("check","checkmate") else None

    if chk_sq==(r,c):       return "#e04040"
    if S.selected==(r,c):   return "#f6f669" if (r+c)%2==0 else "#baca2b"
    if (r,c) in S.legal:    return "#cdd26a" if (r+c)%2==0 else "#aaa23a"
    if (r,c) in last_set:   return "#cdd26a" if (r+c)%2==0 else "#aaa23a"
    return "#f0d9b5" if (r+c)%2==0 else "#b58863"

# ── Render ────────────────────────────────────────────────────────────────────
st.markdown('<h1>♟ Chess</h1><div class="subtitle">Two-player · Classic rules</div>', unsafe_allow_html=True)
st.write("")

# Build CSS for all 64 square buttons dynamically
css_parts = ["<style>"]
for r in range(8):
    for c in range(8):
        bg = sq_bg(r,c)
        key = f"sq_{r}_{c}"
        css_parts.append(
            f'button[kind="secondary"][data-testid="baseButton-secondary"]'
            f'[aria-label="{key}"] {{ background:{bg} !important; color: {"#000" if bg in ("#f0d9b5","#cdd26a") else "#000"} !important; }}'
        )
css_parts.append("</style>")
st.markdown("\n".join(css_parts), unsafe_allow_html=True)

left, mid, right = st.columns([0.18, 3.3, 1.5], gap="small")

with mid:
    files = list("abcdefgh")
    ranks = list("87654321")

    for r in range(8):
        cols = st.columns(8, gap="small")
        for c in range(8):
            piece = S.board[r][c]
            label = PIECES.get(piece,"·") if piece else "·"
            bg = sq_bg(r,c)
            key = f"sq_{r}_{c}"
            # Inject inline style via markdown trick before each button
            with cols[c]:
                st.markdown(
                    f'<style>div[data-testid="stButton"]:has(button[aria-label="{key}"])>button'
                    f'{{background:{bg}!important;border:none!important;'
                    f'width:60px!important;height:60px!important;'
                    f'font-size:2rem!important;padding:0!important;'
                    f'border-radius:0!important;color:#111!important;'
                    f'box-shadow:{"inset 0 0 0 3px #20c020" if (r,c) in S.legal else "none"}!important;}}</style>',
                    unsafe_allow_html=True,
                )
                st.button(label, key=key, on_click=on_click, args=(r,c),
                          help=f"{files[c]}{ranks[r]}")

    # File labels
    fcols = st.columns(8, gap="small")
    for c,f in enumerate(files):
        with fcols[c]:
            st.markdown(f'<div style="text-align:center;font-size:.7rem;color:#a09880;width:60px;">{f}</div>', unsafe_allow_html=True)

with right:
    # Status
    dot_map = {
        "white":("dot-white","White to move"),
        "black":("dot-black","Black to move"),
        "check":("dot-check",f"{'White' if S.turn=='w' else 'Black'} in check!"),
        "checkmate":("dot-check",f"Checkmate! {'Black' if S.turn=='w' else 'White'} wins 🎉"),
        "stalemate":("dot-white","Stalemate — Draw"),
    }
    dc,msg = dot_map.get(S.status,("dot-white",""))
    st.markdown(f'<div class="status-bar"><div class="dot {dc}"></div><span>{msg}</span></div>', unsafe_allow_html=True)

    # Captured
    cb = " ".join(PIECES.get(p,"") for p in S.captured_b) or "—"
    cw = " ".join(PIECES.get(p,"") for p in S.captured_w) or "—"
    st.markdown(f'<div class="status-bar" style="flex-wrap:wrap;font-size:.8rem;"><span style="color:#a09880">♙ took:</span> {cb}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="status-bar" style="flex-wrap:wrap;font-size:.8rem;"><span style="color:#a09880">♟ took:</span> {cw}</div>', unsafe_allow_html=True)

    # History
    st.write("")
    if S.history:
        rows=""
        for i in range(0,len(S.history),2):
            w=S.history[i]; b=S.history[i+1] if i+1<len(S.history) else ""
            rows+=f"<tr><td>{i//2+1}.</td><td>{w}</td><td>{b}</td></tr>"
        st.markdown(f'<table class="move-table"><tr><th>#</th><th>W</th><th>B</th></tr>{rows}</table>', unsafe_allow_html=True)
    else:
        st.markdown('<span style="color:#6a6a8a;font-size:.8rem;">No moves yet</span>', unsafe_allow_html=True)

    st.write("")
    if st.button("↺ New game", use_container_width=True):
        init_state(); st.rerun()

# Promotion modal
if S.promotion_pending:
    sr,sc,nr,nc=S.promotion_pending
    st.markdown("---")
    st.markdown("**Promote pawn to:**")
    pcols=st.columns(4)
    for i,p in enumerate(["Q","R","B","N"]):
        with pcols[i]:
            sym=PIECES[S.turn+p]
            if st.button(sym,key=f"promo_{p}",use_container_width=True):
                finish_move(sr,sc,nr,nc,promo=p); st.rerun()
