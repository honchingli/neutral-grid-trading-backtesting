from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from typing import Dict, List, Optional


'''
Trading action when the level (kth level is triggered)
Enum here is python's Enum type(枚举类型), 定义一组固定有限取值

Action can only be one of the two below:
Action.BUY
Action.SELL

auto() - auto() 是 Enum 的一个工具：让 Python 自动给每个枚举成员分配一个唯一值。
'''
class Action(Enum):
    BUY = auto()
    SELL = auto()


'''
Segment category:
 - GAP: previous close ->to current open (optional)
 - Intrabar: inside the OHLC bar path (meaning its the paths 
 among inside the bar itself, not gap)
'''
class SegmentType(Enum):
    GAP = auto()
    INTRABAR = auto()

'''
frozen=True - meaning the dataclass is immutable
Optional[float] - this variable either float, or None
some bar we don't have prev_close (第一根K线), 那就是None
'''
@dataclass(frozen=True)
class Bar:
    open: float
    high:float
    low:float
    close:float
    prev_close:Optional[float] = None


'''
A monotonic price move within a bar (or a gap)
一个单程的segment, 要不 向上，要不向下

Output usage: 
- used by enumrate_crossed_levels(...) to produce crossed grid leves

Eg.
Segment(start_tick=6100, end_tick=5300, seg_type=SegmentType.INTRABAR)
'''
class Segment:
    start_tick: int
    end_tick: int
    seg_type: SegmentType


'''
Strategy/Grid configuration

fixed_anchor: Optional[float]
Required if anchor_mode == "FIXED".

level_min_k, level_max_k: int
eg.
kth line, 第k th 根线, [-3, -2, -1, 0, 1, 2, 3]
"0" represent $3000的价格线
"1" represent $3200

Risk cap: clamp grid levels to this range.

eg.
GridSpec(step=200.0, qty_per_level=1.0, tick_size=0.5,
anchor_mode="OPEN"or"FIXED")
'''
@dataclass
class GridSpec:
    step: float
    qty_per_level: float
    fee_rate:float = 0.0002
    tick_size: float = 0.5
    anchor_mode: str = "FIXED" # "OPEN" | "PREV_CLOSE" | "FIXED"
    fixed_anchor: Optional[float] = None
    level_min_k: int = -2000
    level_max_k: int = 2000


'''
Grid state machine (persistent across bars).

Fields:
    next_action: Dict[int, Action]
    Key: level index k
    Value: next action to execute when price triggers p_k

Example:
    grid.next_action[-1] = Action.BUY
    grid.next_action[-1] = Action.SELL  # after flip

    经典坑：这个 `{}` 可能被多个实例共享（mutable default 的坑）。

default_factory=dict 保证：每次创建 GridState 都会得到一个全新的空字典 
'''
@dataclass
class GridState:
    next_action: Dict[int, Action] = field(default_factory=dict)


'''
Net position accounting state 算钱的, 算PnL, 还有unrealized_pnl

Fields:
    P: float
    Net position quantity (contracts). Positive = long, negative = short.

    entry_tick: Optional[int]
    Average entry price in ticks; None when P == 0.

    R: float
    Realized PnL (cashflow), fees subtracted here as well.

    fees: float
    Running total of fees.

Example:
    P=2.0, entry_tick=5800 (=> 2900.0 if tick_size=0.5)
'''
@dataclass
class PositionState:
    P: float = 0.0
    entry_tick: Optional[int] = None
    R: float = 0.0
    fees: float = 0.0


'''
One executed trade ("fill") at a grid level.
每个被fill的单 / 每笔交易 都会被记录下来，用于analysis

"at a grid level"? 我们只在grid的kth 线上交易，
也就是只在 Grid's level上交易

Output usage:
    - Emitted by process_segment(...) / run_bar(...)
    - Used for debugging, analytics, trade logs
'''
dataclass(frozen=True)
class Fill:
    bar_index: int
    segment_index: int
    level_k: int
    price: float
    action: Action
    qty: float
    fee: float
    realized_delta: float


