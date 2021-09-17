import os # Library of the operating system
import discord # Library of the API discord.py
from music import *
from keep_awake import keep_alive

client = discord.Client() # Instance of a Client. This client is our connection to Discord.
my_secret = os.environ['TOKEN'] # TOKEN of PolloBot

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    aux = message.content.lower() # To make the message all in lowercase
    if message.author == client.user:
        return

    if aux == 'oscar' or aux == 'juan carlos':
        await message.channel.send('Chupapijas')

    elif aux == 'elias':
        await message.channel.send('Mi economia se basa en talar arboles')
    
    elif aux == 'adryh' or aux == 'adri' or aux == 'rodri':
        await message.channel.send('Dios supremo del Papá Pollo')
    
    elif aux == 'fer' or aux == 'keor98' or aux == 'keor94':
        await message.channel.send('Siempre me encuentro a la gente de espalda GG WP EZ')

keep_alive()

client.run(my_secret)