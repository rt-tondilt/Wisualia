from typing import Tuple, Optional, List
from enum import Enum, IntEnum
from math import pi

from wisualia import core
from wisualia.patterns import Pattern, RGBA,  RED, GREEN, BLUE

def begin_shape(): #type: ignore
    cr = core.context
    if core.current_path_is_used:
        cr.new_path()
        core.current_path_is_used=False
    cr.new_sub_path()
    return cr

def rect(point1:Tuple[float, float],
         point2:Tuple[float, float]) -> None:
    '''
    Args:
        point1:
        point2:
        fill:
        stroke:
    Returns:
        Nothing

    Draw a rectangle to the current image with edges parallel to the x- and
    y-axis. The edges may not be parallel if the function is called inside a
    transformation.
    '''
    cr = begin_shape()
    cr.rectangle(*point1, point2[0]-point1[0], point2[1]-point1[1])

def circle(centre:Tuple[float, float]=(0, 0),
           radius:float=1) -> None:
    '''
    Args:
        centre:
        radius:
        fill:
        stroke:
    Returns:
        Nothing

    Draw a circle to the current image.
    '''
    cr = begin_shape()
    cr.arc(centre[0], centre[1], radius , 0, 2 * pi)

def polygon(*points: Tuple[float, float]) -> None:
    '''
    Args:
        points:
        fill:
        stroke:
    Returns:
        Nothing

    Draw a polygon to the current image.
    '''
    cr = begin_shape()
    cr.move_to(*points[0])
    for i in range(1, len(points)):
        cr.line_to(*points[i])
    cr.close_path()
