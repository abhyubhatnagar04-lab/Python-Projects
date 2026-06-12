import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Chess", page_icon="♟️", layout="centered")

st.markdown("""
<style>
html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:#1a1a2e!important;}
[data-testid="stHeader"]{background:transparent!important;}
[data-testid="stToolbar"]{display:none;}
.block-container{padding:1rem 1rem 0!important;max-width:900px!important;}
</style>
""", unsafe_allow_html=True)

CHESS_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;500;600&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
body{background:#1a1a2e;color:#e8e0d0;font-family:'Inter',sans-serif;
     display:flex;flex-direction:column;align-items:center;padding:20px 12px 32px;}
h1{font-family:'Playfair Display',serif;font-size:2rem;color:#f0c040;margin-bottom:2px;}
.subtitle{font-size:.72rem;color:#a09880;letter-spacing:.1em;text-transform:uppercase;margin-bottom:18px;}
.game-wrap{display:flex;gap:22px;align-items:flex-start;}
.board-area{display:flex;flex-direction:column;align-items:flex-start;}
.board-row{display:flex;align-items:center;}
.rank-label{width:18px;text-align:center;font-size:.68rem;color:#a09880;user-select:none;flex-shrink:0;}
.file-row{display:flex;margin-left:18px;}
.file-label{width:66px;text-align:center;font-size:.68rem;color:#a09880;user-select:none;height:16px;line-height:16px;}
.sq{width:66px;height:66px;display:flex;align-items:center;justify-content:center;
    cursor:pointer;position:relative;transition:filter .1s;user-select:none;}
.sq:hover{filter:brightness(1.13);}
.sq.light{background:#f0d9b5;}.sq.dark{background:#b58863;}
.sq.selected.light{background:#f6f669!important;}.sq.selected.dark{background:#d4d42a!important;}
.sq.last-light{background:#cdd26a!important;}.sq.last-dark{background:#aaa23a!important;}
.sq.in-check{background:#c62a2a!important;}
.sq.legal-empty::after{content:'';position:absolute;width:24px;height:24px;border-radius:50%;
  background:rgba(0,0,0,.22);pointer-events:none;}
.sq.legal-capture::after{content:'';position:absolute;inset:3px;border-radius:50%;
  box-shadow:inset 0 0 0 6px rgba(0,0,0,.25);pointer-events:none;}
.piece{pointer-events:none;font-size:2.5rem;line-height:1;text-shadow:0 1px 4px rgba(0,0,0,.35);}
.panel{width:190px;display:flex;flex-direction:column;gap:9px;padding-top:2px;}
.status-bar{display:flex;align-items:center;gap:9px;background:#16213e;border:1px solid #2a2a4a;
  border-radius:8px;padding:8px 12px;font-size:.86rem;}
.dot{width:11px;height:11px;border-radius:50%;flex-shrink:0;}
.dot.white{background:#f0f0f0;border:1px solid #999;}
.dot.black{background:#222;border:1px solid #888;}
.dot.red{background:#e04040;}
.cap-row{background:#16213e;border:1px solid #2a2a4a;border-radius:8px;padding:6px 12px;min-height:36px;}
.cap-label{font-size:.68rem;color:#a09880;margin-bottom:1px;}
.cap-pieces{font-size:1.05rem;letter-spacing:1px;min-height:16px;}
.history-box{background:#16213e;border:1px solid #2a2a4a;border-radius:8px;
  padding:7px 4px 7px 9px;overflow-y:auto;max-height:300px;flex:1;}
.history-box table{width:100%;border-collapse:collapse;font-size:.78rem;}
.history-box th{color:#a09880;font-weight:600;padding:2px 5px;border-bottom:1px solid #2a2a4a;text-align:left;}
.history-box td{padding:2px 5px;color:#c8c0b0;}
.history-box tr:last-child td{color:#f0c040;}
.no-moves{color:#5a5a7a;font-size:.78rem;padding:3px 0;}
.btn-new{background:#16213e;border:1px solid #3a3a6a;color:#e8e0d0;border-radius:7px;
  font-family:'Inter',sans-serif;font-size:.86rem;padding:9px;cursor:pointer;width:100%;
  transition:border-color .18s,color .18s;}
.btn-new:hover{border-color:#f0c040;color:#f0c040;}
.modal-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.65);
  z-index:100;align-items:center;justify-content:center;}
.modal-overlay.open{display:flex;}
.modal{background:#16213e;border:1px solid #3a3a6a;border-radius:12px;padding:22px 26px;text-align:center;}
.modal h3{font-family:'Playfair Display',serif;color:#f0c040;margin-bottom:14px;font-size:1.15rem;}
.promo-btns{display:flex;gap:10px;}
.promo-btn{width:62px;height:62px;font-size:2.3rem;background:#1a1a2e;border:1px solid #3a3a6a;
  border-radius:8px;cursor:pointer;display:flex;align-items:center;justify-content:center;
  transition:border-color .15s,background .15s;}
.promo-btn:hover{border-color:#f0c040;background:#222244;}
</style>
</head>
<body>
<h1>♟ Chess</h1>
<div class="subtitle">Two-player · Classic rules</div>
<div class="game-wrap">
  <div class="board-area">
    <div id="board-rows"></div>
    <div class="file-row" id="file-row"></div>
  </div>
  <div class="panel">
    <div class="status-bar"><div class="dot white" id="sdot"></div><span id="stxt">White to move</span></div>
    <div class="cap-row"><div class="cap-label">♙ captured</div><div class="cap-pieces" id="capW">—</div></div>
    <div class="cap-row"><div class="cap-label">♟ captured</div><div class="cap-pieces" id="capB">—</div></div>
    <div class="history-box">
      <table><thead><tr><th>#</th><th>White</th><th>Black</th></tr></thead>
      <tbody id="hist"></tbody></table>
    </div>
    <button class="btn-new" onclick="newGame()">↺ New game</button>
  </div>
</div>
<div class="modal-overlay" id="promo-modal">
  <div class="modal"><h3>Promote pawn</h3><div class="promo-btns" id="promo-btns"></div></div>
</div>
<script>
const G={wK:'♔',wQ:'♕',wR:'♖',wB:'♗',wN:'♘',wP:'♙',bK:'♚',bQ:'♛',bR:'♜',bB:'♝',bN:'♞',bP:'♟'};
const INIT=[['bR','bN','bB','bQ','bK','bB','bN','bR'],['bP','bP','bP','bP','bP','bP','bP','bP'],
  [,,,,,,,,].fill(null),[,,,,,,,,].fill(null),[,,,,,,,,].fill(null),[,,,,,,,,].fill(null),
  ['wP','wP','wP','wP','wP','wP','wP','wP'],['wR','wN','wB','wQ','wK','wB','wN','wR']];
let board,turn,sel,legals,lastMove,cr,ep,hist,status,promo,capW,capB;
const col=p=>p?p[0]:null, inB=(r,c)=>r>=0&&r<8&&c>=0&&c<8, cpB=b=>b.map(r=>[...r]);
function newGame(){
  board=INIT.map(r=>[...r]);turn='w';sel=null;legals=[];lastMove=null;
  cr={wK:1,wQ:1,bK:1,bQ:1};ep=null;hist=[];status='white';promo=null;capW=[];capB=[];
  document.getElementById('promo-modal').classList.remove('open');
  render();
}
function findKing(b,cl){for(let r=0;r<8;r++)for(let c=0;c<8;c++)if(b[r][c]===cl+'K')return[r,c];}
function rawMoves(b,r,c,epT,cr){
  const p=b[r][c];if(!p)return[];
  const cl=p[0],ty=p[1],opp=cl==='w'?'b':'w',mv=[];
  const sl=(dr,dc)=>{let nr=r+dr,nc=c+dc;while(inB(nr,nc)){if(b[nr][nc]){if(col(b[nr][nc])===opp)mv.push([nr,nc]);break;}mv.push([nr,nc]);nr+=dr;nc+=dc;}};
  if(ty==='R')[[1,0],[-1,0],[0,1],[0,-1]].forEach(d=>sl(...d));
  else if(ty==='B')[[1,1],[1,-1],[-1,1],[-1,-1]].forEach(d=>sl(...d));
  else if(ty==='Q')[[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]].forEach(d=>sl(...d));
  else if(ty==='N')[[-2,-1],[-2,1],[-1,-2],[-1,2],[1,-2],[1,2],[2,-1],[2,1]].forEach(([dr,dc])=>{const nr=r+dr,nc=c+dc;if(inB(nr,nc)&&col(b[nr][nc])!==cl)mv.push([nr,nc]);});
  else if(ty==='K'){
    for(let dr=-1;dr<=1;dr++)for(let dc=-1;dc<=1;dc++){if(!dr&&!dc)continue;const nr=r+dr,nc=c+dc;if(inB(nr,nc)&&col(b[nr][nc])!==cl)mv.push([nr,nc]);}
    const row=cl==='w'?7:0;
    if(r===row&&c===4){if(cr[cl+'K']&&!b[row][5]&&!b[row][6])mv.push([row,6]);if(cr[cl+'Q']&&!b[row][3]&&!b[row][2]&&!b[row][1])mv.push([row,2]);}
  } else if(ty==='P'){
    const fwd=cl==='w'?-1:1,st=cl==='w'?6:1,nr=r+fwd;
    if(inB(nr,c)&&!b[nr][c]){mv.push([nr,c]);if(r===st&&!b[r+2*fwd][c])mv.push([r+2*fwd,c]);}
    for(const dc of[-1,1]){const nc=c+dc;if(inB(nr,nc)&&(col(b[nr][nc])===opp||(epT&&nr===epT[0]&&nc===epT[1])))mv.push([nr,nc]);}
  }
  return mv;
}
function isAtk(b,r,c,by,epT,cr){
  for(let rr=0;rr<8;rr++)for(let cc=0;cc<8;cc++)
    if(col(b[rr][cc])===by&&rawMoves(b,rr,cc,epT,cr).some(([nr,nc])=>nr===r&&nc===c))return true;
  return false;
}
function applyMove(b,r,c,nr,nc,cr,epT){
  const nb=cpB(b),p=nb[r][c],cl=p[0],ty=p[1],opp=cl==='w'?'b':'w';
  let captured=nb[nr][nc],newEp=null;
  if(ty==='P'&&epT&&nr===epT[0]&&nc===epT[1]){nb[r][nc]=null;captured=opp+'P';}
  if(ty==='K'&&Math.abs(nc-c)===2){if(nc===6){nb[r][5]=nb[r][7];nb[r][7]=null;}else{nb[r][3]=nb[r][0];nb[r][0]=null;}}
  nb[nr][nc]=p;nb[r][c]=null;
  if(ty==='P'&&Math.abs(nr-r)===2)newEp=[Math.floor((r+nr)/2),c];
  const ncr={...cr};
  if(p==='wK'){ncr.wK=0;ncr.wQ=0;}if(p==='bK'){ncr.bK=0;ncr.bQ=0;}
  if((r===7&&c===0)||(nr===7&&nc===0))ncr.wQ=0;if((r===7&&c===7)||(nr===7&&nc===7))ncr.wK=0;
  if((r===0&&c===0)||(nr===0&&nc===0))ncr.bQ=0;if((r===0&&c===7)||(nr===0&&nc===7))ncr.bK=0;
  return{nb,ncr,newEp,captured};
}
function legalMoves(b,r,c,epT,cr){
  const p=b[r][c];if(!p)return[];
  const cl=p[0],opp=cl==='w'?'b':'w',res=[];
  for(const[nr,nc]of rawMoves(b,r,c,epT,cr)){
    const{nb,ncr,newEp}=applyMove(b,r,c,nr,nc,cr,epT);
    const[kr,kc]=findKing(nb,cl);
    if(isAtk(nb,kr,kc,opp,newEp,ncr))continue;
    if(p[1]==='K'&&Math.abs(nc-c)===2){
      const mid=(c+nc)/2,{nb:bm}=applyMove(b,r,c,r,mid,cr,epT);
      if(isAtk(b,r,c,opp,epT,cr))continue;if(isAtk(bm,r,mid,opp,epT,cr))continue;
    }
    res.push([nr,nc]);
  }
  return res;
}
function allLegal(b,cl,epT,cr){const mv=[];for(let r=0;r<8;r++)for(let c=0;c<8;c++)if(col(b[r][c])===cl)for(const[nr,nc]of legalMoves(b,r,c,epT,cr))mv.push([r,c,nr,nc]);return mv;}
function toSAN(b,r,c,nr,nc,epT,promo){
  const p=b[r][c];if(!p)return'?';const ty=p[1],f='abcdefgh';
  if(ty==='K'&&Math.abs(nc-c)===2)return nc===6?'O-O':'O-O-O';
  const cap=(b[nr][nc]||(ty==='P'&&epT&&nr===epT[0]&&nc===epT[1]))?'x':'';
  if(ty==='P')return(cap?f[c]+cap:'')+f[nc]+(8-nr)+(promo?'='+promo:'');
  return ty+cap+f[nc]+(8-nr);
}
function finishMove(r,c,nr,nc,prom){
  const san=toSAN(board,r,c,nr,nc,ep,prom);
  const{nb,ncr,newEp,captured}=applyMove(board,r,c,nr,nc,cr,ep);
  if(prom)nb[nr][nc]=turn+prom;
  if(captured)(col(captured)==='b'?capB:capW).push(captured);
  board=nb;cr=ncr;ep=newEp;lastMove=[r,c,nr,nc];hist.push(san);
  sel=null;legals=[];promo=null;
  const next=turn==='w'?'b':'w';turn=next;
  const moves=allLegal(nb,next,newEp,ncr);
  const chk=isAtk(nb,...findKing(nb,next),(next==='w'?'b':'w'),newEp,ncr);
  if(!moves.length)status=chk?'checkmate':'stalemate';
  else if(chk)status='check';
  else status=next==='w'?'white':'black';
  document.getElementById('promo-modal').classList.remove('open');
  render();
}
function onClick(r,c){
  if(status==='checkmate'||status==='stalemate'||promo)return;
  const p=board[r][c];
  if(!sel){
    if(p&&col(p)===turn){sel=[r,c];legals=legalMoves(board,r,c,ep,cr);render();}
  } else {
    const[sr,sc]=sel,isLeg=legals.some(([lr,lc])=>lr===r&&lc===c);
    if(isLeg){
      const mv=board[sr][sc];
      if(mv[1]==='P'&&(r===0||r===7)){promo=[sr,sc,r,c];showPromo();}
      else finishMove(sr,sc,r,c,null);
    } else if(p&&col(p)===turn&&!(r===sr&&c===sc)){
      sel=[r,c];legals=legalMoves(board,r,c,ep,cr);render();
    } else {sel=null;legals=[];render();}
  }
}
function showPromo(){
  const bb=document.getElementById('promo-btns');bb.innerHTML='';
  for(const p of['Q','R','B','N']){
    const btn=document.createElement('button');btn.className='promo-btn';btn.textContent=G[turn+p];
    btn.onclick=()=>finishMove(...promo,p);bb.appendChild(btn);
  }
  document.getElementById('promo-modal').classList.add('open');
}
function render(){
  const lset=new Set(legals.map(([r,c])=>r*8+c));
  const lmset=lastMove?new Set([lastMove[0]*8+lastMove[1],lastMove[2]*8+lastMove[3]]):new Set();
  const chkK=(status==='check'||status==='checkmate')?findKing(board,turn):null;
  const cont=document.getElementById('board-rows');cont.innerHTML='';
  for(let r=0;r<8;r++){
    const row=document.createElement('div');row.className='board-row';
    const rl=document.createElement('div');rl.className='rank-label';rl.textContent='87654321'[r];row.appendChild(rl);
    for(let c=0;c<8;c++){
      const sq=document.createElement('div'),light=(r+c)%2===0,k=r*8+c;
      sq.className='sq '+(light?'light':'dark');
      if(chkK&&chkK[0]===r&&chkK[1]===c)sq.classList.add('in-check');
      else if(sel&&sel[0]===r&&sel[1]===c)sq.classList.add('selected');
      else if(lmset.has(k))sq.classList.add(light?'last-light':'last-dark');
      const p=board[r][c];
      if(lset.has(k))sq.classList.add(p?'legal-capture':'legal-empty');
      if(p){const sp=document.createElement('span');sp.className='piece';sp.textContent=G[p];sq.appendChild(sp);}
      sq.addEventListener('click',()=>onClick(r,c));
      row.appendChild(sq);
    }
    cont.appendChild(row);
  }
  const fr=document.getElementById('file-row');fr.innerHTML='<div style="width:18px"></div>';
  for(const f of'abcdefgh'){const d=document.createElement('div');d.className='file-label';d.textContent=f;fr.appendChild(d);}
  // status
  const dot=document.getElementById('sdot'),txt=document.getElementById('stxt');
  dot.className='dot';
  const sm={white:['white','White to move'],black:['black','Black to move'],
    check:['red',(turn==='w'?'White':'Black')+' in check!'],
    checkmate:['red','Checkmate! '+(turn==='w'?'Black':'White')+' wins 🎉'],
    stalemate:['white','Stalemate — Draw']};
  const[dc,msg]=sm[status]||['white',''];dot.classList.add(dc);txt.textContent=msg;
  // captured
  document.getElementById('capW').textContent=capB.map(p=>G[p]).join('')||'—';
  document.getElementById('capB').textContent=capW.map(p=>G[p]).join('')||'—';
  // history
  const tbody=document.getElementById('hist');
  if(!hist.length){tbody.innerHTML='<tr><td colspan="3" class="no-moves">No moves yet</td></tr>';return;}
  let html='';for(let i=0;i<hist.length;i+=2)html+=`<tr><td>${i/2+1}.</td><td>${hist[i]}</td><td>${hist[i+1]||''}</td></tr>`;
  tbody.innerHTML=html;
  tbody.closest('.history-box').scrollTop=9999;
}
newGame();
</script>
</body></html>
"""

components.html(CHESS_HTML, height=640, scrolling=False)
