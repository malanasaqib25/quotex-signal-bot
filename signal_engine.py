import pandas as pd
def ema(s,p): return s.ewm(span=p,adjust=False).mean()
def rsi(c,p=14):
 d=c.diff(); g=d.clip(lower=0).ewm(alpha=1/p,adjust=False).mean(); l=(-d.clip(upper=0)).ewm(alpha=1/p,adjust=False).mean()
 return 100-(100/(1+(g/l.replace(0,pd.NA))))
def macd(c):
 line=ema(c,12)-ema(c,26); sig=ema(line,9); return line,sig,line-sig
def atr(df,p=14):
 prev=df.close.shift(1); tr=pd.concat([df.high-df.low,(df.high-prev).abs(),(df.low-prev).abs()],axis=1).max(axis=1)
 return tr.ewm(alpha=1/p,adjust=False).mean()
def adx(df,p=14):
 up=df.high.diff(); down=-df.low.diff()
 plus=up.where((up>down)&(up>0),0.0); minus=down.where((down>up)&(down>0),0.0)
 a=atr(df,p).replace(0,pd.NA)
 pdi=100*plus.ewm(alpha=1/p,adjust=False).mean()/a; mdi=100*minus.ewm(alpha=1/p,adjust=False).mean()/a
 dx=100*(pdi-mdi).abs()/(pdi+mdi).replace(0,pd.NA)
 return dx.ewm(alpha=1/p,adjust=False).mean()
def bollinger(c,p=20,k=2):
 m=c.rolling(p).mean(); s=c.rolling(p).std(); return m,m+k*s,m-k*s
def one_tf(df):
 if len(df)<80:return {"signal":"NO TRADE","confidence":0,"trend":"UNKNOWN","score":0,"adx":None}
 c=df.close.astype(float); r=float(rsi(c).iloc[-1]); ml,ms,mh=macd(c); a=float(adx(df).iloc[-1])
 mid,upper,lower=bollinger(c); e20=ema(c,20).iloc[-1]; e50=ema(c,50).iloc[-1]; e200=ema(c,200).iloc[-1] if len(c)>=200 else e50
 x=df.iloc[-1]; rng=max(x.high-x.low,1e-12); body=abs(x.close-x.open)/rng
 score=0; reasons=[]
 if c.iloc[-1]>e20>e50 and e50>=e200: score+=2
 elif c.iloc[-1]<e20<e50 and e50<=e200: score-=2
 if mh.iloc[-1]>0 and ml.iloc[-1]>ms.iloc[-1]: score+=2
 elif mh.iloc[-1]<0 and ml.iloc[-1]<ms.iloc[-1]: score-=2
 if 52<=r<=68: score+=1
 elif 32<=r<=48: score-=1
 if pd.isna(a) or a<20: score=0
 if c.iloc[-1]>upper.iloc[-1] and score>0: score-=1
 if c.iloc[-1]<lower.iloc[-1] and score<0: score+=1
 if body<.20: score=0
 sig="UP" if score>=4 else "DOWN" if score<=-4 else "NO TRADE"
 conf=min(95,50+abs(score)*7) if sig!="NO TRADE" else 0
 return {"signal":sig,"confidence":conf,"trend":"BULLISH" if score>0 else "BEARISH" if score<0 else "MIXED","score":score,"adx":a}
def analyze(frames):
 weights={"1m":1,"5m":2,"15m":3,"1h":4,"4h":4}; res={tf:one_tf(df) for tf,df in frames.items()}
 ws=sum((1 if x["signal"]=="UP" else -1 if x["signal"]=="DOWN" else 0)*weights.get(tf,1) for tf,x in res.items())
 up=sum(res[x]["signal"]=="UP" for x in ("15m","1h","4h")); down=sum(res[x]["signal"]=="DOWN" for x in ("15m","1h","4h"))
 sig="UP" if up>=2 and ws>=8 else "DOWN" if down>=2 and ws<=-8 else "NO TRADE"
 conf=min(95,50+abs(ws)*4) if sig!="NO TRADE" else 0
 strength="A+" if conf>=85 else "A" if conf>=75 else "B" if conf else "NO SETUP"
 reasons=["Higher timeframes confirm bullish direction" if up>=2 else "Higher timeframes confirm bearish direction" if down>=2 else "Higher timeframes disagree: NO TRADE"]
 reasons += [f"{tf}: {x['signal']} | score {x['score']}" for tf,x in res.items()]
 return {"signal":sig,"confidence":conf,"strength":strength,"timeframes":res,"reasons":reasons}
