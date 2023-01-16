import bpy
import numpy as np
import math
import random
#import addon_panels_particle_system.py as ps_panel

# global parameters
gravity = 30
time_step = 0.02


class Particle():
    def __init__(self):
        self.position = {'x': 0, 'y': 0, 'z': 0}
        self.velocity = {'x': 0, 'y': 0, 'z': 0}
        self.size = {'x': 1, 'y': 1, 'z': 1}
        self.lifetime = 10
        self.life = 0
        self.mass = 30
        self.obj = None
        
    def __str__(self):
        return f"Particle at position ({self.position['x']}, {self.position['y']}, {self.position['z']})"
    
    def set_position(self, x, y, z):
        self.position['x'] = x
        self.position['y'] = y
        self.position['z'] = z
        
    def set_size(self, x, y, z):
        self.size['x'] = x
        self.size['y'] = y
        self.size['z'] = z
    
    def initial_draw(self):
        sphere = bpy.ops.mesh.primitive_uv_sphere_add(radius=1, enter_editmode=False, align='WORLD', location=(self.position['x'], self.position['y'], self.position['z']), scale=(self.size['x'] * 0.2, self.size['y'] * 0.2, self.size['z'] * 0.2))
        self.obj = bpy.data.collections["Particles"].objects[-1]
        
    def start_smoke(self):
        sphere = bpy.ops.mesh.primitive_uv_sphere_add(radius=1, enter_editmode=False, align='WORLD', location=(self.position['x'], self.position['y'], self.position['z']), scale=(self.size['x'] * 0.2, self.size['y'] * 0.2, self.size['z'] * 0.2))
        self.obj = bpy.data.collections["Particles"].objects[-1]
        self.velocity["y"] = random.randint(-10, 10)
        self.velocity["z"] = random.randint(1, 5)
        self.velocity["x"] = random.randint(0, 10)
        #print("Generating mesh for particle", print(self.obj))
        # Add modifier:
        bpy.ops.object.modifier_add(type='COLLISION')
        
    #def collision(self):
        #for obj in bpy.data.collections["Obstacles"].objects:
            #if is_collision(get_BoundingBox(self.obj), get_BoundingBox(obj))
                
        
#def is_collision(bb1, bb2):
    #if 
        
# get bounding box of an object
def get_BoundingBox(obj):
    return [obj.matrix_world * Vector(corner) for corner in ob.bound_box]        


# update the particle data
def update(particles, is_gravity=False, is_smoke=False):
    for i, particle in enumerate(particles):
        if is_gravity:
        # math
            particle.velocity["z"] = particle.velocity["z"] + gravity * time_step
            particle.position["z"] = particle.position["z"] - particle.velocity["z"] * time_step
            #print(particle.position["z"])
        elif is_smoke:
            particle.position["y"] += particle.velocity["y"] * time_step
            particle.position["z"] += particle.velocity["z"] * time_step
            particle.position["x"] += particle.velocity["x"] * time_step
            #print(particle.position)
        
        particle.life += 1
        if particle.life >= particle.lifetime:
            particle.set_size(particle.size['x'] * 0.5, particle.size['y'] * 0.5, particle.size['z'] * 0.5)
            #particles.pop(i)
        # update linked object to this instance
        object = particle.obj
        object.location = np.array([particle.position["x"], particle.position["y"], particle.position["z"]])
        object.scale = np.array([particle.size["x"], particle.size["y"], particle.size["z"]])
        

# animate the particle system        
def animate(collection_name, keyframe):
    for obj in bpy.data.collections[collection_name].objects:
        print("Animating ", obj)
        obj.keyframe_insert(data_path = 'location', frame = keyframe)

def make_grid(particles):
    grid_size = len(particles)
    x = math.floor(math.sqrt(grid_size))
    y = math.ceil(grid_size/x)
    print("Grid size is ({0}, {1})".format(x, y)) 
    p_index = 0
    for i in range(0, x):
        for j in range(0, y):
            if p_index >= len(particles):
                break
            else:
                particles[p_index].set_position(0, i*2, j*2 + 30)
                p_index += 1
    
    
def clear():
    # deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.collections["Particles"].objects:
        # select the object
        obj.select_set(True)
        bpy.ops.object.delete(use_global=False, confirm=False)    


if __name__ == "__main__":
    clear()
    #register()
    
    is_gravity = False
    is_smoke = True
    
    particle_num = 200
    particles = [Particle() for p in range(particle_num)]
    if is_gravity:
        make_grid(particles)
        for particle in particles:
            print(particle)
            particle.initial_draw()
        
    frame_size = 60
    bpy.data.scenes["Scene"].frame_start = 0
    bpy.data.scenes["Scene"].frame_end = frame_size
    keyframe_ind = math.floor(frame_size * time_step)
    
    if particle_num < frame_size:
        ind = 1
    else:
        ind = math.floor(particle_num/frame_size)
    
    index = 0
    for frame in range(0, frame_size, keyframe_ind):
        print(frame)
        if is_smoke:
            for i in range(0, ind):
                if i + index < len(particles):
                    print("  ", i)
                    particles[i + index].start_smoke()
            index += ind
            update(particles[:index], is_gravity, is_smoke)
            animate("Particles", frame)
        elif is_gravity:
            update(particles, is_gravity, is_smoke)
            animate("Particles", frame)
        print("Objects in Particles:", len(bpy.data.collections["Particles"].objects))