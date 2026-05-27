# team_leader_roll_no.py
import json
import sys
import itertools
from typing import List, Tuple

# -------------------------
# 1. Advanced Card Logic
# -------------------------

RANKS = "23456789TJQKA"
RANK_VALUE = {r: i + 2 for i, r in enumerate(RANKS)}

def parse_card(card_str: str) -> Tuple[int, str]:
    return RANK_VALUE[card_str[0]], card_str[1]

def get_hand_score(hole: List[str], table: str) -> Tuple:
    """
    Returns (category, tie_breaker_1, tie_breaker_2, tie_breaker_3).
    Categories: 5:StrFlush, 4:Trips, 3:Str, 2:Flush, 1:Pair, 0:High
    """
    cards = hole + [table]
    rank_values_raw = [parse_card(c)[0] for c in cards]
    suits = [parse_card(c)[1] for c in cards]
    
    # Sort descending
    r_desc = sorted(rank_values_raw, reverse=True)
    r_set = set(r_desc)
    
    is_flush = (len(set(suits)) == 1)
    
    # Straight logic
    is_straight = False
    straight_high = 0
    
    # Normal straight
    if (r_desc[0] - r_desc[1] == 1) and (r_desc[1] - r_desc[2] == 1):
        is_straight = True
        straight_high = r_desc[0]
    # Wheel straight (A, 2, 3) -> 14, 3, 2
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
        kicker = [k for k in r_set if k != pair_val][0]
        return (1, pair_val, kicker, 0)
    # 0. High Card
    return (0, r_desc[0], r_desc[1], r_desc[2])

# -------------------------
# 2. Exact Probability Engine
# -------------------------

def calculate_win_rate(my_hole: List[str], table: str) -> float:
    """
    Returns exact P(Win) + 0.5 * P(Tie) against random opponent hand.
    """
    all_ranks = "23456789TJQKA"
    all_suits = "CDHS"
    full_deck = [r+s for r in all_ranks for s in all_suits]
    
    known_cards = set(my_hole + [table])
    unknown_deck = [c for c in full_deck if c not in known_cards]
    
    my_score = get_hand_score(my_hole, table)
    
    wins = 0
    ties = 0
    total = 0
    
    # 49 choose 2 = 1176 iterations (Very fast)
    for opp_hole in itertools.combinations(unknown_deck, 2):
        total += 1
        opp_score = get_hand_score(list(opp_hole), table)
        
        if my_score > opp_score:
            wins += 1
        elif my_score == opp_score:
            ties += 1
            
    return (wins + 0.5 * ties) / total

# -------------------------
# 3. Aggressive Strategy
# -------------------------

def decide_action(state: dict) -> str:
    hole = state["your_hole"]
    table = state["table_card"]
    opp_stats = state.get("opponent_stats", {})
    
    # 1. Get RAW "equity" (Your hand strength 0.0 to 1.0)
    equity = calculate_win_rate(hole, table)
    
    # 2. Opponent Profiling (The "Bully" Check)
    # We default to assuming they are somewhat rational (not random)
    folds = opp_stats.get("fold", 0)
    calls = opp_stats.get("call", 0)
    raises = opp_stats.get("raise", 0)
    total = folds + calls + raises
    
    if total > 5:
        fold_rate = folds / total
        raise_rate = raises / total
    else:
        # Default assumptions for first few rounds
        fold_rate = 0.2
        raise_rate = 0.2

    # 3. THE DECISION MATRIX (Threshold Based)
    
    # --- ZONE 1: MONSTER HANDS (Raise for Value) ---
    # If we win > 65% of the time, we WANT them to pay us.
    # We raise to get +3 points.
    if equity > 0.65:
        return "RAISE"

    # --- ZONE 2: TRASH HANDS (Cut Losses) ---
    # If we win < 35% of the time, we usually just Fold to save the -1.
    # UNLESS: Opponent folds a lot (>40%), then we might bluff-raise?
    # For stability, let's play safe here.
    if equity < 0.35:
        # If we have a tiny chance (e.g. 30%) and they are passive, we might call.
        # But generally, just fold.
        return "FOLD"

    # --- ZONE 3: THE MIDDLE (Tactical Play) ---
    # Equity is between 0.35 and 0.65. This is where bots usually just "Call".
    # We will be smarter.
    
    # A) Aggressive Bluff Attempt
    # If we have okay equity (45-65%) AND opponent is scared (folds > 30%),
    # we RAISE to steal the pot.
    if equity > 0.45 and fold_rate > 0.30:
        return "RAISE"

    # B) Defensive Call
    # If they are maniacs (raise > 40%), we trap them by Calling.
    if raise_rate > 0.40:
        return "CALL"
        
    # C) Standard Call
    return "CALL"

# -----------------------------
# 4. I/O glue
# -----------------------------
def main():
    raw = sys.stdin.read().strip()
    try:
        state = json.loads(raw) if raw else {}
    except Exception:
        state = {}
    action = decide_action(state)
    sys.stdout.write(json.dumps({"action": action}))

if __name__ == "__main__":
    main()