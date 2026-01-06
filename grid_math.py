from __future__ import annotations

from typing import List

from grid_types import Bar, GridSpec, Segment
from ticks import to_tick, floor_div, ceil_div


'''
Resolve the grid anchor A (in ticks) for this bar.

Inputs:
    spec.anchor_mode: "OPEN" | "PREV_CLOSE" | "FIXED"
    spec.fixed_anchor: required if anchor_mode == "FIXED"
    bar.open / bar.prev_close as needed
    spec.tick_size

Output:
    anchor_tick: int
    The anchor price converted to integer ticks.

Examples:
    - anchor_mode="OPEN"      -> to_tick(bar.open, tick_size)
    - anchor_mode="PREV_CLOSE"-> to_tick(bar.prev_close, tick_size)
    - anchor_mode="FIXED"     -> to_tick(spec.fixed_anchor, tick_size)    

'''
def resolve_anchor_tick(spec:GridSpec, bar:Bar):
    if spec.anchor_mode == "OPEN":
        return to_tick(bar.open, spec.tick_size)
    if spec.anchor_mode == "PREV_CLOSE":
        return to_tick(bar.prev_close, spec.tick_size)
    
'''
compute grid level price p_k in ticks: p_k = anchor + k*step

kth 线 上的价格 in ticks 是多少

Example:
    anchor_tick=6000 (3000), step_tick=400 (step=200, tick=0.5), k=-1
    -> price_tick = 6000 - 400 = 5600 (2800)
'''
def grid_price_tick(anchor_tick:int, step_tick: int, k:int):
    if step_tick <=0:
        raise ValueError("step_tick must be > 0")
    return anchor_tick + k*step_tick



'''

这边是处理单个segment

Enumerate(ordered) grid level indices 'k' that are crossed/triggered
by this monotonic segment

这边的k, 指的是哪些被触发的价格线 (kth)
eg.
触发, 2800, 3000, 3200, 3400
output: [-1, 0, 1, 2]

'''