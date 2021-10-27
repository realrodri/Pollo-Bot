from discord.ext import commands
import youtube_dl
import pafy
import discord
import asyncio

class music(commands.Cog):                        # we first need to define a class
  def __init__(self, bot):                          # we pass bot in the __init__ function
    self.bot = bot                                # we need to import the bot variable from main.py file so we can use it here
    self.song_queue = {}

    self.setup()

  def setup(self):
      for guild in self.bot.guilds:
          self.song_queue[guild.id] = []

  async def check_queue(self, ctx):
        if len(self.song_queue[ctx.guild.id]) > 0:
            ctx.voice_client.stop()
            await self.play_song(ctx, self.song_queue[ctx.guild.id][0])
            self.song_queue[ctx.guild.id].pop(0)

  async def search_song(self, amount, song, get_url=False):
      info = await self.bot.loop.run_in_executor(None, lambda: youtube_dl.YoutubeDL({"format" : "bestaudio", "quiet" : True}).extract_info(f"ytsearch{amount}:{song}", download=False, ie_key="YoutubeSearch"))
      if len(info["entries"]) == 0: return None

      return [entry["webpage_url"] for entry in info["entries"]] if get_url else info

  async def play_song(self, ctx, song):
      url = pafy.new(song).getbestaudio().url
      ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url)), after=lambda error: self.bot.loop.create_task(self.check_queue(ctx)))
      ctx.voice_client.source.volume = 0.5

  @commands.command(name="play", aliases=['p'], help="Reproduce una canción", pass_context = True)
  async def play(self, ctx, *, song=None):
      if song is None:
          return await ctx.send("Debes incluir una canción para reproducir.")

      if ctx.voice_client is None:
          channel = ctx.message.author.voice.channel
          await channel.connect()

      # handle song where song isn't url
      if not ("youtube.com/watch?" in song or "https://youtu.be/" in song):
          result = await self.search_song(1, song, get_url=True)

          if result is None:
              return await ctx.send("Lo siento, no he podido encontrar la canción indicada, intenta utilizar el comando de búsqueda.")

          song = result[0]

      if ctx.voice_client.source is not None:

          try:
              await self.play_song(ctx, song)
              return await ctx.send(f"Sonando: {song}")
          except:
              self.song_queue[ctx.guild.id].append(song)
              return await ctx.send(f"Añadida a la cola")

      await self.play_song(ctx, song)
      await ctx.send(f"Sonando: {song}")

  @commands.command(name="queue", help="Muestra la cola de canciones.", pass_context = True)
  async def queue(self, ctx): # display the current guilds queue
      if len(self.song_queue[ctx.guild.id]) == 0:
          return await ctx.send("Actualmente no hay canciones en la cola.")

      embed = discord.Embed(title="Song Queue", description="", colour=discord.Colour.dark_gold())
      i = 1
      for url in self.song_queue[ctx.guild.id]:
          embed.description += f"{i}) {url}\n"
          print(url)
          i += 1

      embed.set_footer(text="Disfruta de la música pollil 😎")
      await ctx.send(embed=embed)

  @commands.command(name="skip", help="Inicia una votación para saltar.", pass_context = True)
  async def skip(self, ctx):
      if ctx.voice_client is None:
          return await ctx.send("Actualmente, no hay ninguna canción reproduciéndose.")

      if ctx.author.voice is None:
          return await ctx.send("Me da que no estás conectado a ningún canal de voz, amigo mío.")

      if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
          return await ctx.send("Lo siento, pero debido a un error desconocido, no puedo reproducir canciones ahora mismo. Inténtalo más tarde y si el problema persiste, contacta a mis creadores ):")

      poll = discord.Embed(title=f"Votación de skip de - {ctx.author.name}#{ctx.author.discriminator}", description="**El 80% del canal de voz debe votar a favor para continuar.**", colour=discord.Colour.blue())
      poll.add_field(name="Saltar", value=":white_check_mark:")
      poll.add_field(name="Ignorar", value=":no_entry_sign:")
      poll.set_footer(text="La votación acaba en 15 segundos. ¡Date prisa!")

      poll_msg = await ctx.send(embed=poll) # only returns temporary message, we need to get the cached message to get the reactions
      poll_id = poll_msg.id

      await poll_msg.add_reaction(u"\u2705") # yes
      await poll_msg.add_reaction(u"\U0001F6AB") # no
      
      await asyncio.sleep(15) # 15 seconds to vote

      poll_msg = await ctx.channel.fetch_message(poll_id)
      
      votes = {u"\u2705": 0, u"\U0001F6AB": 0}
      reacted = []

      for reaction in poll_msg.reactions:
          if reaction.emoji in [u"\u2705", u"\U0001F6AB"]:
              async for user in reaction.users():
                  if user.voice.channel.id == ctx.voice_client.channel.id and user.id not in reacted and not user.bot:
                      votes[reaction.emoji] += 1

                      reacted.append(user.id)

      skip = False

      if votes[u"\u2705"] > 0:
          if votes[u"\U0001F6AB"] == 0 or votes[u"\u2705"] / (votes[u"\u2705"] + votes[u"\U0001F6AB"]) > 0.79: # 80% or higher
              skip = True
              embed = discord.Embed(title="Skip satisfactorio", description="***La votación ha salido adelante. Cambiando la canción por la siguiente.***", colour=discord.Colour.green())

      if not skip:
          embed = discord.Embed(title="Skip fallido", description="*La votación para saltar la canción ha fallado ):*\n\n**La votación requiere de al menos el 80% del canal de voz activo para poder saltarla.**", colour=discord.Colour.red())

      embed.set_footer(text="La votación ha terminado. ¡Hasta la siguiente!")

      await poll_msg.clear_reactions()
      await poll_msg.edit(embed=embed)

      if skip:
          ctx.voice_client.stop()
          await self.check_queue(ctx)

  @commands.command(name="fskp", aliases=['fs'], help="Fuerza a skipear la canción.", pass_context = True)
  async def fskip(self, ctx):
      ctx.voice_client.stop()
      await self.check_queue(ctx)

  @commands.command(name="pause", help="Pausa la canción que se reproduce ahora mismo. Pause. Del inglés, pausar. Tampoco tiene mucho.", pass_context = True)
  async def pause(self, ctx):
      if ctx.voice_client.is_paused():
          return await ctx.send("Ya está pausada la música mi rey.")

      ctx.voice_client.pause()
      await ctx.send("La canción actual ha sido parada.")

  @commands.command(name="resume", help="Vuelve a reproducir la canción pausada.", pass_context = True)
  async def resume(self, ctx):
      if ctx.voice_client is None:
          return await ctx.send("No estoy conectado a ningún canal de voz. Me da que va a ser un poco complicado...")

      if not ctx.voice_client.is_paused():
          return await ctx.send("Ya estoy reproduciendo una canción. ¡Se siente! :P")
      
      ctx.voice_client.resume()
      await ctx.send("La canción actual ha sido reproducida de nuevo. No desde el principio, sino donde lo dejaste.")

  @commands.command(name="join", help="Con este comando, metes al bot en el canal de voz en el que te encuentras actualmente.", pass_context = True)
  async def join(self, ctx):
    print("!join")
    if (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        await channel.connect()
        await ctx.send("Que pasa chavales.")
    else:
      await ctx.send("Primero necesitas estar en un canal de voz, amigo mío.")
  
  @commands.command(name="disconnect", aliases=['d'], help="Desconectas al bot del canal actual. Algo que nunca querrías que pasase (o eso espero).", pass_context = True)
  async def disconnect(self, ctx):
    print("!disconnect")
    if (ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        await ctx.send("Ale hasta luego.")
    else:
      await ctx.send("Loco, primero tengo que estar en un canal de voz.")

  @commands.command(name="oscar", help="oscar", pass_context = True)
  async def oscar(self, ctx):
    if ctx.voice_client is None:
          channel = ctx.message.author.voice.channel
          await channel.connect()

    if not ctx.voice_client.is_paused() and ctx.voice_client.source is not None:
          ctx.voice_client.pause()

    result = await self.search_song(1, song = "Tu lo que eres es gilipollas - Ibai Llanos", get_url=True)
    song = result[0]
    await self.play_song(ctx, song)
      


def setup(bot):                                       # we'll have to setup the bot now
	bot.add_cog(music(bot))                       # adding the "blah_blah" class to the bot