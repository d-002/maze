import os
import pygame
import numpy as np

from pygame.math import Vector3

from math import *
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *

from laby import *
from entities import *

def initOpenGl():
    glViewport(0, 0, W, H)

    # enable the use of colors and textures
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_TEXTURE_2D)

    glClearColor(0.15, 0.2, 0.1, 0.0)
    glColor(base_color)

    # lights: set up camera light
    glEnable(GL_LIGHT0)
    glLight(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.6, 0.4))
    glLight(GL_LIGHT0, GL_LINEAR_ATTENUATION, 1)

    glEnable(GL_LIGHT1)
    glEnable(GL_LIGHT2)
    glEnable(GL_LIGHT3)

    # fog
    glEnable(GL_FOG)
    glFogfv(GL_FOG_COLOR, (0.15, 0.2, 0.1))
    glFogi(GL_FOG_MODE, GL_EXP2)
    glFogf(GL_FOG_DENSITY, 0.2)

    # set up 3d shader
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)

    # set up transparent surfaces handling
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glLoadIdentity()

def init3d():
    # lighting
    glEnable(GL_LIGHTING)

    # projection mode
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOV + 10*player.sprint, W/H, 0.01, render_distance)
    glMatrixMode(GL_MODELVIEW)

    # depth test (draw nearest surfaces on top)
    glEnable(GL_DEPTH_TEST)

    glLoadIdentity()

    # get the camera matrix after rotating
    cosx, sinx, cosy, siny = cos(player.cam_rot.x), sin(player.cam_rot.x), cos(player.cam_rot.y), sin(player.cam_rot.y)
    matrix = np.array([[ cosy,         0,            -siny,        0 ],  # right
                       [ sinx*siny,    cosx,         sinx*cosy,    0 ],  # top
                       [ cosx*siny,    -sinx,        cosx*cosy,    0 ],  # front
                       [ player.cam.x, player.cam.y, player.cam.z, 1 ]]) # pos
    glLoadMatrixd(sum([list(row) for row in np.linalg.inv(matrix)], start=[]))

    # light from the camera
    glLight(GL_LIGHT0, GL_POSITION, (player.cam.x, player.cam.y, player.cam.z, 1))

    # lights from the nearest light sources
    places = sorted(lights, key=lambda pos: pos.distance_to(player.cam))[:3]
    for var, pos in zip([GL_LIGHT1, GL_LIGHT2, GL_LIGHT3], places):
        glLight(var, GL_POSITION, (pos.x, pos.y, pos.z, 1))
        glLight(var, GL_DIFFUSE, (0.8, 0.8, 1))
        glLight(var, GL_QUADRATIC_ATTENUATION, 3)

def init2d():
    # projection mode
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, W, H, 0)
    glMatrixMode(GL_MODELVIEW)

    # disable lighting
    glDisable(GL_LIGHTING)

    # disable depth test (incompatible with 2d blending)
    glDisable(GL_DEPTH_TEST)

def load_options():
    global options
    # default values
    options = {'move_keys': 'wasd', 'fov': 70, 'render_distance': 20}

    try:
        # read options file
        with open('files/options.txt') as f:
            for line in f.read().split('\n'):
                name, value = line.split('=')
                options[name.strip()] = value.strip()

        # format options
        options['fov'] = min(max(int(options['fov']), 30), 120)
        options['render_distance'] = int(options['render_distance'])
    except Exception as e:
        print('Error reading options.txt:')
        print(type(e), e)

    # add missing values
    with open('files/options.txt', 'w') as f:
        f.write('\n'.join(['%s = %s' %(key, value) for key, value in options.items()]))

def init_tex():
    global textures
    # labyrinth textures
    names = walls_names+['floor', 'mossyfloor', 'ceil', 'lightceil']+['liftfloor', 'liftwall', 'liftceil', 'gate']
    textures = {name: to_texture(pygame.image.load('files/flats/%s.png' %name)) for name in names}

    # text
    for name in [str(x) for x in range(10)]+['level']:
        surf = pygame.image.load('files/text/%s.png' %name)
        textures[name] = [to_texture(surf), surf.get_size()]

    # plain colors need a texture
    textures['white'] = to_texture(pygame.image.load('files/textures/white.png'))

    # monsters textures: {[ID, size] for each texture}
    for name, texname in monsters_names:
        group = {}
        for x in range(8): # here are all the oriented textures
            x_ = str(x+1)
            for anim in range(4):
                group['walk%s%d' %(anim, x)] = 'ABCD'[anim]+x_
            group['aim%d' %x] = 'E'+x_
            group['shoot%d' %x] = 'F'+x_
            group['dmg%d' %x] = 'G'+x_
        for die in range(9):
            group['die%d' %die] = 'MNOPQRSTU'[die]+'0'

        for tex in group:
            surf = pygame.image.load('files/monsters/%s/%s%s.png' %(name, texname, group[tex]))
            group[tex] = [to_texture(surf), surf.get_size()]
        textures[name] = group

def to_texture(surf):
    # makes a texture readable by OpenGl
    texture_data = pygame.image.tostring(surf, 'RGBA', True)
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

    w, h = surf.get_size()
    gluBuild2DMipmaps(GL_TEXTURE_2D, 4, w, h, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)

    return texture_id

def update_hud(first=False):
    # update HUD from its surface
    global hud
    if not first:
        glDeleteTextures(1, [hud])
    hud = to_texture(hud_surf)

def make_lab(m, n):
    display_list = glGenLists(1) # create a display list
    glNewList(display_list, GL_COMPILE)
    lab = to_blocks(gen(n, m), len(walls_names)) # generate a labyrinth
    lights = [] # where the ceiling lights are

    # draw the labyrinth
    normals = [(0, 0, -1), (1, 0, 0), (0, 0, 1), (-1, 0, 0)]
    offset = [[(0, 0), (1, 0)], [(1, 0), (1, 1)], [(1, 1), (0, 1)], [(0, 1), (0, 0)]]
    n, m = n*2 + 1, m*2 + 1
    for z in range(n):
        for x in range(m):
            todo = [] # walls to draw
            value = lab[z][x]
            if value > 0:
                if (0, 1) in [(x, z-1), (x+1, z), (x, z+1), (x-1, z)]: # start: lift
                    tex = textures['liftwall']
                else:
                    tex = textures[walls_names[value-1]] # "normal" wall texture
                if not z or (lab[z-1][x] <= 0):
                    todo.append((0, tex))
                if x == m-1 or (lab[z][x+1] <= 0):
                    todo.append((1, tex))
                if z == n-1 or (lab[z+1][x] <= 0):
                    todo.append((2, tex))
                if not x or (lab[z][x-1] <= 0):
                    todo.append((3, tex))
            elif value < 0:
                spawn = Vector3(x+0.5, 0, z+0.5)
                if value == -1:
                    entities.append(Monster(spawn, 'SoldierGun', 50))
                if value == -2:
                    entities.append(Monster(spawn, 'SoldierShotgun', 100))

            for face, tex in todo:
                a, b = offset[face]

                glBindTexture(GL_TEXTURE_2D, tex)
                glBegin(GL_QUADS)
                glNormal3dv(normals[face])
                glTexCoord2f(0, 0)
                glVertex3f(x+a[0], 0, z+a[1])
                glTexCoord2f(1, 0)
                glVertex3f(x+b[0], 0, z+b[1])
                glTexCoord2f(1, 1)
                glVertex3f(x+b[0], 1, z+b[1])
                glTexCoord2f(0, 1)
                glVertex3f(x+a[0], 1, z+a[1])
                glEnd()

            # floor and ceiling: only add them if visible
            if value <= 0:
                if (x, z) == (0, 1):
                    floor = 'liftfloor'
                    ceil = 'liftceil'
                    lights.append(Vector3(x+0.5, 0.7, z+0.5))
                else:
                    if randint(0, 4):
                        floor = 'floor'
                    else:
                        floor = 'mossyfloor'
                    if randint(0, 8) and (x, z) != (m-1, n-2):
                        ceil = 'ceil'
                    else:
                        ceil = 'lightceil'
                        lights.append(Vector3(x+0.5, 0.7, z+0.5))
                for y, normal, name in [(0, 1, floor), (1, -1, ceil)]:
                    glBindTexture(GL_TEXTURE_2D, textures[name])
                    glBegin(GL_QUADS)
                    glNormal3f(0, normal, 0)
                    for dx, dz in [(0, 0), (1, 0), (1, 1), (0, 1)]:
                        glTexCoord2f(dx, dz)
                        glVertex3f(x+dx, y, z+dz)
                    glEnd()

    # lift/gate out of the labyrinth
    for x, z, normx, tex in [(0, 1, 1, 'liftwall'), (m, n-2, -1, 'gate')]:
        glBindTexture(GL_TEXTURE_2D, textures[tex])
        glNormal3f(normx, 0, 0)
        glBegin(GL_QUADS)
        for y, dz in [(0, 0), (1, 0), (1, 1), (0, 1)]:
            glTexCoord2f(y, 1-dz)
            glVertex(x, y, z+dz)
        glEnd()

    # end the display list
    glEndList()
    return lab, lights, display_list

def new_level():
    global level, lab, entities, lights, lab_display
    level += 1

    if lab_display is not None: # need to delete previous lab
        glDeleteLists(lab_display, 1)

    entities = [player]
    lab, lights, lab_display = make_lab(2 + floor(level/2), 2 + ceil(level/2))
    send_lists(lab, entities)

def lift(first=False):
    global lights
    lights_old = lights[:] # backup them to reuse

    # generate a lift
    lift = glGenLists(1)
    glNewList(lift, GL_COMPILE)

    if first:
        delay, floors = 6300, 5 # follow the music
    else:
        delay, floors = 3000, 3

    normals = [(0, 0, 1), (-1, 0, 0), (0, 0, -1), (1, 0, 0)]
    offset = [[(0, 0), (1, 0)], [(1, 0), (1, 1)], [(1, 1), (0, 1)], [(0, 1), (0, 0)]]
    for y in range(floors):
        for face in range(4):
                a, b = offset[face]

                if (y, face) in [(floors-1, 3), (0, 1)]:
                    tex = textures['gate']
                else:
                    tex = textures['liftwall']
                glBindTexture(GL_TEXTURE_2D, tex)
                glBegin(GL_QUADS)
                glNormal3dv(normals[face])
                glTexCoord2f(0, 0)
                glVertex3f(a[0], y, a[1])
                glTexCoord2f(1, 0)
                glVertex3f(b[0], y, b[1])
                glTexCoord2f(1, 1)
                glVertex3f(b[0], y+1, b[1])
                glTexCoord2f(0, 1)
                glVertex3f(a[0], y+1, a[1])
                glEnd()

    glEndList()

    # genereate text
    sizes = [textures['level'][1], textures['0'][1]]
    w = sizes[0][0] + 10 + sizes[1][0]*len(str(level))
    x = (W-w) // 2
    text = [(textures['level'][0], x, sizes[0])]
    x += sizes[0][0]+10
    for char in str(level):
        text.append((textures[char][0], x, sizes[1]))
        x += sizes[1][0]

    door.play()

    player.pos = Vector3(0.2, floors, 0.5)
    w, h = player.size
    time_passed = 0
    running = True
    start = ticks()+2000

    while running:
        if ticks() < start:
            state = 0 # waiting to descend
            alpha = 1 - (start-ticks())/1000
        elif ticks()-start < delay:
            if state == 0:
                lifton.play()
                if first:
                    # if first level, start the music
                    pygame.mixer.music.play(-1)
            state = 1 # descending
            alpha = min(start+delay-ticks(), 1000)/1000
        else:
            if state == 1:
                liftoff.play()
            state = 2 # waiting to open the door
            alpha = 0

        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                pygame.quit()
                quit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 3 and state == 2:
                running = False

        player.update(events, time_passed, False)

        # the player must stay in this cell
        player.pos.x = min(max(player.pos.x, w/2), 1 - w/2)
        player.pos.z = min(max(player.pos.z, w/2), 1 - w/2)
        if state == 0:
            player.cam.y = floors-1+h
        elif state == 1:
            player.cam.y = (delay-ticks()+start) * (floors-1) / delay + h
        else:
            player.cam.y = h
        lights = [player.cam]

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        glPushMatrix()
        init3d()

        # draw the lift
        glCallList(lift)
        for y, normy, tex in [(player.cam.y-h+1, -1, 'liftceil'), (player.cam.y-h, 1, 'liftfloor')]:
            glBindTexture(GL_TEXTURE_2D, textures[tex])
            glBegin(GL_QUADS)
            glNormal3f(0, normy, 0)
            for x, z in [(0, 0), (1, 0), (1, 1), (0, 1)]:
                glTexCoord2f(x, z)
                glVertex(x, y, z)
            glEnd()

        glPopMatrix()
        glPushMatrix()
        init2d()
        render2d()

        y = H/2 - 100
        glColor4f(1, 1, 1, alpha) # fade in/out
        for tex, x, size in text:
            glBindTexture(GL_TEXTURE_2D, tex)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 1)
            glVertex2f(x, y)
            glTexCoord2f(1, 1)
            glVertex2f(x+size[0], y)
            glTexCoord2f(1, 0)
            glVertex2f(x+size[0], y + size[1])
            glTexCoord2f(0, 0)
            glVertex2f(x, y + size[1])
            glEnd()
        glColor(base_color)

        glPopMatrix()

        time_passed = clock.tick(FPS) / 1000
        pygame.display.flip()

    # prepare for the game
    player.pos = Vector3(player.pos.x, 0, player.pos.z+1)
    lights = lights_old
    door.play()

def render3d():
    glCallList(lab_display) # draw the labyrinth

    for entity in entities:
        entity.render()
    for particle in particles:
        particle.render()

def render2d():
    # render HUD
    glBindTexture(GL_TEXTURE_2D, hud)
    glBegin(GL_QUADS)

    glTexCoord2f(0, 1)
    glVertex2f(0, 0)
    glTexCoord2f(1, 1)
    glVertex2f(W, 0)
    glTexCoord2f(1, 0)
    glVertex2f(W, H)
    glTexCoord2f(0, 0)
    glVertex2f(0, H)

    glEnd()

    # render HP bar
    hp = 500*player.hp/player.max_hp
    glBindTexture(GL_TEXTURE_2D, textures['white'])
    glBegin(GL_QUADS)

    glColor(0.3, 0.3, 0.3)
    glTexCoord2f(0, 1)
    glVertex2f(15, 7)
    glTexCoord2f(1, 1)
    glVertex2f(525, 7)
    glTexCoord2f(1, 0)
    glVertex2f(515, 33)
    glTexCoord2f(0, 0)
    glVertex2f(5, 33)

    glColor(1, 0, 0.2)
    glTexCoord2f(0, 1)
    glVertex2f(18, 10)
    glTexCoord2f(1, 1)
    glVertex2f(18+hp, 10)
    glTexCoord2f(1, 0)
    glVertex2f(10+hp, 30)
    glTexCoord2f(0, 0)
    glVertex2f(10, 30)

    glEnd()

    glColor(base_color)

fullscreen = False

load_options()
FOV, render_distance = options['fov'], options['render_distance']

pygame.init()
if fullscreen:
    info = pygame.display.Info()
    W, H = info.current_w, info.current_h
    screen = pygame.display.set_mode((W, H), HWSURFACE|OPENGL|DOUBLEBUF|FULLSCREEN)
else:
    W, H = 900, 500
    screen = pygame.display.set_mode((W, H), HWSURFACE|OPENGL|DOUBLEBUF)
pygame.display.set_caption('Labyrinth')
pygame.event.set_grab(1) # lock all events to this window
pygame.mouse.set_visible(0)
clock = pygame.time.Clock()
ticks = pygame.time.get_ticks

# music
pygame.mixer.music.load('files/sfx/music.mp3')
pygame.mixer.music.set_volume(0.5)
lifton, liftoff, door, bullet = [pygame.mixer.Sound('files/sfx/%s.wav' %name) for name in ['lifton', 'liftoff', 'door', 'bullet']]

time_passed = 0
FPS = 120
level = 0
lab_display = None
base_color = (1, 1, 1)
initOpenGl()

walls_names = ['bricks', 'slimybricks', 'ironplates', 'concrete']
monsters_names = [('SoldierGun', 'POSS'), ('SoldierShotgun', 'SPOS')]
init_tex() # generate all textures
hud_surf = pygame.Surface((W, H), SRCALPHA)
crosshair = pygame.image.load('files/textures/crosshair.png')
w, h = crosshair.get_size()
hud_surf.blit(crosshair, ((W-w) // 2, (H-h) // 2))
update_hud(True)

send_tex(textures)

particles = []
player = Player()
entities = [player]

new_level()
send_vars(W, H, ticks, player, particles, bullet, options)
lift(True)

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            pygame.quit()
            exit()

    for entity in entities:
        if entity == player:
            player.update(events, time_passed)
        elif entity.pos.distance_to(player.pos) <= 8: # simulation distance
            entity.update(time_passed)
    for particle in particles:
        particle.update(time_passed)

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    # render 3d elements
    glPushMatrix()
    init3d()
    render3d()
    glPopMatrix()

    # render 2d elements
    glPushMatrix()
    init2d()
    render2d()
    glPopMatrix()

    if player.level_end:
        player.level_end = False
        new_level()
        lift()

    time_passed = clock.tick(FPS) / 1000
    pygame.display.flip()
