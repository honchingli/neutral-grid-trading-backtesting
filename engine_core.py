from __future__ import annotations

from typing import Optional

from grid_types import Action, GridSpec, GridState, PositionState


"""
Default initialization rule for a grid level k when
it is first seen (initialization only)
之后Kth线上的Action，是在价格碰到的时候 翻转的

Input:
k: int (grid level index)

Output:
Action

Rule
k>0 -> SELL
k <= 0 -> BUY
之后可能改成 k==0的话，无Action

"""
def default_action_for_level(k:int) -> Action:
    return Action.SELL if k>0 else Action.BUY


"""
Read current state-machine action for level k
If level k has never been seen, initialize it using default_action_for_level(k).

And put the init Action back to grid.next_action[k] if missing

Inputs:
    grid: GridState (mutable, stores next_action map)
    k: int

Output:
    action: Action (BUY or SELL)

Side effect:
    May add grid.next_action[k] if missing.
"""
def get_or_init_action(grid:GridState, k:int)->Action:
    if k in grid.next_action:
        return grid.next_action[k]
    action = default_action_for_level(k)
    grid.next_action[k] = action
    return action



"""
价格碰到Kth线的时候，翻转Action
Kth线上的Action，是在价格碰到的时候 翻转的


当然实际上会更复杂，因为我们只是根据segment去翻转
而segment不包括起点
"""
def flip_action(action: Action) -> Action:
    """
    Flip an action (state-machine transition).

    Input:
      action: Action

    Output:
      Action
        BUY  -> SELL
        SELL -> BUY
    """
    return Action.SELL if action == Action.BUY else Action.BUY

"""
Apply 1 fill/trade to PositionState

一个大仓位
(加仓)同方向开单，Net position increase, Avg Entry re-calculate
- 成本被摊薄，或拉高，加权平均
(减仓)反方向开单 (量<持仓), Net position decrease, Avg Entry stays the same.
- 仅结算卖出部分的盈亏，剩余部分原始成本不变
(全平)反方向开单(量=持仓), Net position归零, Avg Entry N/A
- 仓位关闭，不再有均价(Avg Entry)
(反手)反方向开单(量>持仓), Net position方向反转, Avg Entry重置
- 变为新方向的开仓价


Inputs:
pos: PositionState(mutable)
    - pos.P: float (net position;  >0 long, <0 short)
    - pos.entry_tick: Optional[int] (avg entry price in ticks, None if flat/0)
    - pos.R: float (realized PnL cashflow)
    - pos.fees: float
action: Action (Buy or Sell)
qty: float (contracts)
price_tick: int (fill price in ticks)
spec: GridSpec (uses tick_size)
fee: float (fee in quote currency)

Output:
realized_delta: float
- Realized PnL from this THIS fill/trade excluding fee
- (Fee is still applied tp pos.R as a cash outflow)

Side effects:
updates pos.P, pos.entry_price, pos.R, pos.fees

Rules :
1) Convert action to signed delta position
BUY => deltaP = +qty
SELL => deltaP = -qty


    

"""