import random

# Initialize the deck with 52 cards
def initialize_deck():
    suits = ['spades', 'hearts', 'diamonds', 'clubs']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = [{'suit': suit, 'rank': rank} for suit in suits for rank in ranks]
    return deck

# Function to remove a card from the deck
def remove_card(deck, card):
    return [c for c in deck if not (c['suit'] == card['suit'] and c['rank'] == card['rank'])]

# Function to calculate probabilities of low and high cards
def calculate_probabilities(deck):
    low_cards = {'2', '3', '4', '5', '6', '7'}
    high_cards = {'8', '9', '10', 'J', 'Q', 'K', 'A'}
    
    low_count = sum(1 for card in deck if card['rank'] in low_cards)
    high_count = sum(1 for card in deck if card['rank'] in high_cards)
    
    total = len(deck)
    low_prob = low_count / total if total > 0 else 0
    high_prob = high_count / total if total > 0 else 0

    return low_prob, high_prob

# Get input from the user for a card
def get_card_input(player, used_cards):
    suits = {'spades', 'hearts', 'diamonds', 'clubs'}
    ranks = {'2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'}
    
    while True:
        suit = input(f"Enter the suit for {player}'s card (spades, hearts, diamonds, clubs): ").strip().lower()
        if suit == '-1':
            print(f"{player} decided to exit the game.")
            return -1
        
        rank = input(f"Enter the rank for {player}'s card (2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K, A): ").strip().upper()
        if rank == '-1':
            print(f"{player} decided to exit the game.")
            return -1
        
        if suit not in suits or rank not in ranks:
            print("\n")
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            print("Invalid suit or rank. Please try again.")
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            print("\n")
            continue
        
        card = {'suit': suit, 'rank': rank}
        
        if card in used_cards:
            print("This card has already been used. Please choose a different card.")
        else:
            return card

# Function to display the card with symbols
def display_card(card):
    symbols = {'spades': '♠️', 'hearts': '❤️', 'diamonds': '♦️', 'clubs': '♣️'}
    try:
        return f"{card['rank']} {symbols[card['suit']]}"
    except KeyError:
        print(f"Error displaying card: {card}. Invalid card detected.")
        return "Invalid Card"

# Function to display used cards
def display_used_cards(used_cards):
    print("Cards that have been used so far:")
    for card in used_cards:
        print(display_card(card))

# Compare ranks to determine winner
def compare_ranks(dealer_card, player_card):
    ranks_order = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    dealer_rank_value = ranks_order.index(dealer_card['rank'])
    player_rank_value = ranks_order.index(player_card['rank'])
    
    if dealer_rank_value > player_rank_value:
        return "Dealer"
    elif dealer_rank_value < player_rank_value:
        return "Player"
    else:
        return "Tie"

# Initialize the deck and variables
deck = initialize_deck()
used_cards = []
round_number = 1
last_player_card = None

# Continuous game loop
while len(deck) > 0:
    print(f"\n--- Round {round_number} ---")

    # Input: Dealer's card
    if last_player_card:
        dealer_card = last_player_card
        print(f"Dealer inherits the player's last card: {display_card(dealer_card)}")
    else:
        dealer_card = get_card_input("Dealer", used_cards)
        if dealer_card == -1:
            break

    deck = remove_card(deck, dealer_card)
    used_cards.append(dealer_card)

    # Calculate probabilities after the dealer's card is drawn
    low_prob, high_prob = calculate_probabilities(deck)
    print("\n ===================================")
    print(f"After dealer's card: Low: {low_prob * 100:.2f}%, High: {high_prob * 100:.2f}%")
    print("\n ===================================")
    
    # Display used cards
    display_used_cards(used_cards)

    if len(deck) == 0:
        print("No more cards left in the deck!")
        break

    # Input: Player's card
    player_card = get_card_input("Player", used_cards)
    if player_card == -1:
        break

    deck = remove_card(deck, player_card)
    used_cards.append(player_card)

    # Compare ranks to determine outcome
    result = compare_ranks(dealer_card, player_card)
    
    if result == "Tie":
        print(f"It's a tie! Both Dealer and Player drew {player_card['rank']}.")
        last_player_card = player_card  # Dealer inherits the player's card for the next round
    else:
        print(f"{result} wins this round!")
        last_player_card = player_card  # Dealer inherits the player's card for the next round
    
    # Display used cards
    display_used_cards(used_cards)

    if len(deck) == 0:
        print("No more cards left in the deck!")
        break

    # Ask if the user wants to continue or stop
    continue_game = input("Do you want to continue to the next round? (y/n): ").strip().lower()
    if continue_game != 'y':
        break
    
    round_number += 1

print("Game over!")
