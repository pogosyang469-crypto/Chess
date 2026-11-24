# Оценка ходов Stockfish: python3 tools/analyze.py tools/lines.json -> evals.json (вставляется в index.html как EVALS)
import subprocess, sys, math, json
SF = subprocess.Popen(["/usr/games/stockfish"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
def send(c): SF.stdin.write(c+"\n")
def read_until(tok):
    out=[]
    while True:
        l=SF.stdout.readline().strip(); out.append(l)
        if l.startswith(tok): return out
send("uci"); read_until("uciok")
for o in ["Threads value 4","Hash value 256","MultiPV value 2"]: send("setoption name "+o)
send("isready"); read_until("readyok")
D=20
def sc_of(t):
    i=t.index("score"); n=int(t[i+2]); return n if t[i+1]=="cp" else ((10000-abs(n)) if n>0 else -(10000-abs(n)))
def search(moves, restrict=None):
    send("ucinewgame"); send("position startpos moves "+" ".join(moves))
    send(f"go depth {D}"+(f" searchmoves {restrict}" if restrict else ""))
    out=read_until("bestmove"); pv={}
    for l in out:
        t=l.split()
        if "multipv" in t and "pv" in t and f"depth" in t and int(t[t.index("depth")+1])==D:
            pv[int(t[t.index("multipv")+1])]=(sc_of(t), t[t.index("pv")+1])
    return pv
def wp(c): return 50+50*(2/(1+math.exp(-0.00368208*c))-1)
lines=json.load(open(sys.argv[1])); outall={}
for name,moves in lines.items():
    res=[]
    for i,m in enumerate(moves):
        stm=1 if i%2==0 else -1
        pv=search(moves[:i]); best=pv[1]; second=pv.get(2,(None,None))
        played=search(moves[:i],m)[1][0] if m!=best[1] else best[0]
        loss=max(0,wp(best[0])-wp(played))
        gap=wp(best[0])-wp(second[0]) if second[0] is not None else 0
        res.append(dict(uci=m,best=best[1],evalW=played*stm,loss=round(loss,2),gap=round(gap,1)))
        print(name,i,m,res[-1],flush=True)
    pv=search(moves)
    fin=pv[1][0]*(1 if len(moves)%2==0 else -1) if 1 in pv else None  # None — мат/пат на доске
    outall[name]=dict(moves=res,final=fin)
json.dump(outall,open("evals.json","w"),indent=1)
