def decide_action(state: dict) -> str:
    """
    Quant v3 – Belief Poisoner
    Non-EV, non-threshold, entropy-controlled strategy
    """

    import random
    from collections import Counter

    # -------- persistent state --------
    if not hasattr(decide_action, "mem"):
        decide_action.mem = {
            "round": 0,
            "my_actions": [],
            "opp_actions": [],
            "phase": "EARLY"
        }

    mem = decide_action.mem
    mem["round"] += 1

    if mem["round"] < 20:
        mem["phase"] = "EARLY"
    elif mem["round"] < 60:
        mem["phase"] = "MID"
    else:
        mem["phase"] = "LATE"

    opp_last = state.get("opponent_last_action")
    if opp_last:
        mem["opp_actions"].append(opp_last)
        mem["opp_actions"] = mem["opp_actions"][-12:]

    hole = state["hole_cards"]
    board = state["community_card"]

    # -------- hand shape (not strength) --------
    ranks = sorted([c[0] for c in hole + [board]])
    suits = [c[1] for c in hole + [board]]

    rank_count = Counter(ranks)
    suit_count = Counter(suits)

    has_pair = 2 in rank_count.values()
    has_trips = 3 in rank_count.values()
    is_flush = max(suit_count.values()) == 3
    is_connected = ranks[2] - ranks[0] <= 4

    # -------- opponent belief model --------
    opp_raise_rate = mem["opp_actions"].count("RAISE") / max(1, len(mem["opp_actions"]))
    opp_fold_rate  = mem["opp_actions"].count("FOLD")  / max(1, len(mem["opp_actions"]))

    # -------- entropy budget (key idea) --------
    recent_me = mem["my_actions"][-10:]
    raise_freq = recent_me.count("RAISE") / max(1, len(recent_me))
    fold_freq  = recent_me.count("FOLD")  / max(1, len(recent_me))

    # -------- belief poisoning rules --------
    # We WANT opponent to mislearn us
    poison_raise = raise_freq < 0.22
    poison_fold  = fold_freq  < 0.18

    # -------- ACTION LOGIC (NON MONOTONIC) --------

    # 1. Trips / strong made hands
    if has_trips:
        if mem["phase"] == "EARLY":
            action = "CALL"   # underplay early
        else:
            action = "RAISE"
    
    # 2. Pair / strong shape
    elif has_pair:
        if opp_fold_rate > 0.45 and poison_raise:
            action = "RAISE"
        else:
            action = "CALL"

    # 3. Draw-ish hands (connected / suited)
    elif is_flush or is_connected:
        if mem["phase"] == "MID" and poison_raise:
            action = "RAISE"
        else:
            action = "CALL"

    # 4. Pure garbage (THIS IS WHERE WE DIFFER)
    else:
        if opp_raise_rate > 0.45:
            action = "FOLD"
        elif poison_raise and mem["phase"] == "LATE":
            action = "RAISE"   # late fake strength
        elif poison_fold:
            action = "FOLD"
        else:
            action = "CALL"

    # -------- entropy correction --------
    # prevent getting stuck
    if random.random() < 0.03:
        action = random.choice(["FOLD", "CALL", "RAISE"])

    mem["my_actions"].append(action)
    mem["my_actions"] = mem["my_actions"][-15:]

    return action