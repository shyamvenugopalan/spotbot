# bot.py
import os
import re
import discord
from discord import channel
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from discord.ext import commands
from dotenv import load_dotenv

MESSAGE_LIMIT = 5000
PLAYLIST_LIMIT = 500

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
PLAYLIST_ID = os.getenv('PLAYLIST_ID')

bot = discord.ext.commands.Bot(command_prefix='!')

@bot.command(name='build', help='Builds Playlist from previous messages.')
async def build(ctx):
    await ctx.send('🤖: Building Playlist!')

    scope = ["playlist-modify-public","playlist-modify-private"]
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    current_track_list = []
    playlist = sp.playlist_items(PLAYLIST_ID)
    for item in playlist["items"]:
        current_track_list.append(item['track']['id'])

    def is_spotify_track_link(message):
        if len(message.content) == 0:
            return False
        if 'spotify.com/track' in message.content:
            return True
        else:
            return False

    def get_track_id(message):
        id = str(re.search(".*spotify\.com\/track\/([\w-]{22}).*", message.content).group(1))
        return id

    count = 0
    async for msg in ctx.channel.history(limit=MESSAGE_LIMIT):
        if msg.author != ctx.bot.user:
            if is_spotify_track_link(msg):
                id = get_track_id(msg)
                if id not in current_track_list:
                    count = count+1
                    print(f'Adding track: {id}')
                    sp.playlist_add_items(PLAYLIST_ID, [id])
                else:
                    print(f'Skipping track: {id}')
                # await ctx.send(f'🤖: Found Link {msg.content}')
            if count == PLAYLIST_LIMIT:
                break
    await ctx.send(f'🤖: Added {count} new tracks')
    await ctx.send(f'🤖: Playlist Link https://open.spotify.com/playlist/{PLAYLIST_ID}')

bot.run(TOKEN)