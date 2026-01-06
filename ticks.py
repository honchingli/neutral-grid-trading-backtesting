from __future__ import annotations
from typing import Final



'''
convert a real price(float) into an integer tick index

input:
price: float
tick_size: float (must be > 0)

output
tick: int (rounded to nearest tick)

eg.
tick_size=0.5, price=3050.0 -> 3050/0.5 = 6100 -> 6100
'''
def to_tick(price: float, tick_size: float) -> int:
    if tick_size<=0:
        raise ValueError("tick_size must >0")
    return int(round(price/tick_size))

"""
Convert an integer tick index back into a real price (float).

Input:
    tick: int
    tick_size: float

Output:
    price: float

Example:
    tick=6100, tick_size=0.5 -> 3050.0
"""
def to_price(tick: int, tick_size: float) -> float:
    if tick_size<=0:
        raise ValueError("tick_size must be > 0")
    return tick*tick_size


'''
eg.
-5 // 2 = -3
5 // 2 = 2
'''
def floor_div(a: int, b:int)->int:
    if b<=0:
        raise ValueError("b must be > 0")
    return a // b

'''
ceil(a/b) = -floor((-a)/b)
implemented as: -((-a) // b)

Examples:
    ceil_div(5, 2)   -> 3
    ceil_div(-5, 2)  -> -2
    ceil_div(0, 2)   -> 0
'''
def ceil_div(a: int, b: int) -> int:
    if b<=0:
        raise ValueError("b must be > 0")
    return -((-a)//b)




