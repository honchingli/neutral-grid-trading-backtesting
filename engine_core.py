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
这个pos 就是 最主要记录一切的states
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

2) Realized PnL happens only when reducing an existing position(net position=pos.P)
If pos.P > 0 and deltaP < 0: reducing long
- realized += close_qty * (fill_price - entry_price)
If pos.P<0 and deltaP > 0: reducing short
- realizsed += close_qty * (entry_price - fill_price)

3) Average entry  updates:
- Opening from flat: entry = fill_price
- Adding to same-side: weighted average
- Reducing but staying same-side: entry unchanged
- Crossing through zero: new entry = fill_price(for the new oppsite position)

4) Fee is subtracted from pos.R(cash outflow), and accumulated in pos.fees

"""

def apply_fill_to_position(pos: PositionState, action: Action, 
                           qty:float, price_tick: int, 
                           spec: GridSpec, fee: float) -> float:
    if qty <= 0:
            raise ValueError("qty must be > 0")

    # Signed position change
    deltaP = qty if action == Action.BUY else -qty

    realized = 0.0

    # Helper: convert a tick difference into money PnL
    # q = qty
    def pnl_from_tick_diff(q: float, tick_diff: int)-> float:
        return q*tick_diff*spec.tick_size

    # Realize PnL when reducing existing position(net position)
    if pos.P > 0 and deltaP < 0:
        # reducing long
        close_qty = min(abs(deltaP), abs(pos.P))
        if pos.entry_tick is None:
            raise ValueError("pos.entry_tick is None while pos.P > 0")
        realized += pnl_from_tick_diff(close_qty, price_tick-pos.entry_tick)
    
    if pos.P < 0 and deltaP > 0:
        # reducing a short
        close_qty = min(abs(deltaP), abs(pos.P))
        if pos.entry_tick is None:
            raise ValueError("pos.entry_tick is None while pos.P > 0")
        realized += pnl_from_tick_diff(close_qty, pos.entry_tick - price_tick)

    # update net position
    P_new  = pos.P + deltaP

    # Update average entry
    if P_new ==0:
        pos.P = 0.0
        pos.entry_tick = None
    else:
        cross_zero = (pos.P > 0 and P_new<0) or (pos.P<0 and P_new > 0)

        if pos.P==0:
            # opening from flat
            pos.entry_tick = price_tick
        elif cross_zero:
            # crossed through zero -> new opposite position opened at this price
            pos.entry_tick = price_tick
        else:
            # same-side after trade
            if abs(P_new) > abs(pos.P):
                # increased exposure -> weighted  average entry in ticks
                if pos.entry_tick is None:
                    raise ValueError("pos.entry_tick is None while pos.P != 0")
                new_entry = (abs(pos.P)*pos.entry_tick + abs(deltaP) * price_tick) / abs(P_new)
                pos.entry_tick = int(round(new_entry))
            # else reduced exposure but same side -> keep entry_tick unchanged
        pos.P = P_new
    
    # Apply realized and fee as cashflow
    pos.R += realized
    pos.R -= fee
    pos.fees += fee

    return realized






