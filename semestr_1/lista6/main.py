import Engine as physics
import sys
import numpy as np
import pygame
import time
import threading    
import random 



def main():
    position= [400,200]
    black=[0,0,0]

    world_physics = physics.PhysicSimulation()
    obj = []
    for x in range(0, 100):
        pos = np.array([random.randint(100,700), random.randint(100, 300)])
        v = np.array([random.randint(-5, 5), random.randint(-5,5)])
        mass = random.randint(5,10)
        circle = physics.Sphere(pos, v, np.array([0,0]), mass, mass)
        obj.append(circle)
    
    for o in obj:
        world_physics.add_object(o)

    pygame.init()
    screen = pygame.display.set_mode((800, 400))
    clock = pygame.time.Clock()
    dt = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    pygame.quit()

        world_physics.step(dt/100)
        world_physics.resolve_collision(dt/100)
        screen.fill(black)
        for o in obj:
            pos = o.coordinates
            pygame.draw.circle(screen,[255,255,255],pos,o.mass,100)           

        pygame.display.flip()
        dt = clock.tick(60)

 

if __name__ == "__main__":
    main()