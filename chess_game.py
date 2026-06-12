<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Chess</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: #1a1a2e;
  color: #e8e0d0;
  font-family: 'Inter', sans-serif;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 16px 40px;
}

h1 {
  font-family: 'Playfair Display', serif;
  font-size: 2.2rem;
  color: #f0c040;
  letter-spacing: .01em;
  margin-bottom: 2px;
}
.subtitle {
  font-size: .75rem;
  color: #a09880;
  letter-spacing: .1em;
  text-transform: uppercase;
  margin-bottom: 20px;
}

/* ── Layout ── */
.game-wrap {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

/* ── Board ── */
.board-area { display: flex; flex-direction: column; align-items: center; gap: 0; }
.board-row  { display: flex; align-items: center; }
.rank-label, .file-label {
  font-size: .7rem;
  color: #a09880;
  width: 20px;
  text-align: center;
  user-select: none;
  flex-shrink: 0;
}
.file-row { display: flex; margin-left: 20px; }
.file-label { width: 68px; }

.sq {
  width: 68px; height: 68px;
  display: flex; align-items: center; justify-content: center;
  font-size: 2.6rem;
  cursor: pointer;
  position: relative;
  transition: filter .1s;
  user-select: none;
}
.sq:hover { filter: brightness(1.14); }
.sq.light { background: #f0d9b5; }
.sq.dark  { background: #b58863; }

.sq.selected  { background: #f6f669 !important; }
.sq.selected.dark { background: #d4d42a !important; }

.sq.last-move.light { background: #cdd26a; }
.sq.last-move.dark  { background: #aaa23a; }

.sq.in-check { background: #c62a2a !important; }

/* legal move hints */
.sq.legal-empty::after {
  content: '';
  position: absolute;
  width: 26px; height: 26px;
  border-radius: 50%;
  background: rgba(0,0,0,.22);
  pointer-events: none;
}
.sq.legal-capture::after {
  content: '';
  position: absolute;
  inset: 4px;
  border-radius: 50%;
  box-shadow: inset 0 0 0 6px rgba(0,0,0,.25);
  pointer-events: none;
}

.piece { pointer-events: none; line-height: 1; text-shadow: 0 1px 4px rgba(0,0,0,.35); }

/* ── Side panel ── */
.panel {
  width: 200px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-top: 4px;
}

.status-bar {
  display: flex; align-items: center; gap: 10px;
  background: #16213e;
  border: 1px solid #2a2a4a;
  border-radius: 8px;
  padding: 9px 13px;
  font-size: .88rem;
}
.dot {
  width: 11px; height: 11px;
  border-radius: 50%; flex-shrink: 0;
}
.dot.white { background: #f0f0f0; border: 1px solid #999; }
.dot.black { background: #222; border: 1px solid #888; }
.dot.red   { background: #e04040; }

.cap-row {
  background: #16213e;
  border: 1px solid #2a2a4a;
  border-radius: 8px;
  padding: 7px 13px;
  font-size: .82rem;
  min-height: 38px;
}
.cap-label { font-size: .7rem; color: #a09880; margin-bottom: 2px; }
.cap-pieces { font-size: 1.1rem; letter-spacing: 1px; min-height: 18px; }

.history-box {
  background: #16213e;
  border: 1px solid #2a2a4a;
  border-radius: 8px;
  padding: 8px 4px 8px 10px;
  flex: 1;
  overflow-y: auto;
  max-height: 340px;
}
.history-box table { width: 100%; border-collapse: collapse; font-size: .8rem; }
.history-box th { color: #a09880; font-weight: 600; padding: 2px 6px; border-bottom: 1px solid #2a2a4a; text-align: left; }
.history-box td { padding: 2px 6px; color: #c8c0b0; }
.history-box tr:last-child td { color: #f0c040; }
.no-moves { color: #5a5a7a; font-size: .8rem; padding: 4px 0; }

.btn-new {
  background: #16213e;
  border: 1px solid #3a3a6a;
  color: #e8e0d0;
  border-radius: 7px;
  font-family: 'Inter', sans-serif;
  font-size: .88rem;
  padding: 9px;
  cursor: pointer;
  width: 100%;
  transition: border-color .18s, color .18s;
}
.btn-new:hover { border-color: #f0c040; color: #f0c040; }

/* ── Promotion modal ── */
.modal-overlay {
  display: none;
  position: fixed; inset: 0;
  background: rgba(0,0,0,.65);
  z-index: 100;
  align-items: center; justify-content: center;
}
.modal-overlay.open { display: flex; }
.modal {
  background: #16213e;
  border: 1px solid #3a3a6a;
  border-radius: 12px;
  padding: 24px 28px;
  text-align: center;
}
.modal h3 { font-family: 'Playfair Display', serif; color: #f0c040; margin-bottom: 16px; font-size: 1.2rem; }
.promo-btns { display: flex; gap: 12px; }
.promo-btn {
  width: 64px; height: 64px;
  font-size: 2.4rem;
  background: #1a1a2e;
  border: 1px solid #3a3a6a;
  border-radius: 8px;
  cursor: pointer;
  transition: border-color .15s, background .15s;
  display: flex; align-items: center; justify-content: center;
}
.promo-btn:hover { border-color: #f0c040; background: #222244; }
</style>
</head>
<body>

<h1>♟ Chess</h1>
<div class="subtitle">Two-player · Classic rules</div>

<div class="game-wrap">
  <div class="board-area">
    <div id="board-rows"></div>
    <div class="file-row" id="file-labels"></div>
  </div>

  <div class="panel">
    <div class="status-bar" id="status-bar">
      <div class="dot white" id="status-dot"></div>
      <span id="status-text">White to move</span>
    </div>

    <div class="cap-row">
      <div class="cap-label">♙ captured</div>
      <div class="cap-pieces" id="cap-by-white">—</div>
    </div>
    <div class="cap-row">
      <div class="cap-label">♟ captured</div>
      <div class="cap-pieces" id="cap-by-black">—</div>
    </div>

    <div class="history-box">
      <table>
        <thead><tr><th>#</th><th>White</th><th>Black</th></tr></thead>
        <tbody id="history-body"><tr><td colspan="3" class="no-moves">No moves yet</td></tr></tbody>
      </table>
    </div>

    <button class="btn-new" onclick="newGame()">↺ New game</button>
  </div>
</div>

<!-- Promotion modal -->
<div class="modal-overlay" id="promo-modal">
  <div class="modal">
    <h3>Promote pawn</h3>
    <div class="promo-btns" id="promo-btns"></div>
  </div>
</div>

<script>
// ── Pieces ────────────────────────────────────────────────────────────────────
const GLYPHS = {wK:'♔',wQ:'♕',wR:'♖',wB:'♗',wN:'♘',wP:'♙',
                bK:'♚',bQ:'♛',bR:'♜',bB:'♝',bN:'♞',bP:'♟'};

const INIT = [
  ['bR','bN','bB','bQ','bK','bB','bN','bR'],
  ['bP','bP','bP','bP','bP','bP','bP','bP'],
  Array(8).fill(null),Array(8).fill(null),Array(8).fill(null),Array(8).fill(null),
  ['wP','wP','wP','wP','wP','wP','wP','wP'],
  ['wR','wN','wB','wQ','wK','wB','wN','wR'],
];

// ── State ─────────────────────────────────────────────────────────────────────
let board, turn, selected, legalSq, lastMove, castling, ep, history,
    status, promoPending, capW, capB;

function newGame() {
  board = INIT.map(r => [...r]);
  turn = 'w'; selected = null; legalSq = []; lastMove = null;
  castling = {wK:true,wQ:true,bK:true,bQ:true};
  ep = null; history = []; status = 'white';
  promoPending = null; capW = []; capB = [];
  document.getElementById('promo-modal').classList.remove('open');
  render();
}

// ── Helpers ───────────────────────────────────────────────────────────────────
const col  = p => p ? p[0] : null;
const kind = p => p ? p[1] : null;
const inB  = (r,c) => r>=0&&r<8&&c>=0&&c<8;
const copyB= b => b.map(r=>[...r]);
const key  = (r,c) => r*8+c;

function findKing(b, cl) {
  for(let r=0;r<8;r++) for(let c=0;c<8;c++) if(b[r][c]===cl+'K') return [r,c];
}

function rawMoves(b, r, c, epT, cr) {
  const p=b[r][c]; if(!p) return [];
  const cl=p[0], ty=p[1], opp=cl==='w'?'b':'w', moves=[];
  const slide=(dr,dc)=>{
    let nr=r+dr,nc=c+dc;
    while(inB(nr,nc)){
      if(b[nr][nc]){if(col(b[nr][nc])===opp)moves.push([nr,nc]);break;}
      moves.push([nr,nc]);nr+=dr;nc+=dc;
    }
  };
  if(ty==='R'){[[1,0],[-1,0],[0,1],[0,-1]].forEach(d=>slide(...d));}
  else if(ty==='B'){[[1,1],[1,-1],[-1,1],[-1,-1]].forEach(d=>slide(...d));}
  else if(ty==='Q'){[[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]].forEach(d=>slide(...d));}
  else if(ty==='N'){
    [[-2,-1],[-2,1],[-1,-2],[-1,2],[1,-2],[1,2],[2,-1],[2,1]].forEach(([dr,dc])=>{
      const nr=r+dr,nc=c+dc;
      if(inB(nr,nc)&&col(b[nr][nc])!==cl)moves.push([nr,nc]);
    });
  }
  else if(ty==='K'){
    for(let dr=-1;dr<=1;dr++) for(let dc=-1;dc<=1;dc++){
      if(!dr&&!dc)continue;
      const nr=r+dr,nc=c+dc;
      if(inB(nr,nc)&&col(b[nr][nc])!==cl)moves.push([nr,nc]);
    }
    const row=cl==='w'?7:0;
    if(r===row&&c===4){
      if(cr[cl+'K']&&!b[row][5]&&!b[row][6])moves.push([row,6]);
      if(cr[cl+'Q']&&!b[row][3]&&!b[row][2]&&!b[row][1])moves.push([row,2]);
    }
  }
  else if(ty==='P'){
    const fwd=cl==='w'?-1:1, start=cl==='w'?6:1, nr=r+fwd;
    if(inB(nr,c)&&!b[nr][c]){
      moves.push([nr,c]);
      if(r===start&&!b[r+2*fwd][c])moves.push([r+2*fwd,c]);
    }
    for(const dc of[-1,1]){
      const nc=c+dc;
      if(inB(nr,nc)&&(col(b[nr][nc])===opp||(epT&&epT[0]===nr&&epT[1]===nc)))
        moves.push([nr,nc]);
    }
  }
  return moves;
}

function isAttacked(b, r, c, by, epT, cr) {
  for(let rr=0;rr<8;rr++) for(let cc=0;cc<8;cc++)
    if(col(b[rr][cc])===by && rawMoves(b,rr,cc,epT,cr).some(([nr,nc])=>nr===r&&nc===c))
      return true;
  return false;
}

function applyMove(b, r, c, nr, nc, cr, epT) {
  const nb=copyB(b), p=nb[r][c], cl=p[0], ty=p[1], opp=cl==='w'?'b':'w';
  let captured=nb[nr][nc], newEp=null;
  if(ty==='P'&&epT&&nr===epT[0]&&nc===epT[1]){nb[r][nc]=null;captured=opp+'P';}
  if(ty==='K'&&Math.abs(nc-c)===2){
    if(nc===6){nb[r][5]=nb[r][7];nb[r][7]=null;}
    else{nb[r][3]=nb[r][0];nb[r][0]=null;}
  }
  nb[nr][nc]=p; nb[r][c]=null;
  if(ty==='P'&&Math.abs(nr-r)===2)newEp=[Math.floor((r+nr)/2),c];
  const newCr={...cr};
  if(p==='wK'){newCr.wK=false;newCr.wQ=false;}
  if(p==='bK'){newCr.bK=false;newCr.bQ=false;}
  if((r===7&&c===0)||(nr===7&&nc===0))newCr.wQ=false;
  if((r===7&&c===7)||(nr===7&&nc===7))newCr.wK=false;
  if((r===0&&c===0)||(nr===0&&nc===0))newCr.bQ=false;
  if((r===0&&c===7)||(nr===0&&nc===7))newCr.bK=false;
  return{nb,newCr,newEp,captured};
}

function legalMoves(b, r, c, epT, cr) {
  const p=b[r][c]; if(!p)return[];
  const cl=p[0], opp=cl==='w'?'b':'w', result=[];
  for(const[nr,nc] of rawMoves(b,r,c,epT,cr)){
    const{nb,newCr,newEp}=applyMove(b,r,c,nr,nc,cr,epT);
    const[kr,kc]=findKing(nb,cl);
    if(isAttacked(nb,kr,kc,opp,newEp,newCr))continue;
    if(p[1]==='K'&&Math.abs(nc-c)===2){
      const mid=(c+nc)/2;
      const{nb:bm}=applyMove(b,r,c,r,mid,cr,epT);
      if(isAttacked(b,r,c,opp,epT,cr))continue;
      if(isAttacked(bm,r,mid,opp,epT,cr))continue;
    }
    result.push([nr,nc]);
  }
  return result;
}

function allLegalMoves(b, cl, epT, cr) {
  const moves=[];
  for(let r=0;r<8;r++) for(let c=0;c<8;c++)
    if(col(b[r][c])===cl) for(const[nr,nc] of legalMoves(b,r,c,epT,cr))
      moves.push([r,c,nr,nc]);
  return moves;
}

function toSAN(b, r, c, nr, nc, epT, promo) {
  const p=b[r][c]; if(!p)return'?';
  const ty=p[1], files='abcdefgh';
  if(ty==='K'&&Math.abs(nc-c)===2)return nc===6?'O-O':'O-O-O';
  const cap=(b[nr][nc]||(ty==='P'&&epT&&nr===epT[0]&&nc===epT[1]))?'x':'';
  if(ty==='P'){
    const s=(cap?files[c]+cap:'')+files[nc]+(8-nr);
    return s+(promo?'='+promo:'');
  }
  return ty+cap+files[nc]+(8-nr);
}

// ── Move execution ─────────────────────────────────────────────────────────────
function finishMove(r, c, nr, nc, promo) {
  const san=toSAN(board,r,c,nr,nc,ep,promo);
  const{nb,newCr,newEp,captured}=applyMove(board,r,c,nr,nc,castling,ep);
  if(promo) nb[nr][nc]=turn+promo;
  if(captured)(col(captured)==='b'?capB:capW).push(captured);
  board=nb; castling=newCr; ep=newEp;
  lastMove=[r,c,nr,nc]; history.push(san);
  selected=null; legalSq=[]; promoPending=null;
  const next=turn==='w'?'b':'w'; turn=next;
  const moves=allLegalMoves(nb,next,newEp,newCr);
  const chk=isAttacked(nb,...findKing(nb,next),(next==='w'?'b':'w'),newEp,newCr);
  if(!moves.length) status=chk?'checkmate':'stalemate';
  else if(chk)      status='check';
  else              status=next==='w'?'white':'black';
  document.getElementById('promo-modal').classList.remove('open');
  render();
}

// ── Click handler ─────────────────────────────────────────────────────────────
function onSquareClick(r, c) {
  if(status==='checkmate'||status==='stalemate'||promoPending)return;
  const p=board[r][c];
  if(selected===null){
    if(p&&col(p)===turn){selected=[r,c];legalSq=legalMoves(board,r,c,ep,castling);render();}
  } else {
    const[sr,sc]=selected;
    const isLegal=legalSq.some(([lr,lc])=>lr===r&&lc===c);
    if(isLegal){
      const moving=board[sr][sc];
      if(moving[1]==='P'&&(r===0||r===7)){
        promoPending=[sr,sc,r,c];
        showPromo();
      } else {
        finishMove(sr,sc,r,c,null);
      }
    } else if(p&&col(p)===turn&&!(r===sr&&c===sc)){
      selected=[r,c];legalSq=legalMoves(board,r,c,ep,castling);render();
    } else {
      selected=null;legalSq=[];render();
    }
  }
}

function showPromo() {
  const[,,,]= promoPending;
  const btns=document.getElementById('promo-btns');
  btns.innerHTML='';
  for(const p of['Q','R','B','N']){
    const btn=document.createElement('button');
    btn.className='promo-btn'; btn.textContent=GLYPHS[turn+p];
    btn.onclick=()=>{ finishMove(...promoPending, p); };
    btns.appendChild(btn);
  }
  document.getElementById('promo-modal').classList.add('open');
}

// ── Render ─────────────────────────────────────────────────────────────────────
function render() {
  renderBoard();
  renderStatus();
  renderCaptured();
  renderHistory();
}

function renderBoard() {
  const legalSet=new Set(legalSq.map(([r,c])=>key(r,c)));
  const lastSet=lastMove?new Set(lastMove.map((_,i)=>key(lastMove[i<2?0:2],lastMove[i<2?1:3]))):new Set();
  // fix lastSet properly
  const lmSet=lastMove?new Set([key(lastMove[0],lastMove[1]),key(lastMove[2],lastMove[3])]):new Set();
  const chkKing=( status==='check'||status==='checkmate') ? findKing(board,turn) : null;
  const ranks='87654321';
  const files='abcdefgh';
  const container=document.getElementById('board-rows');
  container.innerHTML='';
  for(let r=0;r<8;r++){
    const rowDiv=document.createElement('div');
    rowDiv.className='board-row';
    // rank label
    const rl=document.createElement('div');
    rl.className='rank-label'; rl.textContent=ranks[r];
    rowDiv.appendChild(rl);
    for(let c=0;c<8;c++){
      const sq=document.createElement('div');
      const isLight=(r+c)%2===0;
      sq.className='sq '+(isLight?'light':'dark');
      const k=key(r,c);
      if(chkKing&&chkKing[0]===r&&chkKing[1]===c) sq.classList.add('in-check');
      else if(selected&&selected[0]===r&&selected[1]===c) sq.classList.add('selected');
      else if(lmSet.has(k)) sq.classList.add('last-move');
      const p=board[r][c];
      if(legalSet.has(k)){
        sq.classList.add(p?'legal-capture':'legal-empty');
      }
      if(p){ const span=document.createElement('span'); span.className='piece'; span.textContent=GLYPHS[p]; sq.appendChild(span); }
      sq.addEventListener('click',()=>onSquareClick(r,c));
      rowDiv.appendChild(sq);
    }
    container.appendChild(rowDiv);
  }
  // file labels
  const fileRow=document.getElementById('file-labels');
  fileRow.innerHTML='<div style="width:20px;flex-shrink:0"></div>';
  for(const f of files){
    const fd=document.createElement('div'); fd.className='file-label'; fd.textContent=f;
    fd.style.cssText='text-align:center;font-size:.7rem;color:#a09880;height:18px;display:flex;align-items:center;justify-content:center;user-select:none;';
    fileRow.appendChild(fd);
  }
}

function renderStatus() {
  const dot=document.getElementById('status-dot');
  const txt=document.getElementById('status-text');
  dot.className='dot';
  const map={
    white:['white','White to move'],
    black:['black','Black to move'],
    check:['red',(turn==='w'?'White':'Black')+' in check!'],
    checkmate:['red','Checkmate! '+(turn==='w'?'Black':'White')+' wins 🎉'],
    stalemate:['white','Stalemate — Draw'],
  };
  const[dcls,msg]=map[status]||['white',''];
  dot.classList.add(dcls); txt.textContent=msg;
}

function renderCaptured() {
  const PIECES=GLYPHS;
  document.getElementById('cap-by-white').textContent=capB.map(p=>PIECES[p]).join('')||'—';
  document.getElementById('cap-by-black').textContent=capW.map(p=>PIECES[p]).join('')||'—';
}

function renderHistory() {
  const tbody=document.getElementById('history-body');
  if(!history.length){ tbody.innerHTML='<tr><td colspan="3" class="no-moves">No moves yet</td></tr>'; return; }
  let html='';
  for(let i=0;i<history.length;i+=2){
    const w=history[i], b=history[i+1]||'';
    html+=`<tr><td>${i/2+1}.</td><td>${w}</td><td>${b}</td></tr>`;
  }
  tbody.innerHTML=html;
  const box=tbody.closest('.history-box');
  box.scrollTop=box.scrollHeight;
}

// ── Start ─────────────────────────────────────────────────────────────────────
newGame();
</script>
</body>
</html>
