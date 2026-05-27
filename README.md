# Quant-Inspired Poker Bot

A quantitative poker-playing bot built for the FEC Quant Poker Challenge using Python.

This project implements a simplified 3-card poker strategy based on:
- Probability estimation
- Expected Value (EV) reasoning
- Opponent behaviour analysis
- Risk vs Reward modelling

The bot was designed as a stable and tournament-compatible implementation while remaining computationally efficient and logically explainable.

---

# Problem Statement

The challenge was to build a poker bot that competes in a simplified 3-card poker environment.

Each round:
- Both players receive 2 private cards
- 1 community card is placed on the table
- Each player chooses:
  - `FOLD`
  - `CALL`
  - `RAISE`

The goal is to maximize long-term expected value by making optimal decisions under uncertainty.

---

# Strategy Used

The final bot (`250122055.py`) follows a quantitative threshold-based approach.

## Core Components

### 1. Hand Evaluation
The bot classifies hands into:
- High Card
- Pair
- Flush
- Straight
- Trips
- Straight Flush

---

### 2. Probability-Based Reasoning
Stronger hands are associated with higher winning confidence.

Example:
- Straight Flush → Very high confidence
- Trips → Strong confidence
- Pair / Flush → Medium confidence
- High Card → Weak confidence

---

### 3. Expected Value (EV) Logic
The bot evaluates:
- Risk of losing points
- Reward potential from aggressive play

Decision philosophy:
- Strong hands → `RAISE`
- Medium hands → `CALL`
- Weak hands → `FOLD`

---

### 4. Opponent Modelling
The bot uses opponent statistics:
- Fold frequency
- Raise frequency

to adapt strategy dynamically.

Examples:
- Passive opponents are exploited with more aggression
- Aggressive opponents encourage safer play

---

# Project Structure

```txt
poker-bot/
│
├── 250122055.py
├── player_template.py
├── strategy_report.pdf
├── README.md
