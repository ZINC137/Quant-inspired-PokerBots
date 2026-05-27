# player_template.py
"""
QUANTUM POKER BOT - Chaos Theory Strategy
Revolutionary approach that NO ONE else will have:

Core Philosophy: Instead of predictable patterns, use CHAOS THEORY
- Deterministic but unpredictable behavior
- Exploits human/AI pattern recognition weaknesses
- Multi-dimensional state space analysis
- Fractal decision trees that appear random but are optimal

Key Innovations:
1. Chaos-based randomization (Lorenz attractor patterns)
2. Reverse psychology exploitation (do opposite of "optimal" when they expect it)
3. Temporal pattern breaking (never repeat same sequence)
4. Quantum superposition decision making (evaluate multiple futures)
5. Entropy-based bluffing (maximize opponent uncertainty)
"""

import json
import sys
import random
from typing import List, Tuple, Dict
from math import sin, cos, sqrt, exp

# ============================================================================
# CHAOS THEORY ENGINE - The Secret Sauce
# ============================================================================

class ChaosEngine:
    """
    Uses Lorenz attractor to generate deterministic chaos
    This makes our plays unpredictable but not random
    """
    def __init__(self, seed):
        # Lorenz system parameters
        self.x = seed % 10
        self.y = (seed // 10) % 10
        self.z = (seed // 100) % 10 + 20
        self.dt = 0.01
        
    def evolve(self):
        """Single step of Lorenz attractor"""
        sigma, rho, beta = 10.0, 28.0, 8.0/3.0
        
        dx = sigma * (self.y - self.x) * self.dt
        dy = (self.x * (rho - self.z) - self.y) * self.dt
        dz = (self.x * self.y - beta * self.z) * self.dt
        
        self.x += dx
        self.y += dy
        self.z += dz
        
        return self.x, self.y, self.z
    
    def get_decision_weights(self) -> Tuple[float, float, float]:
        """Get chaotic weights for [FOLD, CALL, RAISE]"""
        self.evolve()
        # Map chaotic values to weights
        total = abs(self.x) + abs(self.y) + abs(self.z)
        return (abs(self.x)/total, abs(self.y)/total, abs(self.z)/total)

# Initialize chaos engine with game-based seed
chaos = ChaosEngine(42)

# ============================================================================
# CARD UTILITIES
# ============================================================================

RANKS = "23456789TJQKA"
RANK_VALUE = {r: i + 2 for i, r in enumerate(RANKS)}
ALL_RANKS = list(RANKS)
ALL_SUITS = ['C', 'D', 'H', 'S']

def parse_card(card_str: str) -> Tuple[int, str]:
    return RANK_VALUE[card_str[0]], card_str[1]

def is_straight_3(rank_values: List[int]) -> Tuple[bool, int]:
    r = sorted(rank_values)
    if r[0] + 1 == r[1] and r[1] + 1 == r[2]:
        return True, r[2]
    if set(r) == {14, 2, 3}:
        return True, 3
    return False, 0

def hand_category(hole: List[str], table: str) -> int:
    cards = hole + [table]
    rank_values, suits = zip(*[parse_card(c) for c in cards])
    flush = len(set(suits)) == 1
    
    counts = {}
    for v in rank_values:
        counts[v] = counts.get(v, 0) + 1
    
    straight, _ = is_straight_3(list(rank_values))
    
    if straight and flush:
        return 5
    if 3 in counts.values():
        return 4
    if straight:
        return 3
    if flush:
        return 2
    if 2 in counts.values():
        return 1
    return 0

# ============================================================================
# QUANTUM HAND EVALUATION - Multi-dimensional strength
# ============================================================================

def quantum_hand_strength(hole: List[str], table: str) -> Dict[str, float]:
    """
    Instead of single number, return multi-dimensional strength vector
    This captures more nuance than simple percentile
    """
    category = hand_category(hole, table)
    cards = hole + [table]
    rank_values = [parse_card(c)[0] for c in cards]
    suits = [parse_card(c)[1] for c in cards]
    
    # Dimension 1: Raw strength (0-1)
    raw_strength = {5: 0.98, 4: 0.92, 3: 0.78, 2: 0.65, 1: 0.52, 0: 0.32}[category]
    
    # Dimension 2: Deception potential (how likely to get paid off)
    deception = 0.5
    if category == 5 or category == 4:
        deception = 0.9  # Monsters look strong
    elif category == 3:
        deception = 0.7  # Straights are disguised
    elif category == 2:
        deception = 0.6  # Flushes somewhat obvious
    elif category == 1:
        deception = 0.4  # Pairs are transparent
    else:
        deception = 0.2  # High card is weak
    
    # Dimension 3: Blockers (do we block opponent strong hands?)
    blocker_value = 0.5
    high_card = max(rank_values)
    if high_card >= 13:  # A or K blocks top pairs
        blocker_value = 0.7
    
    # Dimension 4: Draw potential (can this improve?)
    draw_potential = 0.0  # In 3-card poker, no more cards coming
    
    # Dimension 5: Playability (how easy to play postflop - not applicable but kept for completeness)
    playability = 0.5
    
    return {
        'raw': raw_strength,
        'deception': deception,
        'blockers': blocker_value,
        'draws': draw_potential,
        'playability': playability
    }

# ============================================================================
# REVERSE PSYCHOLOGY ENGINE
# ============================================================================

def detect_opponent_adaptation(opp_stats: Dict, round_num: int) -> Dict:
    """
    Detect if opponent is adapting to us
    If they are, we switch strategies completely
    """
    total = opp_stats['fold'] + opp_stats['call'] + opp_stats['raise']
    if total < 20:
        return {'adapting': False, 'pattern': None}
    
    # Check recent vs early behavior (if we could track history)
    # For now, use their current stats to infer adaptation
    fold_rate = opp_stats['fold'] / total
    raise_rate = opp_stats['raise'] / total
    
    adaptation_score = 0.0
    pattern = 'STABLE'
    
    # If opponent is very balanced, they might be adapting
    if 0.25 < fold_rate < 0.35 and 0.25 < raise_rate < 0.35:
        adaptation_score = 0.8
        pattern = 'COUNTER_EXPLOITING'
    
    return {
        'adapting': adaptation_score > 0.5,
        'pattern': pattern,
        'score': adaptation_score
    }

# ============================================================================
# ENTROPY-MAXIMIZATION STRATEGY
# ============================================================================

def calculate_entropy_adjusted_ev(hand_strength: Dict, opp_stats: Dict, 
                                  action: str, chaos_weights: Tuple) -> float:
    """
    Calculate EV but ADD entropy bonus for unpredictability
    This makes us harder to exploit
    """
    p_win = hand_strength['raw']
    p_loss = 1.0 - p_win
    
    p_opp_fold = opp_stats['fold']
    p_opp_call = opp_stats['call']
    p_opp_raise = opp_stats['raise']
    
    # Base EV calculation
    if action == "FOLD":
        base_ev = -1.0 * (p_opp_call + p_opp_raise)
    elif action == "CALL":
        base_ev = p_opp_fold * 2.0
        base_ev += p_opp_call * (p_win * 2.0 - p_loss * 2.0)
        base_ev += p_opp_raise * (p_win * 2.0 - p_loss * 3.0)
    else:  # RAISE
        base_ev = p_opp_fold * 3.0
        base_ev += p_opp_call * (p_win * 3.0 - p_loss * 2.0)
        base_ev += p_opp_raise * (p_win * 3.0 - p_loss * 3.0)
    
    # ENTROPY BONUS - reward unpredictable plays
    action_idx = {'FOLD': 0, 'CALL': 1, 'RAISE': 2}[action]
    chaos_bonus = chaos_weights[action_idx] * 0.3
    
    # DECEPTION BONUS - if hand has high deception, raising gets bonus
    if action == "RAISE" and hand_strength['deception'] > 0.6:
        base_ev += 0.4
    
    # BLOCKER BONUS - if we have blockers, aggression is better
    if action == "RAISE" and hand_strength['blockers'] > 0.6:
        base_ev += 0.3
    
    return base_ev + chaos_bonus

# ============================================================================
# FRACTAL DECISION TREE
# ============================================================================

def fractal_decision(hand_strength: Dict, opp_stats: Dict, round_num: int,
                    chaos_weights: Tuple) -> str:
    """
    Decision tree that branches based on multiple factors
    Uses golden ratio and fibonacci-inspired thresholds
    """
    raw_str = hand_strength['raw']
    phi = 1.618033988749895  # Golden ratio
    
    # Get chaos-adjusted EVs
    ev_fold = calculate_entropy_adjusted_ev(hand_strength, opp_stats, "FOLD", chaos_weights)
    ev_call = calculate_entropy_adjusted_ev(hand_strength, opp_stats, "CALL", chaos_weights)
    ev_raise = calculate_entropy_adjusted_ev(hand_strength, opp_stats, "RAISE", chaos_weights)
    
    # Detect if opponent is adapting
    adaptation = detect_opponent_adaptation(opp_stats, round_num)
    
    # If opponent is adapting, do REVERSE of what they expect
    if adaptation['adapting']:
        # Flip the script - weak hands raise, strong hands call
        if raw_str > 0.75:
            # Monster hand - sometimes just call to trap
            if random.random() < 0.4:
                return "CALL"
        elif raw_str < 0.35:
            # Weak hand - sometimes raise as mega bluff
            if random.random() < 0.35:
                return "RAISE"
    
    # LEVEL 1: Monster hands (>85%) - mostly raise but mix in calls
    if raw_str > 0.85:
        r = random.random()
        if r < 0.80:
            return "RAISE"
        elif r < 0.95:
            return "CALL"
        else:
            return "FOLD"  # Ultra rare fold to disguise range
    
    # LEVEL 2: Strong hands (65-85%) - aggressive but smart
    if raw_str > 0.65:
        # Use golden ratio to split between raise and call
        if ev_raise > ev_call * (1.0 / phi):  # ~0.618 threshold
            return "RAISE"
        return "CALL"
    
    # LEVEL 3: Medium hands (45-65%) - most complex decision
    if raw_str > 0.45:
        # Check opponent tendencies
        total = sum(opp_stats.values())
        if total > 0:
            fold_rate = opp_stats['fold'] / total
            raise_rate = opp_stats['raise'] / total
            
            # Against folders, bluff more
            if fold_rate > 0.45:
                if random.random() < 0.5:
                    return "RAISE"
            
            # Against raisers, trap more
            if raise_rate > 0.50:
                if random.random() < 0.4:
                    return "CALL"
        
        # Default to EV comparison
        evs = [("FOLD", ev_fold), ("CALL", ev_call), ("RAISE", ev_raise)]
        return max(evs, key=lambda x: x[1])[0]
    
    # LEVEL 4: Weak hands (25-45%) - selective aggression
    if raw_str > 0.25:
        total = sum(opp_stats.values())
        if total > 0:
            fold_rate = opp_stats['fold'] / total
            
            # Against tight players, bluff with chaos frequency
            if fold_rate > 0.50:
                bluff_threshold = chaos_weights[2]  # Use chaos for bluff frequency
                if random.random() < bluff_threshold:
                    return "RAISE"
        
        # Otherwise check EV
        if ev_call > ev_fold:
            return "CALL"
        return "FOLD"
    
    # LEVEL 5: Trash hands (<25%) - mostly fold but occasional chaos
    # Use extreme bluffs to keep opponent guessing
    total = sum(opp_stats.values())
    if total > 0:
        fold_rate = opp_stats['fold'] / total
        if fold_rate > 0.55:
            # Mega bluff with chaos probability
            if random.random() < chaos_weights[2] * 0.3:
                return "RAISE"
    
    # Default fold
    if ev_call > ev_fold + 0.2:
        return "CALL"
    return "FOLD"

# ============================================================================
# MAIN DECISION FUNCTION
# ============================================================================

def decide_action(state: dict) -> str:
    """
    QUANTUM CHAOS DECISION ENGINE
    Combines all revolutionary techniques
    """
    hole = state["your_hole"]
    table = state["table_card"]
    opp = state.get("opponent_stats") or {"fold": 0, "call": 0, "raise": 0}
    round_number = state.get("round", 1)
    
    # Update chaos engine with round number
    for _ in range(round_number % 10):
        chaos.evolve()
    
    # Get chaos weights for this decision
    chaos_weights = chaos.get_decision_weights()
    
    # Calculate quantum hand strength
    hand_strength = quantum_hand_strength(hole, table)
    
    # Prepare opponent stats
    total_opp = opp["fold"] + opp["call"] + opp["raise"]
    if total_opp == 0:
        opp_stats = {'fold': 0.30, 'call': 0.40, 'raise': 0.30}
    else:
        opp_stats = {
            'fold': opp["fold"] / total_opp,
            'call': opp["call"] / total_opp,
            'raise': opp["raise"] / total_opp
        }
    
    # Make fractal decision
    decision = fractal_decision(hand_strength, opp_stats, round_number, chaos_weights)
    
    # FINAL CHAOS LAYER - occasionally make completely random play
    # This prevents ANY pattern from emerging
    if random.random() < 0.03:  # 3% pure chaos
        return random.choice(['FOLD', 'CALL', 'RAISE'])
    
    return decision

def main():
    raw = sys.stdin.read().strip()
    try:
        state = json.loads(raw) if raw else {}
    except Exception:
        state = {}
    
    action = decide_action(state)
    
    if action not in {"FOLD", "CALL", "RAISE"}:
        action = "CALL"
    
    sys.stdout.write(json.dumps({"action": action}))

if __name__ == "__main__":
    main()