__author__ = "guozi"
__version__ = "2020.07.01"

import rhinoscriptsyntax as rs

# function definition
def face_pt(face,u,v,z):
    '''
    calculate the new center point of a face
    '''
    pts=[vertices[f] for f in face]
    vpface=len(pts)
    
    mid=(1-u)*(1-v)*pts[0] + u*(1-v)*pts[1] + u*v*pts[2] + (1-u)*v*pts[-1]
    vec_mid=[p-mid for p in pts]
    vec_cross=[rs.VectorCrossProduct(vec_mid[(i+1)%vpface],vec_mid[i]) for i in range(vpface)]
    
    for i in range(1,vpface):
        vec_cross[0]=vec_cross[i]+vec_cross[0]
        
    return mid+vec_cross[0]*z

def avg_pt(*pts):
    '''
    average point of a list of points
    '''
    v=pts[0]
    for p in pts[1:]:
        v=v+p
    v=v/len(pts)
    return v

# initialize
if u is None:
    u=0.5
if v is None:
    v=0.5
if z is None:
    z=0
if ratio1 is None:
    ratio1=0.5
if ratio2 is None:
    ratio2=0.5

print(u,v,z)

# vertices
vertices=rs.MeshVertices(quad_mesh)
num_vertices=len(vertices)

# faces
faces=rs.MeshFaceVertices(quad_mesh)
num_faces=len(faces)
vpface=[len(f) for f in faces]

# edges
half_edges={(faces[i][j],faces[i][(j+1)%vpface[i]]):i for i in range(num_faces) for j in range(vpface[i])}
edges=[(i,j) for i,j in list(half_edges.keys()) if i < j]
num_edges=len(edges)

# neighbors
vs_nbe=[[] for _ in range(num_vertices)]
for i in range(num_edges):
    v1,v2=edges[i]
    vs_nbe[v1].append(i)
    vs_nbe[v2].append(i)
print('vertices neighbor edges',vs_nbe)

es_nbf=[[half_edges[(i,j)],half_edges[(j,i)]] for i,j in edges]
print('edges neighbor faces',es_nbf)

vs_nbf=[[] for _ in range(num_vertices)]
for i in range(num_faces):
    for vf in faces[i]:
        vs_nbf[vf].append(i)
print('vertices neighbor faces',vs_nbf)

# calculate face mid points
mid_pt_f=[face_pt(f,u,v,z) for f in faces]

# calculate edge mid points
mid_pt_e=[(vertices[edges[i][0]]+vertices[edges[i][1]])*0.5*ratio1 + (mid_pt_f[es_nbf[i][0]]+mid_pt_f[es_nbf[i][1]])*0.5*(1-ratio1) for i in range(num_edges)]
print(mid_pt_e)

# calculate avg point between adjacent faces
avg_pt_vs=[avg_pt(*[mid_pt_f[f] for f in nb]) for nb in vs_nbf]
avg_pt_vs=[a*ratio2+b*(1-ratio2) for a,b in zip(avg_pt_vs, vertices)]
print(avg_pt_vs)

# construct new mesh
half_edge_2_edge={(v1,v2):i for i in range(num_edges) for v1,v2 in [edges[i],edges[i][::-1]] }
print(half_edge_2_edge)

new_vertices=mid_pt_f+mid_pt_e+avg_pt_vs
new_faces=[]

for i in range(num_faces):
    face_vs=faces[i]
    face_vs_num=vpface[i]
    for j in range(face_vs_num):
        current=face_vs[j] # current vertices id
        prev=face_vs[(j-1+face_vs_num)%face_vs_num] # previous vertices id
        next=face_vs[(j+1)%face_vs_num] # next vertices id
        
        prev=half_edge_2_edge[(current,prev)] # previous edge id
        next=half_edge_2_edge[(current,next)] # next edge id
        
        new_faces.append([i, num_faces+prev, num_faces+num_edges+current, num_faces+next])

a = rs.AddMesh(new_vertices,new_faces)
#print(face_pt(faces[0],u,v,z))