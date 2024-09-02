import discord
import os
import requests
import cv2
import numpy as np
import io
from PIL import Image
from dotenv import load_dotenv
import random
import json

# Load Discord Bot Token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Load character names mapping
with open('monster.json', 'r') as file:
    character_names_mapping = json.load(file)

# Initialize Discord client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Dictionary to store the last image URL for each user
user_last_image_url = {}
# Dictionary to store the number of games played by each user
user_game_count = {}
# Dictionary to store the URLs played by each user
user_played_urls = {}

# Function to generate a random odd number between 6533 and 6199
def get_random_odd_number():
    res = random.choice([i for i in range(6199, 6534)])
    print(res)
    return res

# Function to apply a mosaic (pixelated) and blur effect
def apply_mosaic_and_blur(img_array, mosaic_scale=0.04, blur_ksize=(5, 5)):
    # Get the dimensions of the image
    height, width = img_array.shape[:2]
    
    # Resize the image to a smaller size to create a mosaic effect
    small_img = cv2.resize(img_array, (int(width * mosaic_scale), int(height * mosaic_scale)), interpolation=cv2.INTER_LINEAR)
    
    # Scale the image back up to original size
    mosaic_img = cv2.resize(small_img, (width, height), interpolation=cv2.INTER_NEAREST)
    
    # Apply Gaussian blur to the mosaic image
    blurred_mosaic_img = cv2.GaussianBlur(mosaic_img, blur_ksize, 0)
    
    return blurred_mosaic_img

# Bot startup event
@client.event
async def on_ready():
    print(f'Logged in as {client.user}!')

# Message handling event
@client.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id

    # Initialize user's game count and played URLs if not already initialized
    if user_id not in user_game_count:
        user_game_count[user_id] = 0
    if user_id not in user_played_urls:
        user_played_urls[user_id] = set()

    # Handle !start command
    if message.content.lower() == '!start':
        # Generate a unique image URL that the user has not played yet
        while True:
            random_number = get_random_odd_number()
            image_url = f'https://dic.xflag.com/monsterstrike/assets-update/img/monster/{random_number}/character.webp'
            if image_url not in user_played_urls[user_id]:
                user_last_image_url[user_id] = image_url
                user_played_urls[user_id].add(image_url)
                break

        # Increment the user's game count
        user_game_count[user_id] += 1
        games_played = user_game_count[user_id]

        # Adjust difficulty based on the number of games played
        difficulty_multiplier = 1 + (games_played // 10) * 0.1
        mosaic_scale = max(0.02, 0.04 / difficulty_multiplier)  # Decrease mosaic scale (increase difficulty)
        blur_ksize = (min(15, int(7 * difficulty_multiplier)), min(15, int(7 * difficulty_multiplier)))  # Increase blur kernel size

        try:
            # Download the image
            response = requests.get(image_url)
            img_data = response.content
            img_array = np.array(Image.open(io.BytesIO(img_data)))

            # Apply mosaic and blur effect with adjusted difficulty
            mosaic_blur_img = apply_mosaic_and_blur(img_array, mosaic_scale=mosaic_scale, blur_ksize=blur_ksize)

            # Convert the processed image back to PIL format
            pil_img = Image.fromarray(mosaic_blur_img)

            # Save the image to a byte stream
            img_byte_arr = io.BytesIO()
            pil_img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)

            # Send the pixelated and blurred image as a file back to Discord
            await message.channel.send(f"Round: {games_played} !")
            await message.channel.send(file=discord.File(fp=img_byte_arr, filename='mosaic_blur_image.png'))

        except Exception as e:
            await message.channel.send(f"Error: {str(e)}")

    # Handle !giveup command
    elif message.content.lower() == '!giveup':
        if user_id in user_last_image_url:
            # Send the original image URL
            await message.channel.send(f"Answer: {user_last_image_url[user_id]}")
        else:
            # Notify the user that they haven't started a game yet
            await message.channel.send("還沒開始就認輸喔==")

    # Handle !reset command
    elif message.content.lower() == '!reset':
        if user_id in user_game_count:
            # Reset the game count and last image URL
            user_game_count[user_id] = 0
            user_last_image_url.pop(user_id, None)
            await message.channel.send("Game has been reset!")
        else:
            await message.channel.send("You haven't started any game yet!")

    # Handle !guess <character name> command
    elif message.content.lower().startswith('!guess '):
        guess = message.content[7:].strip()
        if user_id in user_last_image_url:
            correct_name = character_names_mapping.get(user_last_image_url[user_id], None)
            if correct_name and guess.lower() == correct_name.lower():
                await message.channel.send("Correct!")
            else:
                await message.channel.send("Incorrect!")
        else:
            await message.channel.send("You haven't started a game yet!")

client.run(TOKEN)
