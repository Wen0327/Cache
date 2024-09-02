import discord
import os
import requests
import cv2
import numpy as np
import io
from PIL import Image
from dotenv import load_dotenv
import random

# Load Discord Bot Token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Initialize Discord client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Dictionary to store the last image URL for each user
user_last_image_url = {}

# Function to generate a random odd number between 6533 and 6199
def get_random_odd_number():
    res = random.choice([i for i in range(6199, 6534)])
    print(res)
    return res

# Function to apply a mosaic (pixelated) effect
def apply_mosaic(img_array, mosaic_scale=0.1):
    # Get the dimensions of the image
    height, width = img_array.shape[:2]
    
    # Resize the image to a smaller size
    small_img = cv2.resize(img_array, (int(width * mosaic_scale), int(height * mosaic_scale)), interpolation=cv2.INTER_LINEAR)
    
    # Scale the image back up to original size
    mosaic_img = cv2.resize(small_img, (width, height), interpolation=cv2.INTER_NEAREST)
    
    return mosaic_img

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

    # Handle !start command
    if message.content.lower() == '!start':
        random_number = get_random_odd_number()
        image_url = f'https://dic.xflag.com/monsterstrike/assets-update/img/monster/{random_number}/character.webp'
        user_last_image_url[user_id] = image_url  # Store the URL for the user

        try:
            # Download the image
            response = requests.get(image_url)
            img_data = response.content
            img_array = np.array(Image.open(io.BytesIO(img_data)))

            # Apply mosaic effect (pixelation)
            mosaic_img = apply_mosaic(img_array, mosaic_scale=0.07)  # Adjust mosaic_scale to control pixel size

            # Convert the processed image back to PIL format
            pil_img = Image.fromarray(mosaic_img)

            # Save the image to a byte stream
            img_byte_arr = io.BytesIO()
            pil_img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)

            # Send the pixelated image as a file back to Discord
            await message.channel.send(file=discord.File(fp=img_byte_arr, filename='mosaic_image.png'))

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

client.run(TOKEN)
