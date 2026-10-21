"""Software-render the actual native level geometry, without a WebGL dependency."""
import json, math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
ROOT=Path(__file__).resolve().parents[1]
level=json.loads((ROOT/'dist/office-after-hours.json').read_text())
manifest=json.loads((ROOT/'docs/manifest.json').read_text())
fig=plt.figure(figsize=(17,10),facecolor='#0c171c')
fig.text(.05,.94,'AFTER HOURS',fontsize=32,color='#f0e8d3',weight='bold')
fig.text(.05,.905,'Ten offices. Three gems. Five hunts. One way out.',fontsize=14,color='#9db5b7')
ax=fig.add_axes([.04,.12,.34,.73]);ax.set_facecolor('#0c171c');ax.set_aspect('equal');ax.axis('off')
ax.add_patch(Rectangle((-8,-2),16,36,facecolor='#243a40',edgecolor='#8aa6a6',lw=2))
ax.add_patch(Rectangle((-2,-2),4,34,facecolor='#17454c',edgecolor='none'))
for r in manifest['rooms']:
 x,z,i=r['x'],r['z'],r['id'];left=-8 if x<0 else 2
 ax.add_patch(Rectangle((left,z-3),6,6,facecolor='#293c40',edgecolor='#83a0a0',lw=1.2))
 wallx=-2 if x<0 else 2
 ax.plot([wallx,wallx],[z-.7,z+.7],color='#e3c68d',lw=4)
 dx,_,dz=r['desk'];cx,_,cz=r['closet']
 ax.add_patch(Rectangle((dx-1.4,dz-.6),2.8,1.2,facecolor='#ac8051'))
 ax.add_patch(Rectangle((dx-.3,dz+1),.6,.6,facecolor='#6b8c92'))
 ax.add_patch(Rectangle((cx-.625,cz-.7),1.25,1.4,facecolor='#648177'))
 front=cx-(1 if x>0 else -1)*.625
 ax.plot([front,front],[cz-.645,cz+.645],color='#e3c68d',lw=2)
 ax.text(x,z-.4,f'{i:02}',ha='center',va='center',color='#e0e8e0',fontsize=11,weight='bold')
 ax.scatter([dx+.5,cx-(1 if x>0 else -1)*.83],[dz-.35,cz],s=15,c='#62e1de',zorder=5)
ax.text(0,14,'C O R R I D O R',rotation=90,ha='center',va='center',color='#8bc2c6',fontsize=10)
ax.plot([-1.2,1.2],[32,32],color='#71f7a8',lw=5)
ax.text(0,33,'EXIT',ha='center',va='center',color='#adffd5',fontsize=10,weight='bold')
ax.text(0,-1.2,'ENTRY',ha='center',va='center',color='#e3c68d',fontsize=10)
ax.set_xlim(-9,9);ax.set_ylim(-3,35)
fig.text(.08,.105,'FLOOR PLAN',color='#f0e8d3',fontsize=12,weight='bold')
fig.text(.08,.075,'Gold: door   ·   Cyan: hiding pad   ·   Green: closet',color='#9db5b7',fontsize=10)
a3=fig.add_axes([.38,.17,.59,.67],projection='3d',computed_zorder=False);a3.set_facecolor('#0c171c');a3.set_axis_off()
verts=[];colors=[]
def cuboid(p,s,c,yaw=0):
 x,y,z=p;sx,sy,sz=[v/2 for v in s]
 pts=[(x+math.cos(yaw)*dx*sx+math.sin(yaw)*dz*sz,z-math.sin(yaw)*dx*sx+math.cos(yaw)*dz*sz,y+dy*sy) for dx,dy,dz in [(-1,-1,-1),(1,-1,-1),(1,-1,1),(-1,-1,1),(-1,1,-1),(1,1,-1),(1,1,1),(-1,1,1)]]
 for face,shade in zip([[0,1,2,3],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],[.45,1,.68,.8,.65,.74]):
  verts.append([pts[i] for i in face]);colors.append(tuple(min(1,v*shade+.035) for v in c))
def world(p,offset,yaw):return (offset[0]+math.cos(yaw)*p['x']+math.sin(yaw)*p['z'],offset[1]+p['y'],offset[2]-math.sin(yaw)*p['x']+math.cos(yaw)*p['z'])
def angle(d):return 2*math.atan2(d['rotation']['y'],d['rotation']['w'])
def visit(nodes,offset=(0,0,0),yaw=0):
 for n in nodes:
  if 'levelNodeGroup' in n:
   d=n['levelNodeGroup'];visit(d['childNodes'],world(d['position'],offset,yaw),yaw+angle(d))
  elif 'levelNodeStatic' in n:
   d=n['levelNodeStatic'];p=world(d['position'],offset,yaw);s=tuple(d['scale'][k] for k in 'xyz')
   if p[1]<-2 or p[1]>3.4 or abs(p[0])>9:continue
   # cut outer walls low enough to see inside; retain partition geometry
   if s[1]>3:
    s=(s[0],.6,s[2]);p=(p[0],.3,p[2])
   c=tuple(d['color1'][k] for k in 'rgb')
   if s[0]>10 and s[2]>30:
    # Subdivide the large floor for correct painter sorting; same surface.
    for ix in range(8):
     for iz in range(18):
      cuboid((p[0]-s[0]/2+(ix+.5)*s[0]/8,p[1],p[2]-s[2]/2+(iz+.5)*s[2]/18),(s[0]/8,s[1],s[2]/18),c)
   else:cuboid(p,s,c,yaw+angle(d))
visit(level['levelNodes'])
coll=Poly3DCollection(verts,facecolors=colors,linewidths=.12,edgecolors=(.1,.15,.16,.2),zsort='average');a3.add_collection3d(coll)
a3.set_xlim(-9,9);a3.set_ylim(-3,35);a3.set_zlim(-.3,4);a3.set_box_aspect((18,38,8));a3.view_init(elev=50,azim=-48)
fig.text(.43,.18,'NATIVE GEOMETRY CUTAWAY',color='#f0e8d3',fontsize=12,weight='bold')
fig.text(.43,.145,'Ceiling removed and walls lowered for visibility. Doors shown closed.',color='#9db5b7',fontsize=10)
fig.text(.43,.10,'60s CALM  /  60s HUNT',color='#7ad9d0',fontsize=17,weight='bold')
fig.text(.43,.068,'EXPERIMENTAL BUILD — Quest play-test required',color='#d3ae78',fontsize=11)
fig.savefig(ROOT/'docs/office-after-hours-preview.png',dpi=150,facecolor=fig.get_facecolor());plt.close(fig)
print('Rendered actual generated geometry')
