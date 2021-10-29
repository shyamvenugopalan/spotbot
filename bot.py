# bot.py
import os
import re
import discord
import spotipy
import logging

from logging.handlers import RotatingFileHandler
from spotipy.oauth2 import SpotifyOAuth
from discord.ext import commands
from dotenv import load_dotenv

MESSAGE_LIMIT = 5000 # Limit for searching message history in channel
PLAYLIST_LIMIT = 500 # Limit for adding new songs to playlist

# Logging configs
logger = logging.getLogger("spotbot")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler("spotbot.log", mode='a', maxBytes=50000000, backupCount=5, encoding='utf-8', delay=0) #50000000Bytes ~ 50MB
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

'''
Create .env file in the same directory and set the following environment variables.
DISCORD_TOKEN='<your discord token>'
DISCORD_GUILD='<your discord guild>'
SPOTIPY_CLIENT_ID='<spotify client id>'
SPOTIPY_CLIENT_SECRET='<spotify client id>'
SPOTIPY_REDIRECT_URI='http://localhost:9090'
PLAYLIST_ID='<your playlist id>'
LOG_FILE=''
'''
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
PLAYLIST_ID = os.getenv('PLAYLIST_ID')

bot = discord.ext.commands.Bot(command_prefix='!')

@bot.command(name='build', help='Builds playlist from previous messages in channel.')
async def build(ctx):
    logger.info(f"build playlist called by {ctx.author}")
    await ctx.send('🤖: Building Playlist!')

    scope = ["playlist-modify-public","playlist-modify-private"]
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    current_track_list = []
    playlist = sp.playlist_items(PLAYLIST_ID)
    for item in playlist["items"]:
        current_track_list.append(item['track']['id']) #get list of tracks already in playlist
    logger.info(f"playlist contains {len(current_track_list)} tracks")
    def is_spotify_track_link(message):
        if len(message.content) == 0:
            return False
        if 'spotify.com/track' in message.content:
            return True
        else:
            return False

    def get_track_ids(message):
        return re.findall(r'.spotify\.com\/track\/([\w-]{22}).', message.content)

    count = 0
    async for msg in ctx.channel.history(limit=MESSAGE_LIMIT, oldest_first=True):
        if msg.author != ctx.bot.user:
            if is_spotify_track_link(msg):
                ids = get_track_ids(msg)
                for id in ids:
                    if id not in current_track_list:
                        count = count+1
                        logger.info(f'Adding track: {id}')
                        sp.playlist_add_items(PLAYLIST_ID, [id], position=0)
                    else:
                        logger.info(f'Skipping track: {id}')
                    # await ctx.send(f'🤖: Found Link {msg.content}')
            if count >= PLAYLIST_LIMIT:
                break
    logger.info(f'Added {count} new tracks')
    await ctx.send(f'🤖: Added {count} new tracks')
    await ctx.send(f'🤖: Playlist Link https://open.spotify.com/playlist/{PLAYLIST_ID}')

bot.run(TOKEN)