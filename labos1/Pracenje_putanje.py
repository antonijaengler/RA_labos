import bpy
import numpy as np
import math
import pdb
import gpu
from gpu_extras.batch import batch_for_shader

def animate(start_location, T_kontrolni_poligon, B, B_der, step, frame_size):
    # za svaki segment krivulje -> 4 po 4 točke
    segment_index =  len(T_kontrolni_poligon) - 3 # math.ceil(len(T_kontrolni_poligon) / 4)
    print("Broj iteracija: ", segment_index)
    keyframe_index = (frame_size / segment_index) * step
    keyframe = 0
    spline = []
    for s in range(0, segment_index):
        print(s)
        # za t od 0 do 1
        t, fi = 0.0, 0.0
        #p = np.array([[0, 1, 0]*int(1 / step)])
        p = os = [[0], [0], [0]]
        print("p:", p)
        while t <= 0.9:
            print(" ", t)
            print(" tocke: ", T_kontrolni_poligon[int(s) : int(s) + 4, :])
            
            # odrediti ciljnu orijentaciju
            p = np.array([t ** 2, t, 1]) * (1/2) @ B_der @ T_kontrolni_poligon[int(s) : int(s) + 4, :]
            print("  ", p)
            
            # izračunaj os rotacije
            os = np.cross(start_location, p)
            print("  rotacija:", os)
            
            # izračunaj kut rotacije
            if np.dot(np.linalg.norm(palma.location), np.linalg.norm(p)) == 0:
                fi = 0
            else:
                fi = np.cos(np.dot(start_location, p) / np.dot(np.linalg.norm(start_location), np.linalg.norm(p)))
            print("  fi: ", fi)
            
            # izračunaj translaciju
            trans = np.array([t **3, t ** 2, t, 1]) * (1/6) @ B @ T_kontrolni_poligon[int(s) : int(s) + 4, :]
            print("  translacija: ", trans)
            
            # izračunaj orijentaciju
            p_der = np.array([2*t, 1, 0]) * (1/2) @ B_der @ T_kontrolni_poligon[int(s) : int(s) + 4, :]
            u = np.cross(p, p_der)
            v = np.cross(p, u)
            R = np.array([[p[0], u[0], v[0]], [p[1], u[1], v[1]], [p[2], u[2], v[2]]])
            print("    R: ", R)
            if np.linalg.det(R) == 0:
                os = np.array([palma.rotation_quaternion[1], palma.rotation_quaternion[2], palma.rotation_quaternion[3]])
            else:
                os = trans @ np.linalg.inv(R)
            print("  nova rotacija: ", os)
            
            # pomakni objekt (umetni keyframe)
            print("keyframe = ", keyframe)
            palma.rotation_quaternion = [fi, os[0], os[1], os[2]]
            palma.keyframe_insert(data_path = "rotation_quaternion", frame = keyframe)
            palma.location = trans
            palma.keyframe_insert(data_path = "location", frame = keyframe)
            keyframe += keyframe_index
            
            # crtaj tangente
            #print("---Crtam: ", p)
            #print("   do : ", trans)
            #print("    => ", trans + p)
            draw([trans, trans + p], "Tangents", 'tangent')
            
            spline.append(trans)
            t += step
    #print(spline)
    draw(spline, "Curves", 'B-spline')
            
    
def draw(vertices, collection, name):
    # create the Curve Datablock  
    data = bpy.data.curves.new(name, type='CURVE')
    data.dimensions = '3D'
    
    # map coords to spline
    polyline = data.splines.new('POLY')
    polyline.points.add(len(vertices) - 1)
    for i, vertex in enumerate(vertices):
        x, y, z = vertex
        polyline.points[i].co = (x, y, z, 1)
        
    # create Object
    obj = bpy.data.objects.new(name, data)
    
    # attach to collection
    bpy.data.collections[collection].objects.link(obj)
    
    
def deleteObjects(collection_name):
    # Get the collection from its name
    collection = bpy.data.collections[collection_name]

    for obj in [o for o in collection.objects]:
        # Delete the object
        bpy.data.objects.remove(obj)
    

palma = bpy.data.collections["Collection"].objects["palma"]
kocka = bpy.data.collections["Collection"].objects["kocka"]
palma.animation_data_clear()

B = np.array([[-1, 3, -3, 1], [3, -6, 3, 0], [-3, 0, 3, 0], [1, 4, 1, 0]])    
B_der = np.array([[-1, 3, -3, 1], [2, -4, 2, 0], [-1, 0, 1, 0]])
step = 0.1

T_kontrolni_poligon = np.array([[0, 1, 0], [0, 1, 1], [0, 0, 1], [0, -1, 1], [0, -1, 0]])
print("Tocke kontrolnog poligona: ", T_kontrolni_poligon)

spirala = np.array([[0, 0, 0], [0, 10, 5], [10, 10, 10], [10, 0, 15], [0, 0, 20], [0, 10, 25], [10, 10, 30], [10, 0, 35], [0, 0, 40], [0, 10, 45], [10, 10, 50], [10, 0, 55]])

# postavi početne vrijednosti
#palma.location = T_kontrolni_poligon[0]
palma.location = spirala[0]
palma.keyframe_insert(data_path = "location", frame = 0)
palma.rotation_quaternion = [0, 0, 1, 0]
palma.keyframe_insert(data_path = "rotation_quaternion", frame = 0)

frame_size = 60
bpy.data.scenes["Scene"].frame_start = 0
bpy.data.scenes["Scene"].frame_end = frame_size

# obriši sve prijašnje elemente
deleteObjects("Tangents")
deleteObjects("Curves")

# animiraj
animate(palma.location, spirala, B, B_der, step, frame_size)


