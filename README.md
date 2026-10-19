Blackjack Strategy Advisor

Author: Kekeba Hachalu Bekele

A Python project that turns a simple Blackjack game into a small decision-making system.

What it does
Plays Blackjack with a coach: before each move, an AI advisor suggests Hit, Stand, Double, or Split based on your hand and the dealer's visible card.
Scores hands correctly: Aces count as 11 or 1 as needed, so hands like Ace + 9 + 5 are not wrongly counted as busts.
Measures strategy quality: a simulator plays thousands of hands with a naive "hit until 17" strategy and with the advisor, then compares their win rates (about 41% vs 43% in my runs).
How it works
Card, Deck, Hand classes replace repeated card-drawing code with one reusable version.
BasicStrategyAdvisor applies standard Basic Strategy rules for hard totals, soft totals, and pairs.
A simulation engine runs the comparison and prints the results.
Run it

Requires Python 3 and no extra libraries.

bash
python3 blackjack_strategy_advisor.py

Choose 1 to play a coached hand or 2 to run the simulation.

Future work

Full Split support, card counting, charts with matplotlib, and a machine-learning model compared against the hand-coded strategy.

Built by Kekeba Hachalu Bekele during my first Python course, as a personal project.
