import bpy, json, base64, struct, math
from mathutils import Matrix, Vector
import numpy as np
bpy.ops.wm.open_mainfile(filepath='oga/minotaur.blend')
sc=bpy.context.scene
arm=bpy.data.objects['MinotaurArm']
arm.animation_data.action=bpy.data.actions['Action.005']
bones=[b.name for b in arm.data.bones]; bidx={n:i for i,n in enumerate(bones)}
# basis change: blender (x,y,z) -> ours (-x, z, y)  (forward -Y -> -Z, up Z -> Y)
Cm=Matrix(((-1,0,0,0),(0,0,1,0),(0,1,0,0),(0,0,0,1)))
arm.data.pose_position='REST'; sc.frame_set(1)
dg=bpy.context.evaluated_depsgraph_get()
Ainv=arm.matrix_world.inverted()
MATCOL={'Fur':(0.46,0.30,0.20),'Horns':(0.86,0.80,0.66),'Black':(0.08,0.07,0.06),'Skin':(0.62,0.48,0.36),'SkinNoNormal':(0.62,0.48,0.36),
        'Gold':(0.85,0.55,0.18),'RoughWood':(0.42,0.30,0.18),'Iron':(0.28,0.28,0.30),'Leather':(0.32,0.24,0.18),'Steel':(0.70,0.72,0.76)}
P=[];N=[];UV=[];COL=[];TEX=[];J=[];W=[];IDX=[]
def add_obj(name, fixed_bone=None):
    o=bpy.data.objects[name]; oe=o.evaluated_get(dg); me=oe.to_mesh()
    M=Ainv@oe.matrix_world; Mn=M.to_3x3().inverted().transposed()
    me.calc_loop_triangles()
    uvl=me.uv_layers.active.data if me.uv_layers.active else None
    gnames={g.index:g.name for g in o.vertex_groups}
    base=len(P)//3
    for li,l in enumerate(me.loops):
        v=me.vertices[l.vertex_index]
        p=M@v.co; n=(Mn@me.corner_normals[li].vector).normalized()
        P.extend([p.x,p.y,p.z]); N.extend([n.x,n.y,n.z])
        uv=uvl[li].uv if uvl else (0,0); UV.extend([uv[0],1-uv[1]])
        if fixed_bone: js=[bidx[fixed_bone],0,0,0]; ws=[1,0,0,0]
        else:
            gs=sorted([(g.weight,gnames.get(g.group)) for g in v.groups if gnames.get(g.group) in bidx], reverse=True)[:4]
            tot=sum(w for w,_ in gs) or 1
            js=[bidx[n] for _,n in gs]+[0]*(4-len(gs)); ws=[w/tot for w,_ in gs]+[0]*(4-len(gs))
        J.extend(js); W.extend(ws)
    for tri in me.loop_triangles:
        mat=me.materials[tri.material_index].name if me.materials and me.materials[tri.material_index] else 'Skin'
        for li in tri.loops:
            IDX.append(base+li)
    # per-loop color/tex from polygon material
    for poly in me.polygons:
        mat=me.materials[poly.material_index].name if me.materials and me.materials[poly.material_index] else 'Skin'
        c=MATCOL.get(mat,(0.5,0.5,0.5)); t=1 if mat in('Fur','Skin','SkinNoNormal') else 0
        for li in poly.loop_indices: pass
    # fill COL/TEX in loop order
    colmap=[None]*len(me.loops)
    for poly in me.polygons:
        mat=me.materials[poly.material_index].name if me.materials and me.materials[poly.material_index] else 'Skin'
        for li in poly.loop_indices: colmap[li]=mat
    for li in range(len(me.loops)):
        mat=colmap[li] or 'Skin'; c=MATCOL.get(mat,(0.5,0.5,0.5)); COL.extend(c); TEX.append(1 if mat in('Fur','Skin','SkinNoNormal') else 0)
    print(name,'loops',len(me.loops),'tris',len(me.loop_triangles))
    oe.to_mesh_clear()
add_obj('Minotaur'); add_obj('WarAxe','Hand.Right'); add_obj('Circle','Head')
# vertices are in armature space (blender axes). Convert + normalise: feet on y=0, centred, height 1.55
pts=np.array(P).reshape(-1,3)
pts_c=np.array([[ -p[0], p[2], p[1]] for p in pts])  # Cm applied
mn=pts_c.min(0); mx=pts_c.max(0); h=mx[1]-mn[1]; s=1.55/h
cx=(mn[0]+mx[0])/2; cz=(mn[2]+mx[2])/2
Nm=Matrix.Translation(Vector((-cx*s,-mn[1]*s,-cz*s)))@Matrix.Scale(s,4)
Q=Nm@Cm; Qi=Q.inverted()
pts_f=np.array([list((Q@Vector(p))[:3]) for p in pts])
nrm=np.array(N).reshape(-1,3); nrm_f=np.array([list((Cm.to_3x3()@Vector(n)).normalized()) for n in nrm])
print('bbox', pts_f.min(0), pts_f.max(0), 'scale', s)
# animation: skin matrices per frame
arm.data.pose_position='POSE'
frames=24; anim=[]
for f in range(1,frames+1):
    sc.frame_set(f); dg=bpy.context.evaluated_depsgraph_get()
    for bn in bones:
        pb=arm.pose.bones[bn]; S=pb.matrix@arm.data.bones[bn].matrix_local.inverted()
        Sp=Q@S@Qi
        for r in range(3): anim.extend([Sp[r][0],Sp[r][1],Sp[r][2],Sp[r][3]])
# dedupe identical loops
keys={}; remap=[]; keep=[]
for i in range(len(pts_f)):
    k=(tuple(np.round(pts_f[i],4)),tuple(np.round(nrm_f[i],2)),tuple(np.round(UV[2*i:2*i+2],4)),tuple(COL[3*i:3*i+3]),TEX[i],tuple(J[4*i:4*i+4]),tuple(np.round(W[4*i:4*i+4],3)))
    if k not in keys: keys[k]=len(keep); keep.append(i)
    remap.append(keys[k])
pts_f=pts_f[keep]; nrm_f=nrm_f[keep]
UV=[UV[2*i+c] for i in keep for c in range(2)]; COL=[COL[3*i+c] for i in keep for c in range(3)]; TEX=[TEX[i] for i in keep]
J=[J[4*i+c] for i in keep for c in range(4)]; W=[W[4*i+c] for i in keep for c in range(4)]
IDX=[remap[i] for i in IDX]
def b64(a): return base64.b64encode(a.tobytes()).decode()
nv=len(pts_f)
out={
 'nv':nv,'bones':len(bones),'frames':frames,
 'pos':b64(np.round(pts_f/1.6*32767).astype(np.int16)),'posScale':1.6,
 'nrm':b64(np.round(nrm_f*127).astype(np.int8)),
 'uv':b64(np.round(np.clip(np.array(UV),0,1)*65535).astype(np.uint16)),
 'col':b64(np.round(np.array(COL)*255).astype(np.uint8)),
 'tex':b64(np.array(TEX).astype(np.uint8)),
 'j':b64(np.array(J).astype(np.uint8)),'w':b64(np.round(np.array(W)*255).astype(np.uint8)),
 'idx':b64(np.array(IDX).astype(np.uint16)),
 'anim':b64(np.array(anim).astype(np.float32)),
 'clips':{'idle':[0,3],'run':[4,11],'swing':[12,15],'block':[16,17],'die':[18,23]},
}
json.dump(out,open('mino.json','w'))
print('verts',nv,'idx',len(IDX),'json bytes',len(json.dumps(out)))
# texture 256x256 jpeg
img=bpy.data.images['catfur.jpg']; img.scale(256,256)
sc.render.image_settings.file_format='JPEG'; sc.render.image_settings.quality=72
img.save_render('catfur256.jpg', scene=sc)
