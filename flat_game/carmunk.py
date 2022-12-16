import random
import math
import numpy as np

import pygame
from pygame.color import THECOLORS

import pymunk
from pymunk.vec2d import Vec2d
from pymunk.pygame_util import draw

# PyGame init
width = 1366
height = 768
pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

screen.set_alpha(None)

show_sensors = True
draw_screen = True


class GameState:
    def __init__(self):
        
        self.crashed = False
        self.space = pymunk.Space()
        self.space.gravity = pymunk.Vec2d(0., 0.)

        self.plot=1

        # Create the car.
        self.create_car(200, 200, 0.5)

        # Record steps.
        self.num_steps = 0

        # Create walls.
        static = [
            pymunk.Segment(
                self.space.static_body,
                (0, 1), (0, height), 1),
            pymunk.Segment(
                self.space.static_body,
                (1, height), (width, height), 1),
            pymunk.Segment(
                self.space.static_body,
                (width-1, height), (width-1, 1), 1),
            pymunk.Segment(
                self.space.static_body,
                (1, 1), (width, 1), 1)
        ]
        for s in static:
            s.friction = 1.
            s.group = 1
            s.collision_type = 1
            s.color = THECOLORS['red']
        self.space.add(static)

        self.obstacles = []
        self.obstacles.append(self.create_obstacle(500, 350, 35))

    def create_obstacle(self, x, y, r):
        c_body = pymunk.Body(pymunk.inf, pymunk.inf)
        c_shape = pymunk.Circle(c_body, r)
        c_shape.elasticity = 1.0
        c_body.position = x, y
        c_shape.color = THECOLORS["blue"]
        self.space.add(c_body, c_shape)
        return c_body

    def create_car(self, x, y, r):
        inertia = pymunk.moment_for_circle(1, 0, 14, (0, 0))
        self.car_body = pymunk.Body(1, inertia)
        self.car_body.position = x, y
        self.car_shape = pymunk.Circle(self.car_body, 25)
        self.car_shape.color = THECOLORS["green"]
        self.car_shape.elasticity = 1.0
        self.car_body.angle = r
        driving_direction = Vec2d(1, 0).rotated(self.car_body.angle)
        self.car_body.apply_impulse(driving_direction)
        self.space.add(self.car_body, self.car_shape)

    def frame_step(self, action):
        if action == 0:  # Turn left.
            self.car_body.angle -= .15
        elif action == 1:  # Turn right.

            self.car_body.angle += .15
        # Move obstacles.
        #if self.num_steps % 100 == 0:
            #self.move_obstacles()

        driving_direction = Vec2d(1, 0).rotated(self.car_body.angle)
        self.car_body.velocity = 100 * driving_direction

        #print("dd")
        #print(driving_direction);

        #print((self.obstacles[0]._get_position()))

        # Update the screen and stuff.
        screen.fill(THECOLORS["black"])
        draw(screen, self.space)
        self.space.step(1./10)
        if draw_screen:
            pygame.display.flip()
        clock.tick()

        x, y = self.car_body.position

        correct_angle = self.obstacles[0]._get_position()-Vec2d(x,y)
        correction_angle = math.degrees(correct_angle.get_angle_between(driving_direction))
        #print(string(correction_angle)+)
        correction_angle = (abs(correction_angle))



                
        #readings = self.get_sonar_readings(x, y, self.car_body.angle)
        normalized_readings = []
        dis = self.obstacles[0]._get_position().get_distance(self.car_body.position)
        
        normalized_readings.append(dis/20)
        #angle = Vec2d(1, 0).rotated(0.5).get_angle_between(Vec2d(1, 0).rotated(self.car_body.angle))
        normalized_readings.append((correction_angle)) 
        state = np.array([normalized_readings])

        # Set the reward.
        # Car crashed when any reading == 1
            # Higher readings are better, so return the sum.
        # obs_coord = self.obstacles[0]._get_position().int_tuple
        # if x<obs_coord[0]:
        #     reward = -5 + int(-1*dis / 20)-int(abs(angle))
        # else:
        #     reward = -5 + int(-1*dis / 20)+int(abs(angle))
        
        if self.car_is_crashed(x,y):
            self.crashed = True
            reward = -200
            self.recover_from_crash(driving_direction)
        elif int(dis)<100:
            reward = 200
            self.crashed = True
            #self.obstacles[0]._set_position((650,600))
            rand_y = random.randrange(150,600)
            rand_x = random.randrange(150,1000)
            t = self.obstacles[0]._get_position().int_tuple
            if self.plot==1:
                if t[0]+100<1250:
                    self.obstacles[0]._set_position((t[0]+100,t[1]))
                elif t[1]+100<600:
                    self.obstacles[0]._set_position((t[0],t[1]+100))
                else:
                 self.plot=-1

            if self.plot==-1:
                if t[0]-100>200:
                    self.obstacles[0]._set_position((t[0]-100,t[1]))
                elif t[1]-100>200:
                    self.obstacles[0]._set_position((t[0],t[1]-100))
                else:
                    self.plot=1

            # elif t[0]-100>150:
            #     self.obstacles[0]._set_position((t[0]-100,t[1]))



            #self.recover_from_crash(driving_direction)
        else:
            if correction_angle>30:
                reward = -1*int(dis/20 )-(int(abs(correction_angle)/2))
                reward = int(reward/10)
            else:
                reward = 20-1*int(dis/20 )-(int(abs(correction_angle)))+30
                reward = int(reward/10)
        
        self.num_steps += 1

        print(state,end=" ")
        print(reward)

        return reward, state

    def car_is_crashed(self, x,y):
        if x<25 or x>width-25:
            return True
        if y<25 or y>height-25:
            return True
        return False



    def recover_from_crash(self, driving_direction):
  	  while self.crashed:
            # Go backwards.
            self.car_body.velocity = -100 * driving_direction
            self.crashed = False
            for i in range(10):
                self.car_body.angle += .2 
		screen.fill(THECOLORS["grey7"])
		draw(screen, self.space)
                self.space.step(1./10)
                if draw_screen:
                    pygame.display.flip()
                clock.tick()

    def get_rotated_point(self, x_1, y_1, x_2, y_2, radians):
        x_change = (x_2 - x_1) * math.cos(radians) + \
            (y_2 - y_1) * math.sin(radians)
        y_change = (y_1 - y_2) * math.cos(radians) - \
            (x_1 - x_2) * math.sin(radians)
        new_x = x_change + x_1
        new_y = height - (y_change + y_1)
        return int(new_x), int(new_y)

    def get_track_or_not(self, reading):
        if reading == THECOLORS['black']:
            return 0
        else:
            return 1

if __name__ == "__main__":
    game_state = GameState()
    while True:
        game_state.frame_step((random.randint(0, 2)))
