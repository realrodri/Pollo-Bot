import os # Library of the operating system
import discord # Library of the API discord.py
from discord.ext import commands
from keep_awake import keep_alive

bot = commands.Bot(command_prefix = '!')

cogs = ["cogs.music"]


@bot.event
async def on_ready():
	print("The bot is ready!")                # The bot sends this when it's ready, there isn't really need of it, but looks good in the terminal
	print("Loading cogs . . .")               # This again, no actual need, but looks in the terminal
	for cog in cogs:                          # Now, we iterate through the "cogs" list we created up there
		try:                                  # we put up a "try" so it doesn't break the loop when one of the cogs return any error
			bot.load_extension(cog)           # and now, we actually just load the extension
			print(cog + " was loaded.")       # and, again, for terminal's appearance sake, also it would tell you if the cogs got loaded successfully
		except Exception as e:                # now, the "except" part, we simply reference a variable "e" as the Exception(error)
			print(e)                          # and we tell it to print "e" which is actually the Exception i.e. error in the cog

@bot.command()
async def ping(ctx):
	await ctx.send("Pong!!")

#@bot.command()                               # we use the @commands.command() decorator to create commands
#async def name(self, ctx):                        # in a class, the "self" argument is necessary in every single function just like ctx
  #bot_name = self.bot.user.name                 # we use "self.bot" instead of just "bot" as we used to do in main.py
  #await ctx.send(f"My name is {bot_name}")      # You'll see the bot will now return its name 
        
keep_alive()

my_secret = os.environ['TOKEN'] # TOKEN of PolloBot
bot.run(my_secret, reconnect = True, bot = True)


#Rodri code below
#from discord.ext import commands
#import music

#cogs = [music]

#client = commands.Bot(command_prefix='?', intents = discord.Intents.all())
#client.run('ODg4MTI2MDA2NDI5MzcyNDU2.YUOJzA.Z-vHEnjib-OVR6l3KVCMTSwprjo')


#for i in range(len(cogs)):
#    cogs[i].setup(client)

# Fin Rodri code



