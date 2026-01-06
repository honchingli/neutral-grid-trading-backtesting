from __future__ import annotations
from typing import List

from grid_types import Bar, Segment, SegmentType, GridSpec
from ticks import to_tick


'''

Build a deterministic, monotonic intrabar path as a 
list of Segments
这是给一根K线 (aka 一根bar) 提取Segments的

Purpose:
force a deterministic path on OHLC bar


Inputs:
    bar: Bar
    - open/high/low/close (float)
    - prev_close (Optional[float]) used only if use_gap=True

    spec: GridSpec
    - tick_size is used to convert float prices into integer ticks

    use_gap: bool
    - True: optionally prepend a GAP segment prev_close -> open (if prev_close exists and differs from open)
    - False: ignore prev_close, only intrabar segments

Output:
    List[Segment]
    Each Segment is monotonic from start_tick -> end_tick.
    这边的Segment暂时用的还是tick price, 并不是第几条kth 线

Path rule (your chosen model):
    If close > open  (bullish):
    O -> L -> H -> C
    If close < open  (bearish):
    O -> H -> L -> C
    If close == open:
    deterministic tie-breaker (here: O -> H -> L -> C)

Example output (use_gap=True):
    [ GAP(prev_close->open), INTRABAR(...), INTRABAR(...), INTRABAR(...) ]

'''
def build_path_segments(bar: Bar, spec: GridSpec, use_gap: bool) -> List[Segment]:
    ts = spec.tick_size
    segments: List[Segment] = []

    if use_gap and bar.prev_close is not None and bar.prev_close != bar.open:
        segments.append(
            Segment(
                start_tick = to_tick(bar.prev_close, ts),
                end_tick = to_tick(bar.open, ts),
                seg_type = SegmentType.GAP
            )
        )
    
    # 2) Intrabar segments: based on close vs open
    O = to_tick(bar.open, ts)
    H = to_tick(bar.high, ts)
    L = to_tick(bar.low, ts)
    C = to_tick(bar.close, ts)

    if bar.close >= bar.open:
        # bullish: O -> L -> H -> C
        segments.extend([
            Segment(O, L, SegmentType.INTRABAR),
            Segment(L, H, SegmentType.INTRABAR),
            Segment(H, C, SegmentType.INTRABAR),
        ])
    else:
        # bearish: O -> H -> L -> C
        segments.extend([
            Segment(O, H, SegmentType.INTRABAR),
            Segment(H, L, SegmentType.INTRABAR),
            Segment(L, C, SegmentType.INTRABAR),
        ])
    
    return segments




