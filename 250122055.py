# team_leader_roll_no.py
"""
Simplified PokerBot – Player Template
Strategy: Combinatorial Enumeration & Asymmetric Payoff Exploitation.
"""

import json
import sys
import itertools
from typing import List, Tuple

# -------------------------
# 1. Basic card utilities
# -------------------------

# Ranks from lowest to highest. T = 10, J = Jack, Q = Queen, K = King, A = Ace.
RANKS = "23456789TJQKA"
# Map rank character -> numeric value (2..14)
RANK_VALUE = {r: i + 2 for i, r in enumerate(RANKS)}  # 2..14 (A=14)

def parse_card(card_str: str) -> Tuple[int, str]:
    """
    Convert a string like "AH" or "7D" into (rank_value, suit).
    """
    return RANK_VALUE[card_str[0]], card_str[1]

# --------------------------------------
# 2. Advanced Hand Evaluation (Tuple Based)
# --------------------------------------
"""
We use a more precise evaluation than the template's default category 
function to handle tie-breakers (kickers) correctly during the 
combinatorial simulation.
"""

def get_hand_score_tuple(hole: List[str], table: str) -> Tuple:
    """
    Returns a comparable tuple (category, tb1, tb2, tb3).
    Higher tuple wins.
    
    Categories:
    5: Straight Flush
    4: Trips
    3: Straight
    2: Flush
    1: Pair
    0: High Card
    """
    cards = hole + [table]
    rank_values_raw = [parse_card(c)[0] for c in cards]
    suits = [parse_card(c)[1] for c in cards]
    
    # Sort descending for easy tie-breaker comparison
    r_desc = sorted(rank_values_raw, reverse=True)
    r_set = set(r_desc)
    
    is_flush = (len(set(suits)) == 1)
    
    # Straight logic
    is_straight = False
    straight_high = 0
    
    # Normal straight check (e.g. 6, 5, 4)
    if (r_desc[0] - r_desc[1] == 1) and (r_desc[1] - r_desc[2] == 1):
        is_straight = True
        straight_high = r_desc[0]
    # Wheel straight check (A, 2, 3 -> 14, 3, 2). Treated as low straight (high card 3)
    elif r_set == {14, 2, 3}:
        is_straight = True
        straight_high = 3
        
    counts = {x: rank_values_raw.count(x) for x in r_set}
    
    # 5. Straight Flush
    if is_straight and is_flush:
        return (5, straight_high, 0, 0)
        
    # 4. Trips
    if 3 in counts.values():
        trip_val = [k for k, v in counts.items() if v == 3][0]
        return (4, trip_val, 0, 0)
        
    # 3. Straight
    if is_straight:
        return (3, straight_high, 0, 0)
        
    # 2. Flush
    if is_flush:
        return (2, r_desc[0], r_desc[1], r_desc[2])
        
    # 1. Pair
    if 2 in counts.values():
        pair_val = [k for k, v in counts.items() if v == 2][0]
        # Kicker is the remaining card
        kicker = [k for k in r_set if k != pair_val][0]
        return (1, pair_val, kicker, 0)
        
    # 0. High Card
    return (0, r_desc[0], r_desc[1], r_desc[2])


# -----------------------------------
# 3. Quantitative Engine
# -----------------------------------

def get_exact_win_rate(my_hole: List[str], table: str) -> float:
    """
    Iterates through all 1,176 possible opponent hands (C(49,2)) to find
    the exact win rate.
    """
    # 1. Build the remaining deck
    all_ranks = "23456789TJQKA"
    all_suits = "CDHS"
    full_deck = [r+s for r in all_ranks for s in all_suits]
    
    used_cards = set(my_hole + [table])
    unknown_deck = [c for c in full_deck if c not in used_cards]
    
    # 2. Get my strength
    my_score = get_hand_score_tuple(my_hole, table)
    
    wins = 0
    ties = 0
    total = 0
    
    # 3. Brute force every possible opponent hand (FAST in Python: <0.05s)
    # 49 choose 2 = 1176 iterations.
    for opp_hole in itertools.combinations(unknown_deck, 2):
        total += 1
        opp_score = get_hand_score_tuple(list(opp_hole), table)
        
        if my_score > opp_score:
            wins += 1
        elif my_score == opp_score:
            ties += 1
            
    # Return equity (Win + half of tie)
    return (wins + 0.5 * ties) / total


# -----------------------------------
# 4. Main strategy function
# -----------------------------------

def decide_action(state: dict) -> str:
    """
    Uses Combinatorial Enumeration to calculate exact equity, then applies 
    Threshold-Based Logic to exploit the asymmetric scoring table.
    """
    try:
        # 1) Extract information
        hole = state["your_hole"]
        table = state["table_card"]
        stats = state.get("opponent_stats", {})
        
        # 2) Calculate Exact Equity (0.0 to 1.0)
        # This is the "God Mode" math part.
        equity = get_exact_win_rate(hole, table)
        
        # 3) Analyze Opponent (Exploitation)
        total_actions = stats.get("fold", 0) + stats.get("call", 0) + stats.get("raise", 0)
        
        # Default assumptions (Laplace smoothing / Prior beliefs)
        if total_actions < 5:
            fold_rate = 0.2
            raise_rate = 0.2
        else:
            fold_rate = stats.get("fold", 0) / total_actions
            raise_rate = stats.get("raise", 0) / total_actions

        # 4) Decision Matrix
        
        # --- ZONE 1: MONSTER HANDS (Raise for Value) ---
        # If we win > 65% of the time, we WANT to inflate the pot.
        # Payoff Table: Raise wins +3, Call wins +2. We want +3.
        if equity >= 0.65:
            return "RAISE"

        # --- ZONE 2: TRASH HANDS (Fold to Save) ---
        # If we win < 35% of the time, we are usually losing money (-EV).
        # Standard play is to FOLD (-1) rather than Call (-2 or -3).
        if equity <= 0.35:
            # EXCEPTION: Pure Bluff
            # If the opponent folds > 50% of the time, Raising gives +3 often enough
            # to be profitable even with a 0% win rate.
            if fold_rate > 0.50:
                return "RAISE"
            return "FOLD"

        # --- ZONE 3: MARGINAL HANDS (0.35 to 0.65) ---
        # This is where we outplay other bots.
        
        # Strategy A: Bully the Passive
        # If opponent folds often (>30%) and we have decent equity (>45%),
        # we Raise to steal the +3.
        if equity > 0.45 and fold_rate > 0.30:
            return "RAISE"
            
        # Strategy B: Trap the Aggressive
        # If opponent raises often (>40%), we just Call.
        # We let them risk the -3 while we risk -2.
        if raise_rate > 0.40:
            # Only call if we are on the upper end of marginal
            if equity > 0.50:
                return "CALL"
            else:
                return "FOLD"
        
        # Default fallback for average scenarios
        return "CALL"

    except Exception:
        # Failsafe: ensure we never crash (crashes = disqualification)
        return "CALL"


# -----------------------------
# 5. I/O glue (do not touch)
# -----------------------------

def main():
    """
    DO NOT modify this unless you know what you're doing.
    """
    raw = sys.stdin.read().strip()
    try:
        state = json.loads(raw) if raw else {}
    except Exception:
        state = {}

    action = decide_action(state)

    # Safety check: default to CALL if something invalid is returned
    if action not in {"FOLD", "CALL", "RAISE"}:
        action = "CALL"

    sys.stdout.write(json.dumps({"action": action}))


if __name__ == "__main__":
    main()