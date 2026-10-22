"""Render actual generated vehicle/skeleton primitives for offline visual QA."""
from pathlib import Path
import importlib.util
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT=Path(__file__).resolve().parents[1]

def rotation(q):
    x,y,z,w=[q.get(k,0) for k in ('x','y','z','w')]
    return np.array([[1-2*y*y-2*z*z,2*x*y-2*z*w,2*x*z+2*y*w],
                     [2*x*y+2*z*w,1-2*x*x-2*z*z,2*y*z-2*x*w],
                     [2*x*z-2*y*w,2*y*z+2*x*w,1-2*x*x-2*y*y]])

def primitive(shape):
    if shape==1001:
        vertices=[];faces=[]
        for j in range(7):
            ph=np.pi*j/6
            for i in range(12):
                th=2*np.pi*i/12
                vertices.append((.5*np.sin(ph)*np.cos(th),.5*np.cos(ph),.5*np.sin(ph)*np.sin(th)))
        for j in range(6):
            for i in range(12):faces.append([j*12+i,j*12+(i+1)%12,(j+1)*12+(i+1)%12,(j+1)*12+i])
    elif shape==1002:
        vertices=[(.5*np.cos(2*np.pi*i/12),y,.5*np.sin(2*np.pi*i/12)) for y in [-.5,.5] for i in range(12)]
        faces=[list(range(12)),list(range(12,24))]+[[i,(i+1)%12,(i+1)%12+12,i+12] for i in range(12)]
    else:
        vertices=[(x,y,z) for x in [-.5,.5] for y in [-.5,.5] for z in [-.5,.5]]
        faces=[[0,1,3,2],[4,5,7,6],[0,1,5,4],[2,3,7,6],[0,2,6,4],[1,3,7,5]]
    return np.array(vertices),faces

def draw(ax,node,parent=np.eye(4),ignore_origin=False,polygons=None,colors=None):
    outer=polygons is None
    if outer:polygons=[];colors=[]
    kind=next(k for k in node if k.startswith('levelNode'))
    data=node[kind]
    mat=np.eye(4);mat[:3,:3]=np.eye(3) if ignore_origin else rotation(data.get('rotation',dict(w=1)))
    mat[:3,:3]@=np.diag([data.get('scale',{}).get(k,1) for k in 'xyz'])
    mat[:3,3]=[data.get('position',{}).get(k,0) for k in 'xyz'] if not ignore_origin else [0,0,0]
    transform=parent@mat
    if kind=='levelNodeGroup':
        for ch in data['childNodes']:draw(ax,ch,transform,polygons=polygons,colors=colors)
    elif kind=='levelNodeStatic':
        v,f=primitive(data.get('shape',1000));v=np.c_[v,np.ones(len(v))]@transform.T
        c=data.get('color1',{});color=[c.get(k,.5) for k in 'rgb']
        polys=[v[idx][:,[0,2,1]] for idx in f]
        for poly in polys:
            normal=np.cross(poly[1]-poly[0],poly[2]-poly[0]);norm=np.linalg.norm(normal)
            brightness=.65+.35*abs(np.dot(normal/max(norm,1e-8),np.array([.4,-.4,.82])))
            polygons.append(poly);colors.append(np.clip(np.array(color)*brightness,0,1))
    if outer:ax.add_collection3d(Poly3DCollection(polygons,facecolors=colors,edgecolors=(0,0,0,.14),linewidths=.15,zsort='average'))

def main():
    ctx={'__file__':str(ROOT/'src/build.py')}
    exec((ROOT/'src/build.py').read_text().split('MAP=')[0],ctx)
    for module in ['vehicles','monster']:
        spec=importlib.util.spec_from_file_location(module,ROOT/f'src/{module}.py')
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.build(ctx)
    models=[('SportCar','Sport car'),('Minivan1','Sliding-door minivan'),('ExplorerSUV','Blue SUV'),
            ('BlueStreetBike','Blue street motorcycle'),('RykerTrike','Three-wheel roadster'),
            ('Wreck1','Crushed car'),('Minivan2','Second minivan'),('Monster','Ghost skeleton')]
    fig=plt.figure(figsize=(16,9),facecolor='#101a21')
    for i,(name,title) in enumerate(models,1):
        ax=fig.add_subplot(2,4,i,projection='3d',facecolor='#14222b')
        draw(ax,ctx['names'][name],ignore_origin=True)
        if name=='Monster':ax.set(xlim=(-1,1),ylim=(-1,1),zlim=(0,2.7));ax.set_box_aspect((2,2,2.7))
        else:ax.set(xlim=(-1.5,1.5),ylim=(-2.8,2.8),zlim=(0,2.4));ax.set_box_aspect((3,5.6,2.4))
        ax.view_init(elev=23,azim=-135);ax.set_axis_off();ax.set_title(title,color='#e1eaf0',fontsize=12,pad=-12)
    fig.suptitle('PARKING LOT HORROR  |  Native primitive asset review',color='white',fontsize=20,y=.98)
    fig.text(.5,.015,'Actual generated geometry • Offline review; native lighting, particles and interactions require Quest playtesting',ha='center',color='#a8bac6',fontsize=10)
    fig.subplots_adjust(left=.01,right=.99,bottom=.04,top=.93,wspace=0,hspace=.02)
    output=ROOT/'docs/vehicles-and-monster-preview.png';output.parent.mkdir(exist_ok=True)
    fig.savefig(output,dpi=150,facecolor=fig.get_facecolor());print(output)

if __name__=='__main__':main()
