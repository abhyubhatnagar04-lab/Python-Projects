import streamlit as st
import chess
import chess.svg
import base64

# ==========================================
# 1. UI CONFIGURATION & PREMIUM STYLING
# ==========================================
st.set_page_config(page_title="Premium Chess Arena", page_icon="♔", layout="centered")
st.title("♔ Autonomous Chess Arena")
st.caption("High-Definition SVG Graphics with Native Click-to-Move Mechanics")

# Injecting Custom CSS to turn standard Streamlit buttons completely transparent
# This allows the beautiful SVG chess pieces to show through from underneath!
st.markdown("""
    <style>
    div.stButton > button {
        background-color: transparent !important;
        color: transparent !important;
        border: 1px solid transparent !important;
        height: 52px !important;
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        border: 2px solid #829769 !important;
        background-color: rgba(130, 151, 105, 0.3) !important;
    }
    /* Highlight selected square */
    div.stButton > button:active, div.stButton > button:focus {
        border: 2px solid #FFCC00 !important;
        background-color: rgba(255, 204, 0, 0.2) !important;
    }
    /* Grid gap reset for perfect alignment */
    div[data-testid="stHorizontalBlock"] {
        gap: 0px !important;
        margin-bottom: -4px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Session state initialization
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "selected_square" not in st.session_state:
    st.session_state.selected_square = None
if "move_log" not in st.session_state:
    st.session_state.move_log = []

board = st.session_state.board

# ==========================================
# 2. GAME CONTROLS IN SIDEBAR
# ==========================================
with st.sidebar:
    st.header("⚙️ Match Analytics")
    st.markdown(f"**Active Turn:** {'⚪ White' if board.turn == chess.WHITE else '⚫ Black'}")
    st.markdown(f"**Moves Stack:** {len(board.move_stack)}")
    
    if st.session_state.selected_square is not None:
        sq_name = chess.square_name(st.session_state.selected_square)
        st.info(f"📍 Selected: **{sq_name.upper()}**")
        if st.button("❌ Clear Selection", use_container_width=True):
            st.session_state.selected_square = None
            st.rerun()
            
    st.markdown("---")
    if st.button("🔄 Reset Board Matrix", use_container_width=True, type="secondary"):
        st.session_state.board = chess.Board()
        st.session_state.selected_square = None
        st.session_state.move_log = []
        st.rerun()

# ==========================================
# 3. PREMIUM VISUAL RENDERING (THE FIX)
# ==========================================
# Generate official high-res chess pieces & board vectors
fill_dict = {}
if st.session_state.selected_square is not None:
    fill_dict = {st.session_state.selected_square: "rgba(255, 204, 0, 0.5)"}

board_svg = chess.svg.board(
    board=board,
    size=420,
    fill=fill_dict,
    coordinates=True
)
b64_svg = base64.b64encode(board_svg.encode('utf-8')).decode('utf-8')

# Render the HD Board directly as a background canvas layout
st.markdown(
    f'<div style="display: flex; justify-content: center; position: relative; width: 420px; margin: 0 auto;">'
    f'<img src="data:image/svg+xml;base64,{b64_svg}" width="420" style="position: absolute; z-index: 1;"/>'
    f'<div style="position: relative; z-index: 2; width: 368px; margin-top: 26px; margin-left: 26px;">', # Aligns transparent buttons over grid cells
    unsafe_allow_html=True
)

# Render the 8x8 transparent interactive button layer over the SVG image
for rank in range(7, -1, -1):
    grid_cols = st.columns(8)
    for file in range(8):
        square_idx = chess.square(file, rank)
        
        # Invisible button that captures user clicks perfectly
        if grid_cols[file].button("", key=f"cell_{rank}_{file}"):
            if st.session_state.selected_square is None:
                # First click: Select piece
                piece = board.piece_at(square_idx)
                if piece and piece.color == board.turn:
                    st.session_state.selected_square = square_idx
                    st.rerun()
            else:
                # Second click: Move piece
                source_sq = st.session_state.selected_square
                target_sq = square_idx
                proposed_move = chess.Move(source_sq, target_sq)
                
                # Auto-promotion handling
                moving_piece = board.piece_at(source_sq)
                if moving_piece and moving_piece.piece_type == chess.PAWN and rank in [0, 7]:
                    proposed_move.promotion = chess.QUEEN
                
                if proposed_move in board.legal_moves:
                    board.push(proposed_move)
                    st.session_state.move_log.append(proposed_move.uci())
                    st.toast(f"Moved: {proposed_move.uci()}", icon="⚔️")
                
                st.session_state.selected_square = None
                st.rerun()

st.markdown('</div></div><br><br>', unsafe_allow_html=True)

# ==========================================
# 4. GAME NOTATION LOG
# ==========================================
if st.session_state.move_log:
    st.markdown("### 📋 Match History")
    st.info(", ".join(st.session_state.move_log))
