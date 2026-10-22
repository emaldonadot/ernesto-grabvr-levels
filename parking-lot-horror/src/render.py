"""Software geometry preview; not an engine screenshot. Roof omitted for inspection."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
ROOT=Path(__file__).resolve().parents[1]
FACES=((0,1,2,3),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))
def hull(points):
 p=sorted(set(map(tuple,points)))
 if len(p)<3:return np.array(p)
 def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 lower=[];upper=[]
 for q in p:
  while len(lower)>=2 and cross(lower[-2],lower[-1],q)<=0:lower.pop()
  lower.append(q)
 for q in reversed(p):
  while len(upper)>=2 and cross(upper[-2],upper[-1],q)<=0:upper.pop()
  upper.append(q)
 return np.array(lower[:-1]+upper[:-1])
CORNERS=np.array([[-1,-1,-1],[1,-1,-1],[1,-1,1],[-1,-1,1],[-1,1,-1],[1,1,-1],[1,1,1],[-1,1,1]])
def vector(d,default=0):return np.array([d.get(k,default) for k in 'xyz'])
def transform(d):
 q=d.get('rotation',{}); x,y,z,w=(q.get(k,0) for k in 'xyzw');w=w or (1 if not(x or y or z) else w)
 r=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)], [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)], [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
 t=np.eye(4);t[:3,:3]=r@np.diag(vector(d.get('scale',{}),1));t[:3,3]=vector(d.get('position',{}));return t
solids=[]
def visit(nodes,parent=np.eye(4)):
 for n in nodes:
  if 'levelNodeGroup' in n:
   d=n['levelNodeGroup'];visit(d.get('childNodes',[]),parent@transform(d))
  elif 'levelNodeStatic' in n:
   d=n['levelNodeStatic']; t=parent@transform(d); center=t[:3,3]
   if abs(center[0])>28 or abs(center[2])>31 or center[1]<-.5 or center[1]>3.2:continue
   scale=np.linalg.norm(t[:3,:3],axis=0)
   # Walls are lowered in this cutaway, while columns/vehicles stay full height.
   if scale[1]>3.5:
    t[:3,1]*=.45/scale[1];t[1,3]=.225
   c=tuple(d.get('color1',{}).get(k,.3) for k in 'rgb')
   if scale[0]>35 and scale[2]>55 and center[1]<0:
    # Tile the same floor surface to preserve 3D painter ordering.
    for ix in range(10):
     for iz in range(14):
      tile=t.copy();tile[:3,0]/=10;tile[:3,2]/=14
      tile[:3,3]=(t@np.array([-.5+(ix+.5)/10,0,-.5+(iz+.5)/14,1]))[:3]
      pts=(tile@np.column_stack((CORNERS*.5,np.ones(8))).T).T[:,:3]
      solids.append((pts,c,center[1]))
   else:
    pts=(t@np.column_stack((CORNERS*.5,np.ones(8))).T).T[:,:3]
    solids.append((pts,c,center[1]))

def main():
 level=json.loads((ROOT/'dist/parking-lot-horror.json').read_text());visit(level['levelNodes'])
 fig=plt.figure(figsize=(18,11),facecolor='#101b21');fig.text(.045,.94,'PARKING LOT HORROR',fontsize=31,weight='bold',color='#eee7d5')
 fig.text(.045,.90,'60 marked spaces  /  9 vehicles  /  10 players  /  5 skeleton hunts',fontsize=14,color='#9fb9bb')
 ax=fig.add_axes([.035,.15,.35,.70]);ax.set_facecolor('#101b21');ax.set_aspect('equal');ax.axis('off')
 for pts,c,y in sorted(solids,key=lambda s:s[2]):
  # Convex hull makes rotation-aware top-down silhouettes of actual primitives.
  p=hull(pts[:,[0,2]])
  if len(p)<3:continue
  ax.add_patch(Polygon(p,facecolor=c,edgecolor=(.05,.08,.10,.4),linewidth=.2))
 for ri,z in enumerate((-23.75,-11.65,-6.05,6.05,11.65,23.75)):
  ax.text(-19.7,z,chr(65+ri),color='#e7d7ac',fontsize=11,ha='center',va='center',weight='bold')
 ax.text(24,0,'SPECTATOR',color='#a8e4ea',fontsize=9,rotation=90,ha='center',va='center')
 ax.text(0,-28,'START',color='#f4d695',fontsize=8,ha='center');ax.text(0,30,'ESCAPE GATE',color='#9ef2bc',fontsize=9,ha='center')
 ax.set_xlim(-22.5,28);ax.set_ylim(-31,32)
 a3=fig.add_axes([.38,.16,.60,.69],projection='3d');a3.set_facecolor('#101b21');a3.set_axis_off();verts=[];colors=[]
 for pts,c,y in solids:
  for face,shade in zip(FACES,(.45,1,.65,.80,.65,.75)):
   verts.append([(pts[i,0],pts[i,2],pts[i,1]) for i in face]);colors.append(tuple(min(1,v*shade+.025) for v in c))
 a3.add_collection3d(Poly3DCollection(verts,facecolors=colors,linewidths=.08,edgecolors=(.1,.15,.17,.20),zsort='average'))
 a3.set_xlim(-22,28);a3.set_ylim(-30,31);a3.set_zlim(-.3,4.5);a3.set_box_aspect((50,61,16),zoom=.87);a3.view_init(elev=53,azim=-135)
 fig.text(.045,.105,'TOP-DOWN GEOMETRY',fontsize=12,weight='bold',color='#eee7d5')
 fig.text(.405,.105,'PARKING STRUCTURE CUTAWAY',fontsize=12,weight='bold',color='#eee7d5')
 fig.text(.045,.068,'Software preview of generated primitives. Roof omitted and tall walls lowered for visibility.',fontsize=11,color='#9fb9bb')
 fig.text(.045,.038,'Actual level has a covered roof. Native lighting, particles, animation and Quest performance require in-game testing.',fontsize=10,color='#d2b682')
 (ROOT/'docs').mkdir(exist_ok=True);fig.savefig(ROOT/'docs/parking-lot-horror-preview.png',dpi=150,facecolor=fig.get_facecolor());plt.close(fig)
 print(f'Rendered {len(solids)} generated static primitives')
if __name__=='__main__':main()
