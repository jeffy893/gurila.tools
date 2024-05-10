# Re-Porter Potty

Write out a game that is called "Re-Porter Potty"

That is played like the following:

The process is a solicitation is made for a request for proposal for a bid
an example of this would be:

you pull a card for a supplier of porter potties
and decide if you want to pay / hold onto that card
if then another card comes up with a news event about porter potties (like trump making his secret  service use porter potties), then you can play that card to make a solication for request for proposal from a News reporter who has the option to write about the porter potty event or about other events solicited by the other players
then, if the porter potty solicitation pays the most, then the news article is written and the player with the porter potty card get paid because the public is aware of idea of porter potties (for instance, parents will be more likely to buy porter potties for their family qinceneras)

## ChatGPT Response:

"Re-Porter Potty" is a game that simulates the process of soliciting requests for proposals (RFPs) for porter potties and leveraging news events to influence the outcome. The game involves players holding and playing cards representing suppliers of porter potties, news events related to porter potties, and news reporters who can write about these events.

**Players:** 3 or more

**Objective:** Earn the most money by successfully soliciting RFPs for porter potties and influencing news articles.

**Setup:**
1. Shuffle the deck of cards containing supplier cards, news event cards, and news reporter cards.
2. Each player starts with a hand of 5 cards.

**Gameplay:**
1. The game is played in rounds.
2. In each round, players take turns performing the following actions:
   a. Draw a card from the deck.
   b. Decide whether to keep the card or discard it.
   c. If a news event card is drawn, it can be played immediately to solicit an RFP from a news reporter.
   d. If a porter potty supplier card is drawn, it can be kept for potential use in the future.
3. Once all players have taken their turns, the round ends.
4. If a news event card was played, the news reporter decides which RFP to write about based on the cards played by the players.
5. The player whose porter potty RFP pays the most (based on the cards played) earns money from the RFP.

**End of Game:**
The game ends after a predetermined number of rounds. The player with the most money earned from successful RFPs wins the game.

**Example Scenario:**
- Player 1 draws a news event card about a celebrity using a porter potty at an event.
- Player 1 decides to play the news event card and solicits an RFP from a news reporter.
- The news reporter receives RFPs from other players about different events.
- The news reporter decides to write about the celebrity porter potty event, influenced by the cards played.
- Player 1, who played the porter potty supplier card related to the celebrity event, earns money from the RFP.


```python

import random

class Player:
    def __init__(self, name, money):
        self.name = name
        self.money = money
        self.hand = []

    def draw_card(self, deck):
        card = random.choice(deck)
        self.hand.append(card)
        deck.remove(card)

    def pay_to_hold(self, card):
        if card in self.hand and self.money >= 1:
            self.money -= 1
        else:
            print(f"{self.name} cannot pay to hold a supplier card.")

    def play_card(self):
        if not self.hand:
            return None
        return self.hand.pop()

class Card:
    def __init__(self, card_type, value):
        self.card_type = card_type
        self.value = value

class Game:
    def __init__(self, players, rounds):
        self.players = players
        self.deck = []
        self.rounds = rounds
        self.initialize_deck()

    def initialize_deck(self):
        # Initialize the deck with supplier cards and event cards
        for _ in range(10):  # Adjust the number of cards as needed
            self.deck.append(Card("supplier", random.randint(1, 10)))
            self.deck.append(Card("event", random.randint(1, 10)))

    def play_round(self):
        print("=== New Round ===")
        
        # The player pays to hold onto a supplier card
        supplier_player = random.choice(self.players[1:])  # Randomly select a supplier player
        supplier_cards = [card for card in supplier_player.hand if card.card_type == "supplier"]
        if supplier_cards:
            supplier_card = random.choice(supplier_cards)
            supplier_player.pay_to_hold(supplier_card)
            print(f"{supplier_player.name} pays to hold a supplier card.")
        
        # The reporter player always draws an event card
        reporter = self.players[0]
        reporter.draw_card([card for card in self.deck if card.card_type == "event"])
        event_card = reporter.play_card()
        print(f"{reporter.name} draws an event card with value {event_card.value}.")

        # The reporter player automatically chooses the winning supplier based on the event card value
        chosen_supplier = None
        for player in self.players[1:]:
            for card in player.hand:
                if card.card_type == "supplier" and card.value == event_card.value:
                    chosen_supplier = player
                    break
            if chosen_supplier:
                break

        if chosen_supplier:
            print(f"{chosen_supplier.name} wins the RFP for porter potties related to the event!")
            chosen_supplier.hand = [card for card in chosen_supplier.hand if card.card_type != "supplier" or card.value != event_card.value]

    print("=== End of Round ===")

    def simulate(self):
        for _ in range(self.rounds):
            self.play_round()

# Initialize players
players = [Player("Reporter", 10), Player("Supplier 1", 10), Player("Supplier 2", 10)]

# Initialize game
game = Game(players, rounds=5)
game.simulate()


```