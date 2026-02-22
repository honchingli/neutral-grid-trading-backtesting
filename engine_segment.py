from __future__ import annotations
from typing import List

from grid_types import Fill, GridSpec, GridState, PositionState, Segment
from ticks import to_tick, to_price
from grid_math import enumrate_crossed_levels, grid_price_tick
from engine_core import get_or_init_action, flip_action, apply_fill_to_position


"""
Step6 处理单个Segment (枚举level->成交->更新仓位->翻转state machine)
Process one monotonic Segment
- Enumerate crossed grid levels k (ordered)
- For each k:
    - determine level price
    - read/init current action from GridState
    - compute fee
    - apply fill to PositionState
    - flip the action at this current level (state-machine transition)

Inputs
seg: Segment
    - seg.start_tick, seg.end_tick (monotonic)
bar_index: int
segment_index: int
anchor_tick: int
    The anchor A in ticks for this bar (from resolve_anchor_tick)
spec: GridSpec
    uses step, tick_size, qty_per_level, fee_rate, k bounds
grid: GridState(mutable)
    grid.next_action[k] may be created/updated
pos: PositionState(mutable)
    pos.P/pos.entry_tick/pos.R/pos.fees updated per fill

Output:
fills: List[Fill]
One Fill per triggered level k
If the segment crosses no levels, returns []

Side effects:
- updates grid.next_action[k] (flip at triggered levels k)
- updates pos (position + pnl + fees)
"""






