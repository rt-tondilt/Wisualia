from typing import List, Optional, Tuple
from enum import IntEnum

from cairo import FillRule #type:ignore

from wisualia.core import derive_repr, Modifier
from wisualia.patterns import Pattern,RGBA
from wisualia.geometry import Point
from wisualia import core

class LineJoin(IntEnum):
    '''
    Style of the corner between two joined lines.
    '''
    MITER = 0
    ROUND = 1
    BEVEL = 2

class LineCap(IntEnum):
    '''
    Style of the start and end of a line if it is not joined with another one.
    '''
    BUTT = 0
    ROUND = 1
    SQUARE = 2

@derive_repr
class Dash(object):
    '''
    Args:
        dashes:
        offset:

    Todo:
        Experimentad and undocumented.
    '''
    def __init__(self, dashes:List[float], offset:int=0) -> None:
        self.dashes = dashes
        self.offset = offset

def fill(pattern:Pattern=RGBA(0,0,1,0.4)) -> None:
    cr = core.context
    cr.set_fill_rule(FillRule.EVEN_ODD)
    pattern._use_as_source_on(cr)
    cr.fill_preserve()
    core.current_path_is_used = True

def stroke(
    width:float=0.1,
    pattern:Pattern=RGBA(0,0,0,1),
    join:LineJoin=LineJoin.MITER,
    cap:LineCap=LineCap.BUTT,
    dash:Dash=Dash([],0)
    ) -> None:
    cr = core.context
    cr.set_line_width(width)
    cr.set_line_join(join)
    cr.set_line_cap(cap)
    cr.set_dash(dash.dashes, dash.offset)
    pattern._use_as_source_on(cr)
    cr.stroke_preserve()
    core.current_path_is_used = True

class Clip(Modifier):
    def modify(self, cr): #type:ignore
        cr.set_fill_rule(FillRule.EVEN_ODD)
        cr.clip_preserve()
        core.current_path_is_used = True

def paint(pattern:Pattern, alpha:float=1) -> None:
    '''
    Args:
        pattern:
        alpha:
    Returns:
        Nothing

    Paints a pattern to the current image, using given alpha value.
    '''
    cr = core.context
    pattern._use_as_source_on(cr)
    cr.paint_with_alpha(alpha)

def mask(pattern:Pattern, mask:Pattern) -> None:
    cr=core.context
    pattern._use_as_source_on(cr)
    mask._use_as_mask_on(cr)

def in_fill(x:float, y:float) -> bool:
    cr = core.context
    return cr.in_fill(x,y) #type: ignore
def in_clip(x:float, y:float) -> bool:
    cr = core.context
    return cr.in_clip(x,y) #type: ignore

def fill_extents() -> Tuple[Tuple[float,float], Tuple[float,float]]:
    cr = core.context
    x1,y1,x2,y2 = cr.fill_extents()
    return (x1,y1), (x2,y2)
def clip_extents() -> Tuple[Tuple[float,float], Tuple[float,float]]:
    cr = core.context
    x1,y1,x2,y2 = cr.clip_extents()
    return (x1,y1), (x2,y2)
