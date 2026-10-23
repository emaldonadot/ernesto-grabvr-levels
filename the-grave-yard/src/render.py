"""Render the serialized primitive layout, not a GRAB engine screenshot.

Includes actual group transforms. Sky objects are omitted from the floor plan.
"""
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]


def multiply(a,b):
    return [[sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def transform(d):
    q=d.get('rotation',{}); x,y,z,w=(q.get(k,0) for k in 'xyzw')
    w=w or (1 if not (x or y or z) else 0)
    r=[[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
       [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
       [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]]
    p=d.get('position',{});s=d.get('scale',{})
    return [[r[i][j]*s.get('xyz'[j],1) for j in range(3)]+[p.get('xyz'[i],0)] for i in range(3)]+[[0,0,0,1]]


def main():
    data=json.loads((ROOT/'dist/the-grave-yard.json').read_text())
    image=Image.new('RGB',(1500,1250),'#101a20');draw=ImageDraw.Draw(image)
    try:
        title=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',42)
        body=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
    except OSError:
        title=body=ImageFont.load_default()
    draw.text((55,28),'THE GRAVE YARD',font=title,fill='#ede5ca')
    draw.text((55,88),'Serialized layout preview • 16 graves • 3 protective gems • 5 zombie hunts',font=body,fill='#a9bdba')
    identity=[[int(i==j) for j in range(4)] for i in range(4)]
    solids=[]
    def walk(nodes,parent):
        for n in nodes:
            if 'levelNodeGroup' in n:
                d=n['levelNodeGroup'];walk(d.get('childNodes',[]),multiply(parent,transform(d)))
            elif 'levelNodeStatic' in n:
                d=n['levelNodeStatic']; t=multiply(parent,transform(d))
                if t[1][3]>12 or t[1][3]<-5: continue
                corners=[]
                for x,z in ((-.5,-.5),(.5,-.5),(.5,.5),(-.5,.5)):
                    p=[sum(t[i][k]*v for k,v in enumerate((x,0,z,1))) for i in range(3)]
                    corners.append((720+p[0]*14,620-p[2]*14))
                color=tuple(max(0,min(255,int(d.get('color1',{}).get(k,.35)*255))) for k in 'rgb')
                solids.append((t[1][3],corners,color,d.get('shape',1000)))
    walk(data['levelNodes'],identity)
    for y,p,color,shape in sorted(solids,key=lambda s:s[0]):
        if shape==1001:
            draw.ellipse((min(v[0] for v in p),min(v[1] for v in p),max(v[0] for v in p),max(v[1] for v in p)),fill=color)
        else:
            draw.polygon(p,fill=color,outline='#29302a')
    draw.text((735,990),'START',font=body,fill='#cbd3c0')
    draw.text((775,1075),'GATE / FINISH',font=body,fill='#efda9e')
    draw.text((1160,600),'SPECTATORS',font=body,fill='#a9d4df')
    spec=json.loads((ROOT/'docs/manifest.json').read_text())
    for i,item in enumerate(spec['loot'],1):
        x,y,z=item['position'];px,pz=720+x*14,620-z*14
        draw.ellipse((px-5,pz-5,px+5,pz+5),fill='#7affd7')
        draw.text((px+9,pz-8),f'GEM {i}',font=body,fill='#7affd7')
    draw.text((40,1165),'Top view • north at top • sky omitted • geometry and state positions from JSON',font=body,fill='#a9bdba')
    draw.text((40,1200),'Software preview only. Headset appearance, interaction and multiplayer require Quest testing.',font=body,fill='#8ca6a9')
    output=ROOT/'docs/the-grave-yard-preview.png'; output.parent.mkdir(exist_ok=True)
    image.save(output)
    print(output)


if __name__=='__main__':
    main()
