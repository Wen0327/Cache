const { Client, GatewayIntentBits,Partials } = require("discord.js");
const dotenv = require("dotenv");

dotenv.config();

const TOKEN = process.env.DISCORD_TOKEN;

const client = new Client({
  intents: [
    GatewayIntentBits.DirectMessages,
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildBans,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
  ],
  partials: [Partials.Channel],
});

// Initialize the deck with 52 cards
function initializeDeck() {
  const suits = ["spades", "hearts", "diamonds", "clubs"];
  const ranks = [
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "J",
    "Q",
    "K",
    "A",
  ];
  let deck = [];
  for (let suit of suits) {
    for (let rank of ranks) {
      deck.push({ suit: suit, rank: rank });
    }
  }
  return deck;
}

// Function to remove a card from the deck
function removeCard(deck, card) {
  return deck.filter((c) => !(c.suit === card.suit && c.rank === card.rank));
}

// Function to calculate probabilities of lower or higher cards relative to dealer's card
function calculateProbabilities(deck, dealerCard) {
  const ranksOrder = [
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "J",
    "Q",
    "K",
    "A",
  ];
  const dealerRankIndex = ranksOrder.indexOf(dealerCard.rank);

  const lowerCount = deck.filter(
    (card) => ranksOrder.indexOf(card.rank) < dealerRankIndex
  ).length;
  const higherCount = deck.filter(
    (card) => ranksOrder.indexOf(card.rank) > dealerRankIndex
  ).length;

  const total = deck.length;
  const lowerProb = total > 0 ? lowerCount / total : 0;
  const higherProb = total > 0 ? higherCount / total : 0;

  return { lowerProb, higherProb };
}

// Function to display the card with symbols
function displayCard(card) {
  const symbols = { spades: "♠️", hearts: "❤️", diamonds: "♦️", clubs: "♣️" };
  return `${card.rank} ${symbols[card.suit]}`;
}

// Function to filter and display unique used cards
function displayUniqueUsedCards(usedCards) {
  const uniqueUsedCards = [...new Set(usedCards.map(JSON.stringify))].map(
    JSON.parse
  );
  return uniqueUsedCards.map(displayCard).join("\n");
}

// Compare ranks to determine winner
function compareRanks(dealerCard, playerCard) {
  const ranksOrder = [
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "J",
    "Q",
    "K",
    "A",
  ];
  const dealerRankValue = ranksOrder.indexOf(dealerCard.rank);
  const playerRankValue = ranksOrder.indexOf(playerCard.rank);

  if (dealerRankValue > playerRankValue) {
    return "Dealer";
  } else if (dealerRankValue < playerRankValue) {
    return "Player";
  } else {
    return "Tie";
  }
}

// Game state
let deck = initializeDeck();
let usedCards = [];
let lastPlayerCard = null;
let dealerCard = null;

client.once("ready", () => {
  console.log(`Logged in as ${client.user.tag}`);
});

client.on("messageCreate", async (message) => {
  console.log(`Received message: '${message}'`);
  if (message.author.bot) return;

  const args = message.content.trim().split(/ +/);

  if (message.content.toLowerCase() === "!startgame") {
    deck = initializeDeck();
    usedCards = [];
    lastPlayerCard = null;
    dealerCard = null;
    await message.channel.send("Game started! Enter `!dealercard` to start.");
    await message.channel.send("Enter `!hg` to check the rule");
    await message.channel.send(
      "'spades': '♠️', 'hearts': '❤️', 'diamonds': '♦️', 'clubs': '♣️'"
    );
  }

  if (message.content.toLowerCase() === "!hg") {
    await message.channel.send(
      "'spades': '♠️', 'hearts': '❤️', 'diamonds': '♦️', 'clubs': '♣️'"
    );
  }

  if (message.content.toLowerCase() === "!reset") {
    deck = initializeDeck();
    usedCards = [];
    lastPlayerCard = null;
    dealerCard = null;
    await message.channel.send(
      "Game has been reset! Enter `!dealercard` to start."
    );
  }

  if (message.content.toLowerCase() === "!dealercard") {
    if (lastPlayerCard) {
      dealerCard = lastPlayerCard;
      lastPlayerCard = null;
      await message.channel.send(
        `Dealer inherits the player's last card: ${displayCard(dealerCard)}`
      );
    } else {
      await message.channel.send(
        "Enter the suit and rank for Dealer's card (e.g., `!dealer spades Q`)"
      );
      return;
    }

    deck = removeCard(deck, dealerCard);
    usedCards.push(dealerCard);

    const { lowerProb, higherProb } = calculateProbabilities(deck, dealerCard);
    await message.channel.send(
      `Based on dealer's card: Lower: ${(lowerProb * 100).toFixed(
        2
      )}%, Higher: ${(higherProb * 100).toFixed(2)}%`
    );
    await message.channel.send(
      `Cards that have been used so far:\n${displayUniqueUsedCards(usedCards)}`
    );

    if (deck.length === 0) {
      await message.channel.send("No more cards left in the deck!");
    }
  }

  if (
    message.content.toLowerCase() === "!dealer" ||
    message.content.toLowerCase().startsWith("!player")
  ) {
    if (args.length !== 3) {
      await message.channel.send(
        "Invalid format. Please enter the command in the format: `!player <suit> <rank>` or `!dealer <suit> <rank>`."
      );
      return;
    }

    const suit = args[1].toLowerCase();
    const rank = args[2].toUpperCase();

    const validSuits = ["spades", "hearts", "diamonds", "clubs"];
    const validRanks = [
      "2",
      "3",
      "4",
      "5",
      "6",
      "7",
      "8",
      "9",
      "10",
      "J",
      "Q",
      "K",
      "A",
    ];

    if (!validSuits.includes(suit) || !validRanks.includes(rank)) {
      await message.channel.send(
        "Invalid suit or rank. Please enter a valid suit ('spades', 'hearts', 'diamonds', 'clubs') and rank (2-10, J, Q, K, A)."
      );
      return;
    }

    const card = { suit, rank };

    if (message.content.toLowerCase() === "!dealer") {
      dealerCard = card;
      if (usedCards.some((uc) => uc.suit === suit && uc.rank === rank)) {
        await message.channel.send(
          "This card has already been used. Please choose a different card."
        );
        return;
      }

      deck = removeCard(deck, dealerCard);
      usedCards.push(dealerCard);

      const { lowerProb, higherProb } = calculateProbabilities(
        deck,
        dealerCard
      );
      await message.channel.send(
        `Based on dealer's card: Lower: ${(lowerProb * 100).toFixed(
          2
        )}%, Higher: ${(higherProb * 100).toFixed(2)}%`
      );
      await message.channel.send(
        `Cards that have been used so far:\n${displayUniqueUsedCards(
          usedCards
        )}`
      );
      await message.channel.send(
        "Enter `!player <suit> <rank>` to continue the game."
      );

      if (deck.length === 0) {
        await message.channel.send("No more cards left in the deck!");
      }
    }

    if (message.content.toLowerCase().startsWith("!player")) {
      if (!dealerCard) {
        await message.channel.send("Please deal the Dealer's card first.");
        return;
      }

      if (usedCards.some((uc) => uc.suit === suit && uc.rank === rank)) {
        await message.channel.send(
          "This card has already been used. Please choose a different card."
        );
        return;
      }

      deck = removeCard(deck, card);
      usedCards.push(card);

      const result = compareRanks(dealerCard, card);
      if (result === "Tie") {
        await message.channel.send(
          `It's a tie! Both Dealer and Player drew ${card.rank}.`
        );
        lastPlayerCard = card;
        dealerCard = card;
      } else {
        await message.channel.send(`${result} wins this round!`);
        lastPlayerCard = card;
        dealerCard = card;
      }

      await message.channel.send(
        `Cards that have been used so far:\n${displayUniqueUsedCards(
          usedCards
        )}`
      );

      const { lowerProb, higherProb } = calculateProbabilities(
        deck,
        dealerCard
      );
      await message.channel.send(
        `Updated probabilities: Lower: ${(lowerProb * 100).toFixed(
          2
        )}%, Higher: ${(higherProb * 100).toFixed(2)}%`
      );
      await message.channel.send(
        "Enter `!player <suit> <rank>` to continue the game."
      );

      if (deck.length === 0) {
        await message.channel.send("No more cards left in the deck!");
      }
    }
  }
});

client.login(TOKEN);
