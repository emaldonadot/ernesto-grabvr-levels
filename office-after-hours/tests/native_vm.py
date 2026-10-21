"""Deterministic test harness for the generated scalar GASM bytecode.
Not the GRAB engine: immediate connection writes and second-based DeltaTime are
explicit assumptions to verify in Quest. Executes the serialized instructions.
"""
import json, random, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class World:
 def __init__(self,players=2,seed=1):
  self.level=json.loads((ROOT/'dist/office-after-hours.json').read_text());self.nodes={};self.byname={};self.triggers={};self.progs=[];self.rng=random.Random(seed);self.time=0
  def flatten(nodes):
   for n in nodes:
    self.nodes[len(self.nodes)+1]=n
    if 'levelNodeGroup' in n:flatten(n['levelNodeGroup']['childNodes'])
  flatten(self.level['levelNodes'])
  ids=json.loads((ROOT/'docs/manifest.json').read_text())['ids'];self.byname={k:self.nodes[v] for k,v in ids.items()}
  self.players=[dict(id=i+10,pos=[0,1.6,0],vars=[0]*5) for i in range(players)]
  for n in self.nodes.values():
   if 'levelNodeGASM' in n:self.progs.append(VM(self,n['levelNodeGASM']))
 def pos(self,n):return self.byname[n]['levelNodeGroup']['position']
 def touch(self,name,player,active=1):self.triggers[id(self.byname[name])]=(active,self.players[player]['id'])
 def tick(self,dt=1/60):
  self.dt=dt;self.time+=dt
  for p in self.progs:p.run()
 def frames(self,n,dt=1/60):
  for _ in range(n):self.tick(dt)
 def pulse(self,name,player):
  self.touch(name,player);self.frames(3);self.touch(name,player,0);self.frames(3)
class VM:
 def __init__(self,w,data):
  self.w=w;self.p=data['program'];self.pc=0;self.sleep=0;self.r=[0]*8;self.io={};self.bind={};self.selected=None
  self.labels={i:next(j for j,x in enumerate(self.p['instructions']) if x['type']==13 and x['operands'][0]['index']==i) for i in range(len(self.p['labels']))}
  for c in data['connections']:
   for prop in c['properties']:
    kind=next(k for k in prop if k not in ['components','objectID'])
    expected={'player':28,'triggerActive':6}.get(kind)
    if expected is not None and len(prop['components'])!=expected:
     raise ValueError(f'{kind} requires {expected} native component slots; got {len(prop["components"])}')
    for i,component in enumerate(prop['components']):
     for key,t in [('inputRegisterIndex',0),('outputRegisterIndex',1),('inoutRegisterIndex',7)]:
      idx=component.get(key,-1)
      if idx>=0:self.bind[t,idx]=(c['objectID'],kind,i)
 def read(self,o):
  t=o['type'];i=o.get('index',0)
  if t==4:return o['value']
  if t==2:return self.r[i]
  if t==3:return self.w.dt if i==4 else 0
  if t==5:return i
  binding=self.bind.get((t,i))
  if not binding:return self.io.get((t,i),0)
  oid,k,j=binding
  if k=='player':
   a=self.selected;values={4:len(self.w.players),5:int(a is not None),6:a['id'] if a else 0,18:10}
   if j in values:return values[j]
   if j in [7,8,9]:return a['pos'][j-7] if a else 0
   return self.io.get((t,i),0)
  if k=='playerVariables':return self.selected['vars'][j] if self.selected else 0
  node=self.w.nodes[oid]
  if k=='position':return node[next(key for key in node if key.startswith('levelNode'))]['position']['xyz'[j]]
  if k=='triggerActive':return self.w.triggers.get(id(node),(0,0))[j] if j in [0,1] else self.io.get((t,i),0)
  return self.io.get((t,i),0)
 def write(self,o,v):
  t=o['type'];i=o.get('index',0)
  if t==2:self.r[i]=v;return
  if t==3:raise AssertionError('unexpected special write')
  assert t in [1,7],('write to read-only operand',o)
  self.io[t,i]=v;oid,k,j=self.bind[t,i]
  if k=='player':
   if j==0:self.selected=self.w.players[int(v)] if 0<=int(v)<len(self.w.players) else None
   if j==1:self.selected=next((p for p in self.w.players if p['id']==v),None)
   if j==24 and v and self.selected:
    vals={self.bind[key][2]:val for key,val in self.io.items() if self.bind.get(key,(0,'',0))[1]=='player'}
    self.selected['pos']=[vals.get(q,0) for q in [20,21,22]]
  elif k=='playerVariables':
   if self.selected:self.selected['vars'][j]=v
  elif k=='position':
   node=self.w.nodes[oid];node[next(key for key in node if key.startswith('levelNode'))]['position']['xyz'[j]]=v
 def run(self):
  if self.sleep>0:self.sleep-=self.w.dt;return
  code=self.p['instructions'];steps=0
  while self.pc<len(code) and steps<500:
   ins=code[self.pc];self.pc+=1;steps+=1;t=ins['type'];o=ins['operands'];get=lambda j:self.read(o[j])
   if t==13:continue
   if t==14:self.pc=self.labels[get(0)];continue
   if t==15:
    if get(0):self.pc=self.labels[get(1)]
    continue
   if t==16:self.sleep=get(0)/1000;return
   if t==17:self.pc=len(code);return
   if t==1:v=get(1)
   elif t==3:v=get(1)+get(2)
   elif t==4:v=get(1)-get(2)
   elif t==5:v=get(1)*get(2)
   elif t==6:v=get(1)/get(2)
   elif t==7:v=int(get(1)==get(2))
   elif t==8:v=int(get(1)<get(2))
   elif t==9:v=int(get(1)>get(2))
   elif t==10:v=int(bool(get(1)) and bool(get(2)))
   elif t==11:v=int(bool(get(1)) or bool(get(2)))
   elif t==12:v=int(not get(1))
   elif t==18:v=self.w.rng.randrange(int(get(1)))
   elif t==19:v=math.floor(get(1))
   elif t==20:v=get(1)%get(2)
   elif t==23:v=math.sqrt(get(1))
   elif t==24:v=math.degrees(math.atan2(get(1),get(2)))
   elif t==26:v=abs(get(1))
   else:raise AssertionError(t)
   self.write(o[0],v)
