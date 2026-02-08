from __future__ import annotations

from typing import Optional

from grid_types import Action, GridSpec, GridState, PositionState


"""
Default initialization rule for a grid level k when
it is first seen

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

Inputs:
pos: PositionState(mutable)
    - pos.P: float (net position,  >0 long, <0 short)
    - pos.entry_tick: Optional[int] (avg entry price in ticks, None if flat/0)
    - pos.R: float (realized PnL cashflow)

"""