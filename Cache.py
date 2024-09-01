import discord
import random
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Initialize the deck with 52 cards
def initialize_deck():
    suits = ['spades', 'hearts', 'diamonds', 'clubs']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = [{'suit': suit, 'rank': rank} for suit in suits for rank in ranks]
    return deck

# Function to remove a card from the deck
def remove_card(deck, card):
    return [c for c in deck if not (c['suit'] == card['suit'] and c['rank'] == card['rank'])]

# Function to calculate probabilities of lower or higher cards relative to dealer's card
def calculate_probabilities(deck, dealer_card):
    ranks_order = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    dealer_rank_index = ranks_order.index(dealer_card['rank'])
    
    lower_count = sum(1 for card in deck if ranks_order.index(card['rank']) < dealer_rank_index)
    higher_count = sum(1 for card in deck if ranks_order.index(card['rank']) > dealer_rank_index)
    
    total = len(deck)
    lower_prob = lower_count / total if total > 0 else 0
    higher_prob = higher_count / total if total > 0 else 0

    return lower_prob, higher_prob

# Function to display the card with symbols
def display_card(card):
    symbols = {'spades': '♠️', 'hearts': '❤️', 'diamonds': '♦️', 'clubs': '♣️'}
    return f"{card['rank']} {symbols[card['suit']]}"

# Function to filter and display unique used cards
def display_unique_used_cards(used_cards):
    unique_used_cards = []
    for card in used_cards:
        if card not in unique_used_cards:
            unique_used_cards.append(card)
    
    return "\n".join(display_card(card) for card in unique_used_cards)

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

# Game state
deck = initialize_deck()
used_cards = []
round_number = 1
last_player_card = None
dealer_card = None  # 初始化 dealer_card

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    global deck, used_cards, round_number, last_player_card, dealer_card
    
    if message.author == client.user:
        return
    
    if message.content.lower().startswith("!startgame"):
        deck = initialize_deck()
        used_cards = []
        round_number = 1
        last_player_card = None
        dealer_card = None
        await message.channel.send("Game started! Enter `!dealercard` to start.")

    if message.content.lower().startswith("!dealercard"):
        if last_player_card:
            dealer_card = last_player_card
            last_player_card = None  # Reset after use
            await message.channel.send(f"Dealer inherits the player's last card: {display_card(dealer_card)}")
        else:
            await message.channel.send("Enter the suit and rank for Dealer's card (e.g., `!dealer spades Q`)")
            return

        deck = remove_card(deck, dealer_card)
        used_cards.append(dealer_card)

        lower_prob, higher_prob = calculate_probabilities(deck, dealer_card)
        await message.channel.send(f"Based on dealer's card: Lower: {lower_prob * 100:.2f}%, Higher: {higher_prob * 100:.2f}%")
        await message.channel.send(f"Cards that have been used so far:\n{display_unique_used_cards(used_cards)}")

        if len(deck) == 0:
            await message.channel.send("No more cards left in the deck!")
            return

    if message.content.lower().startswith("!dealer"):
        _, suit, rank = message.content.split()
        dealer_card = {'suit': suit, 'rank': rank.upper()}  # 这里为 dealer_card 赋值
        if dealer_card in used_cards:
            await message.channel.send("This card has already been used. Please choose a different card.")
            return
        
        deck = remove_card(deck, dealer_card)
        used_cards.append(dealer_card)

        lower_prob, higher_prob = calculate_probabilities(deck, dealer_card)
        await message.channel.send(f"Based on dealer's card: Lower: {lower_prob * 100:.2f}%, Higher: {higher_prob * 100:.2f}%")
        await message.channel.send(f"Cards that have been used so far:\n{display_unique_used_cards(used_cards)}")

        if len(deck) == 0:
            await message.channel.send("No more cards left in the deck!")
            return
        
    if message.content.lower().startswith("!player"):
        if not dealer_card:
            await message.channel.send("Please deal the Dealer's card first.")
            return

        _, suit, rank = message.content.split()
        player_card = {'suit': suit, 'rank': rank.upper()}
        if player_card in used_cards:
            await message.channel.send("This card has already been used. Please choose a different card.")
            return
        
        deck = remove_card(deck, player_card)
        used_cards.append(player_card)

        result = compare_ranks(dealer_card, player_card)
        if result == "Tie":
            await message.channel.send(f"It's a tie! Both Dealer and Player drew {player_card['rank']}.")
            last_player_card = player_card
        else:
            await message.channel.send(f"{result} wins this round!")
            last_player_card = player_card
        
        await message.channel.send(f"Cards that have been used so far:\n{display_unique_used_cards(used_cards)}")

        # 在每轮结束后重新计算概率
        lower_prob, higher_prob = calculate_probabilities(deck, dealer_card)
        await message.channel.send(f"Updated probabilities: Lower: {lower_prob * 100:.2f}%, Higher: {higher_prob * 100:.2f}%")

        if len(deck) == 0:
            await message.channel.send("No more cards left in the deck!")
            return

client.run(TOKEN)

