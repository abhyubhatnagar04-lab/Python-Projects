import streamlit as st
import time

# ==========================================
# 1. CORE ENGINE LOGIC (Your Exact Code)
# ==========================================
STARTING_BOARD = [
    [7, 8, 0, 4, 0, 0, 1, 2, 0],
    [6, 0, 0, 0, 7, 5, 0, 0, 9],
    [0, 0, 0, 6, 0, 1, 0, 7, 8],
    [0, 0, 7, 0, 4, 0, 2, 6, 0],
    [0, 0, 1, 0, 5, 0, 9, 3, 0],
    [9, 0, 4, 0, 6, 0, 0, 0, 5],
    [0, 7, 0, 3, 0, 0, 0, 1, 2],
    [1, 2, 0, 0, 0, 7, 4, 0, 0],
    [0, 4, 9, 2, 0, 6, 0, 0, 7]
]

def is_valid(b, num, pos):
    row, col = pos
    for j in range(9):
        if b[row][j] == num and col != j: return False
    for i in range(9):
        if b[i][col] == num and row != i: return False
    box_x, box_y = col // 3, row // 3
    for i in range(box_y * 3, box_y * 3 + 3):
        for j in range(box_x * 3, box_x * 3 + 3):
            if b[i][j] == num and (i, j) != pos: return False
    return True

def find_empty(b):
    for i in range(9):
        for j in range(9):
            if b[i][j] == 0: return (i, j)
    return None

def solve_backtrack(b):
    find = find_empty(b)
    if not find: return True
    row, col = find
    for i in range(1, 10):
        if is_valid(b, i, (row, col)):
            b[row][col] = i
            if solve_backtrack(b): return True
            b[row][col] = 0
    return False

# Pre-calculate the master key right on boot
if "solution_key" not in st.session_state:
    master_key = [row[:] for row in STARTING_BOARD]
    start_time = time.time()
    solve_backtrack(master_key)
    elapsed = time.time() - start_time
    st.session_state.solution_key = master_key
    st.session_state.bench_time = elapsed

# Initialize player canvas matrix
if "player_matrix" not in st.session_state:
    st.session_state.player_matrix = [row[:] for row in STARTING_BOARD]

# ==========================================
# 2. UI CONFIGURATION & SIDEBAR MODE
# ==========================================
st.set_page_config(page_title="Web Sudoku Engine", page_icon="🧩", layout="centered")
st.title("🧩 Autonomous Sudoku Dashboard")
st.caption("Clean browser view powered by your recursive backtracking logic")

with st.sidebar:
    st.header("⚙️ Board Controller")
    # Dropdown replacing the problematic button actions
    app_mode = st.selectbox(
        "Choose App Mode:",
        ["🎮 Play / Manual Entry", "🤖 View Solved Board"]
    )
    
    st.markdown("---")
    st.markdown(f"**Engine Benchmark:**")
    st.caption(f"Core backtrack solved initial state matrix in **{st.session_state.bench_time:.4f} seconds**.")

# Inject clean CSS styling for grid alignment
st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] {
        gap: 4px !important;
    }
    input {
        text-align: center !important;
        font-weight: bold !important;
        font-size: 20px !important;
        height: 42px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. INTERACTIVE 9x9 GRID RENDERING
# ==========================================
# Determine which dataset to project on screen based on sidebar toggle
active_render_source = (
    st.session_state.solution_key 
    if app_mode == "🤖 View Solved Board" 
    else st.session_state.player_matrix
)

for r in range(9):
    cols = st.columns(9)
    for c in range(9):
        original_val = STARTING_BOARD[r][c]
        display_val = active_render_source[r][c]
        
        if original_val != 0:
            # Render fixed start clues as grey badges
            cols[c].markdown(
                f"<div style='text-align:center; background-color:#E0E0E0; border-radius:4px; padding:8px; font-weight:bold; font-size:18px; color:#333;'>{original_val}</div>", 
                unsafe_allow_html=True
            )       
        else:
            if app_mode == "🤖 View Solved Board":
                # Render solved engine numbers as green badges
                cols[c].markdown(
                    f"<div style='text-align:center; background-color:#D4EDDA; border-radius:4px; padding:8px; font-weight:bold; font-size:18px; color:#155724;'>{display_val}</div>", 
                    unsafe_allow_html=True
                )
            else:
                # Active play inputs
                val_str = str(display_val) if display_val != 0 else ""
                user_entry = cols[c].text_input(
                    "", 
                    value=val_str, 
                    max_chars=1, 
                    key=f"cell_{r}_{c}", 
                    label_visibility="collapsed"
                )
                if user_entry.isdigit() and 1 <= int(user_entry) <= 9:
                    st.session_state.player_matrix[r][c] = int(user_entry)
                elif user_entry == "":
                    st.session_state.player_matrix[r][c] = 0

# Add a little state tracker text at the bottom for feedback
if app_mode == "🎮 Play / Manual Entry":
    st.info("💡 Tip: Toggle 'View Solved Board' in the sidebar to see the engine's answer key instantly!")
else:
    st.success("🤖 Displaying complete matrix solution calculated by the backtracking algorithm.")
