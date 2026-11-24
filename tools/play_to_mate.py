# Доигрывает линию из tools/lines.json до мата: Stockfish 2500 Эло, при оценке > 6 пешек — полная сила.
# python3 tools/play_to_mate.py <линия> <число партий>  (нужен pip install chess)
import chess, chess.engine, json, sys
lines=json.load(open('/home/user/Chess/tools/lines.json'))
name=sys.argv[1]; tries=int(sys.argv[2])
weak=chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish")
weak.configure({"UCI_LimitStrength":True,"UCI_Elo":2500,"Threads":1,"Hash":64})
full=chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish"); full.configure({"Threads":1,"Hash":64})
games=[]
for t in range(tries):
    b=chess.Board()
    for m in lines[name]: b.push_uci(m)
    while not b.is_game_over(claim_draw=True) and b.ply()<200:
        info=full.analyse(b,chess.engine.Limit(depth=12))
        sc=info["score"].white()
        decisive = sc.is_mate() or abs(sc.score())>600
        r=(full if decisive else weak).play(b,chess.engine.Limit(time=0.3))
        b.push(r.move)
    res=b.result(claim_draw=True); under=any(m.promotion and m.promotion!=chess.QUEEN for m in b.move_stack)
    print(name,t,res,b.is_checkmate(),b.ply(),"under" if under else "",flush=True)
    if b.is_checkmate() and res=="1-0" and not under: games.append([m.uci() for m in b.move_stack])
weak.quit(); full.quit()
json.dump(sorted(games,key=len),open(f'ext2_{name}.json','w'))
