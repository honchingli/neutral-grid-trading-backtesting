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
    if spec.anchor_mode == "FIXED":
        return to_tick(spec.fixed_anchor, spec.tick_size)
    
'''
compute grid level price p_k in ticks: p_k = anchor + k*step

return/output
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

这边是处理单个segment, 并且只有一个方向

Enumerate(ordered) grid level indices 'k' that are crossed/triggered
by this monotonic segment

这边的k, 指的是哪些被触发的价格线 (kth)
eg.
anchor是 $3000
触发, $2800, $3000, $3200, $3400
output: [0, 1, 2] (每段segment的起点不算)
这边每一个数字就是一个k

这边其实应该正好处理了我以下的问题 - 
如果是线反转，anchor是3000，上升段触发3200，3400，下落触发3400，
3200，然后open = close，这样岂不是赚不到还给手续费，怎么解

因为不包括起点，
所以最后停的那条线(触发order的线)不会被重复触发(不会同一条线平仓)



eg. close(3200) > open (2800) (green candlestick)
下降段 [2800, 2600]
上升段 [2600, 2800, 3000, 3200, 3400]
下降段 [3400, 3200]

实际上被触发的
下降段 [2600]
上升段 [2800, 3000, 3200, 3400]
下降段 [3200]

3600--------------------------
3400--------------------------
3200--------------------------
3000--------------------------
2800--------------------------
2600--------------------------
2400--------------------------

'''
def enumrate_crossed_levels(seg:Segment, anchor_tick: int, spec: GridSpec)-> List[int]:
    x = seg.start_tick
    y = seg.end_tick

    step_tick = to_tick(spec.step, spec.tick_size)
    if step_tick<=0:
        raise ValueError("step must be > 0")
    
    k_min = spec.level_min_k
    k_max = spec.level_max_k

    # upward segment: p_k in (x, y] (不包括起点x)
    if y>x:
        # floor ((x-A)/s) + 1 to floor((y-A)/s)
        k_start = floor_div(x-anchor_tick, step_tick) + 1
        k_end = floor_div(y-anchor_tick, step_tick)
        
        # clamp to the risk bounds (not necessary for now)

        if k_start>k_end:
            return []
        return list(range(k_start, k_end+1))
    
    # downward segment: p_k in [y, x) (不包括起点x)
    if y < x:
        # ceil((x-A)/s)-1 down tp ceil((y-A)/s)
        k_start = ceil_div(x - anchor_tick, step_tick) - 1
        k_end = ceil_div(y-anchor_tick, step_tick)

        # clamp to the risk bounds (not necessary for now)

        if k_start<k_end:
            return []
        return list(range(k_start, k_end - 1, -1))

    # Flat segment
    return []
