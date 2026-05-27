# team_leader_roll_no.py
"""
QUANT-KILLER BOT
Strategy: Combinatorial Enumeration & Expected Value Maximization
"""

import json
import sys
import itertools
from typing import List, Tuple

# ---------------------------------------------------------
# CORE LOGIC: HAND EVALUATION ENGINE
# ---------------------------------------------------------

# Rank mapping: 2=2 ... T=10, J=11, Q=12, K=13, A=14
RANKS = "23456789TJQKA"
RANK_MAP = {r: i + 2 for i, r in enumerate(RANKS)}

def parse_card(c: str) -> Tuple[int, str]:
    """Converts '7H' to (7, 'H') or 'AS' to (14, 'S')"""
    return RANK_MAP[c[0]], c[1]

def get_hand_strength(hole: List[str], table: str) -> Tuple:
    """
    Returns a comparable tuple representing hand strength exactly according to PDF rules.
    Format: (Score_Category, Tie_Breaker_1, Tie_Breaker_2, Tie_Breaker_3)
    
    Scores (Higher is better):
    5: Straight Flush [cite: 38]
    4: Trips [cite: 41]
    3: Straight [cite: 43]
    2: Flush [cite: 49]
    1: Pair [cite: 54]
    0: High Card [cite: 59]
    """
    # 1. Parse all 3 cards
    cards = hole + [table]
    parsed = [parse_card(c) for c in cards]
    values = sorted([p[0] for p in parsed], reverse=True) # Descending for tie-breaks
    suits = [p[1] for p in parsed]
    
    unique_vals = set(values)
    is_flush = (len(set(suits)) == 1)
    
    # 2. Straight Detection
    # Standard sequence (e.g., 6,5,4)
    is_straight = (values[0] - values[1] == 1) and (values[1] - values[2] == 1)
    
    # Special Ace Case: A-2-3 (Low Straight) [cite: 40]
    # In our values, A=14, 2=2, 3=3. Set is {14, 3, 2}
    is_wheel = (unique_vals == {14, 3, 2})
    
    if is_wheel:
        is_straight = True
        # For A-2-3, the high card is 3[cite: 40]. 
        # We must re-order values for tie-breaking: (3, 2, 14 ignored as low)
        values = [3, 2, 14] 

    # 3. Categorize
    
    # STRAIGHT FLUSH (5)
    if is_straight and is_flush:
        return (5, values[0], values[1], values[2])
        
    # TRIPS (4)
    # If set length is 1, all 3 are same
    if len(unique_vals) == 1:
        return (4, values[0], 0, 0)
        
    # STRAIGHT (3)
    if is_straight:
        return (3, values[0], values[1], values[2])
        
    # FLUSH (2)
    if is_flush:
        return (2, values[0], values[1], values[2])
        
    # PAIR (1)
    if len(unique_vals) == 2:
        # Identify the pair and the kicker
        # values is sorted desc, e.g. [10, 10, 8] or [10, 8, 8]
        if values[0] == values[1]:
            pair_rank = values[0]
            kicker = values[2]
        else:
            pair_rank = values[1] # [10, 8, 8] -> pair is 8
            kicker = values[0]
        return (1, pair_rank, kicker, 0)
        
    # HIGH CARD (0)
    return (0, values[0], values[1], values[2])

# ---------------------------------------------------------
# QUANTITATIVE ENGINE: EXACT PROBABILITY
# ---------------------------------------------------------

def get_exact_win_rate(my_hole: List[str], table: str) -> float:
    """
    Iterates through all 1,176 possible opponent hands (C(49,2)) to find
    the exact win rate.
    """
    # 1. Build the remaining deck
    full_deck = [r+s for r in RANKS for s in "CDHS"]
    used_cards = set(my_hole + [table])
    deck = [c for c in full_deck if c not in used_cards]
    
    # 2. Get my strength
    my_strength = get_hand_strength(my_hole, table)
    
    wins = 0
    ties = 0
    total = 0
    
    # 3. Brute force every possible opponent hand (FAST in Python)
    for opp_hole in itertools.combinations(deck, 2):
        total += 1
        opp_strength = get_hand_strength(list(opp_hole), table)
        
        if my_strength > opp_strength:
            wins += 1
        elif my_strength == opp_strength:
            ties += 1
            
    # Return equity (Win + half of tie)
    return (wins + 0.5 * ties) / total

# ---------------------------------------------------------
# DECISION MATRIX
# ---------------------------------------------------------

def decide_action(state: dict) -> str:
    """
    Uses Threshold-Based Logic + Opponent Exploitation
    """
    try:
        hole = state["your_hole"]
        table = state["table_card"]
        stats = state.get("opponent_stats", {})
        
        # 1. Calculate Exact Equity
        equity = get_exact_win_rate(hole, table)
        
        # 2. Analyze Opponent (Exploitation)
        total_actions = stats.get("fold", 0) + stats.get("call", 0) + stats.get("raise", 0)
        
        # Default assumptions if limited data
        if total_actions < 5:
            fold_rate = 0.2
            raise_rate = 0.2
        else:
            fold_rate = stats.get("fold", 0) / total_actions
            raise_rate = stats.get("raise", 0) / total_actions

        # 3. Strategy Tiers
        
        # TIER A: THE NUT RANGE (Raise for Value)
        # If we have > 65% equity, we want to bloat the pot.
        # Even if they fold, we get +2 or +3. If they call, we likely win +3.
        if equity >= 0.65:
            return "RAISE"
            
        # TIER B: THE TRASH RANGE (Fold to Save)
        # If equity is < 30%, we are losing long term. 
        # Exception: If opponent folds > 60% of time, we might bluff, 
        # but let's play solid math first.
        if equity <= 0.35:
            # Bluff opportunity: If they fold > 50% of the time, 
            # Raising is profitable even with 0% equity!
            if fold_rate > 0.50: 
                return "RAISE"
            return "FOLD"
            
        # TIER C: THE MARGINAL RANGE (0.35 to 0.65)
        # This is where most bots fail. They always Call.
        # We will use opponent stats to decide.
        
        # If opponent is passive (Fold rate > 30%), we bully them.
        if equity > 0.45 and fold_rate > 0.30:
            return "RAISE"
            
        # If opponent is aggressive (Raise rate > 40%), we play safe.
        if raise_rate > 0.40:
            # Only call if we are on the upper end of marginal
            if equity > 0.50:
                return "CALL"
            else:
                return "FOLD"
                
        # Default fallback for middle hands
        return "CALL"

    except Exception:
        # Failsafe: If anything crashes, Call is the safest default
        return "CALL"

# ---------------------------------------------------------
# IO HANDLER
# ---------------------------------------------------------
def main():
    raw = sys.stdin.read().strip()
    if not raw: return
    try:
        state = json.loads(raw)
        action = decide_action(state)
        sys.stdout.write(json.dumps({"action": action}))
    except:
        sys.stdout.write(json.dumps({"action": "CALL"}))

if __name__ == "__main__":
    main()