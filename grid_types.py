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





