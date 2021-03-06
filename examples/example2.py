import wisualia
from wisualia.do import fill
from wisualia.shapes import circle
from wisualia.modifiers import Rotate, Move
from wisualia.patterns import HSVA
from wisualia.animation import animate, Camera
from math import sin, pi


def loop_function(t):
    for i in range(36):
        with Rotate(i*10):
            with Move(-(i%6)*sin(t), 0):
                circle((5,0),0.5)
                fill(HSVA(i/36+t))
    
animate(loop_function, camera=Camera((20,20), 40))