"""
Blackjack Strategy Advisor
Author: Kekeba Hachalu Bekele

Built during my first Python course as a personal project.
I rebuilt a basic Blackjack game to fix its flaws (duplicated card-drawing
code, Aces hardcoded to 11 causing false busts) and added two things:
  - an AI advisor that recommends Hit / Stand / Double / Split
  - a simulator that measures how much good decisions improve win rate

Run: python3 blackjack_strategy_advisor.py   (Python 3, no extra libraries)
Future work: full Split support, card counting, charts, ML-based advisor.
"""

from random import shuffle

# ---------- Core models: Card, Deck, Hand ----------

RANK_NAMES = {1: "Ace", 11: "Jack", 12: "Queen", 13: "King"}


class Card:
    """A playing card. Rank 1-13 (1 = Ace, 11-13 = face cards)."""

    SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    @property
    def name(self):
        return RANK_NAMES.get(self.rank, str(self.rank))

    @property
    def base_value(self):
        # Ace counts as 11 here; Hand lowers it to 1 when needed.
        if self.rank in (11, 12, 13):
            return 10
        if self.rank == 1:
            return 11
        return self.rank

    @property
    def is_ace(self):
        return self.rank == 1

    def article(self):
        return "an" if self.name[0] in "AEIOU" else "a"

    def __str__(self):
        return f"{self.name} of {self.suit}"


class Deck:
    """A shuffled 52-card deck."""

    def __init__(self):
        self.cards = [Card(rank, suit) for suit in Card.SUITS for rank in range(1, 14)]
        shuffle(self.cards)

    def draw(self):
        if not self.cards:
            self.__init__()  # reshuffle a fresh deck if empty
        return self.cards.pop()


class Hand:
    """A hand with correct Ace handling (fixes the false-bust bug)."""

    def __init__(self):
        self.cards = []

    def add(self, card):
        self.cards.append(card)

    @property
    def value(self):
        total = sum(c.base_value for c in self.cards)
        aces = sum(1 for c in self.cards if c.is_ace)
        while total > 21 and aces:  # turn an Ace from 11 into 1
            total -= 10
            aces -= 1
        return total

    @property
    def is_soft(self):
        # True if an Ace is still counted as 11.
        total = sum(c.base_value for c in self.cards)
        aces_left = sum(1 for c in self.cards if c.is_ace)
        while total > 21 and aces_left:
            total -= 10
            aces_left -= 1
        return aces_left > 0

    @property
    def is_pair(self):
        return len(self.cards) == 2 and self.cards[0].rank == self.cards[1].rank

    @property
    def is_blackjack(self):
        return len(self.cards) == 2 and self.value == 21

    @property
    def is_bust(self):
        return self.value > 21

    def __str__(self):
        return ", ".join(str(c) for c in self.cards)


# ---------- AI advisor: Basic Strategy ----------

HIT, STAND, DOUBLE, SPLIT = "Hit", "Stand", "Double", "Split"
ACTION_LABELS = {HIT: "Hit", STAND: "Stand", DOUBLE: "Double down", SPLIT: "Split"}


class BasicStrategyAdvisor:
    """Recommends an action from the player's hand and the dealer's up card."""

    def suggest(self, hand, dealer_up_card):
        up = 11 if dealer_up_card.is_ace else dealer_up_card.base_value
        if hand.is_pair:
            action = self._pair_strategy(hand.cards[0].rank, up)
            if action is not None:
                return action
        if hand.is_soft:
            return self._soft_strategy(hand.value, up)
        return self._hard_strategy(hand.value, up)

    def _pair_strategy(self, rank, up):
        if rank == 1:
            return SPLIT
        if rank in (10, 11, 12, 13):
            return STAND  # never split tens or face cards
        if rank == 9:
            return STAND if up in (7, 10, 11) else SPLIT
        if rank == 8:
            return SPLIT
        if rank == 7:
            return SPLIT if up <= 7 else HIT
        if rank == 6:
            return SPLIT if up <= 6 else HIT
        if rank == 5:
            return None  # play as a hard 10
        if rank in (2, 3):
            return SPLIT if up <= 7 else HIT
        return None

    def _soft_strategy(self, total, up):
        if total >= 19:
            return STAND
        if total == 18:
            if up in (2, 3, 4, 5, 6):
                return DOUBLE
            return STAND if up in (7, 8) else HIT
        if total == 17:
            return DOUBLE if up in (3, 4, 5, 6) else HIT
        if total in (15, 16):
            return DOUBLE if up in (4, 5, 6) else HIT
        if total in (13, 14):
            return DOUBLE if up in (5, 6) else HIT
        return HIT

    def _hard_strategy(self, total, up):
        if total >= 17:
            return STAND
        if 13 <= total <= 16:
            return STAND if up <= 6 else HIT
        if total == 12:
            return STAND if up in (4, 5, 6) else HIT
        if total == 11:
            return DOUBLE
        if total == 10:
            return DOUBLE if up <= 9 else HIT
        if total == 9:
            return DOUBLE if up in (3, 4, 5, 6) else HIT
        return HIT


# ---------- Simulator: measures strategy performance ----------

def naive_strategy(hand, dealer_up_card):
    """Beginner habit: hit until 17, ignoring the dealer's card."""
    return HIT if hand.value < 17 else STAND


def dealer_plays(deck, dealer_hand):
    while dealer_hand.value < 17:
        dealer_hand.add(deck.draw())
    return dealer_hand


def play_one_hand(deck, strategy_fn):
    """Play one hand; return 'win', 'lose' or 'push'. Split counts as Stand."""
    player, dealer = Hand(), Hand()
    for _ in range(2):
        player.add(deck.draw())
        dealer.add(deck.draw())

    if player.is_blackjack:
        return "push" if dealer.is_blackjack else "win"

    while True:
        action = strategy_fn(player, dealer.cards[0])
        if action == HIT:
            player.add(deck.draw())
            if player.is_bust:
                return "lose"
        elif action == DOUBLE:
            player.add(deck.draw())
            if player.is_bust:
                return "lose"
            break
        else:
            break

    dealer_plays(deck, dealer)

    if dealer.is_bust or player.value > dealer.value:
        return "win"
    if player.value < dealer.value:
        return "lose"
    return "push"


def run_simulation(strategy_fn, num_hands):
    deck = Deck()
    results = {"win": 0, "lose": 0, "push": 0}
    for _ in range(num_hands):
        results[play_one_hand(deck, strategy_fn)] += 1
    return results


def win_rate(results):
    return 100 * results["win"] / sum(results.values())


def compare_strategies(num_hands=10000):
    advisor = BasicStrategyAdvisor()
    advisor_strategy = lambda hand, up: advisor.suggest(hand, up)

    print(f"Running {num_hands:,} simulated hands per strategy...\n")
    naive_results = run_simulation(naive_strategy, num_hands)
    advisor_results = run_simulation(advisor_strategy, num_hands)

    print("Naive strategy ('hit until 17'):")
    print(f"  {naive_results}  -> win rate: {win_rate(naive_results):.2f}%\n")
    print("AI Basic Strategy Advisor:")
    print(f"  {advisor_results}  -> win rate: {win_rate(advisor_results):.2f}%\n")

    diff = win_rate(advisor_results) - win_rate(naive_results)
    print(f"Result: the Advisor changes the win rate by {diff:+.2f} "
          f"percentage points over {num_hands:,} hands.")


# ---------- Interactive game coached by the advisor ----------

def announce_draw(card):
    print(f"Drew {card.article()} {card.name} of {card.suit}.")


def play_round():
    deck = Deck()
    advisor = BasicStrategyAdvisor()
    player, dealer = Hand(), Hand()

    for _ in range(2):
        card = deck.draw()
        player.add(card)
        announce_draw(card)
        dealer.add(deck.draw())

    print(f"\nDealer shows: {dealer.cards[0]}")
    print(f"Your hand: {player} (value: {player.value})\n")

    if player.is_blackjack:
        print("BLACKJACK!")
    else:
        while player.value < 21:
            suggestion = advisor.suggest(player, dealer.cards[0])
            choice = input(f"You have {player.value}. AI Advisor suggests: "
                           f"{ACTION_LABELS[suggestion]}. Hit (y/n)? ").strip().lower()
            if choice == "n":
                break
            elif choice == "y":
                card = deck.draw()
                player.add(card)
                announce_draw(card)
            else:
                print("Sorry, I didn't get that.")

    print(f"\nYour final hand: {player} (value: {player.value})")
    if player.is_bust:
        print("BUST. Dealer wins!")
        return

    print(f"Dealer reveals: {dealer}")
    while dealer.value < 17:
        card = deck.draw()
        dealer.add(card)
        print(f"Dealer draws {card.name} of {card.suit}. Dealer has {dealer.value}.")

    print(f"Dealer final hand: {dealer} (value: {dealer.value})")
    print("\n--- RESULT ---")
    if dealer.is_bust or player.value > dealer.value:
        print("You win!")
    elif player.value < dealer.value:
        print("Dealer wins!")
    else:
        print("Push.")


# ---------- Entry point ----------

def main():
    print("=== Blackjack Strategy Advisor ===")
    print("1. Play a hand (with AI coaching)")
    print("2. Run a statistical simulation (Advisor vs. Naive strategy)")
    choice = input("Choose an option (1/2): ").strip()

    if choice == "1":
        play_round()
    elif choice == "2":
        raw = input("How many hands to simulate? [default 10000]: ").strip()
        try:
            n = int(raw) if raw else 10000
        except ValueError:
            n = 10000
        compare_strategies(n)
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()
