import discord
from discord.ext import commands, tasks
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option
import json
import requests
import io
from PIL import Image

with open("configuracion.json") as f:
    config = json.load(f)

bot = commands.Bot(command_prefix='!', description="ayuda bot")
slash = SlashCommand(bot, sync_commands=True)  # sync_commands=True para registrar automáticamente los comandos slash

@slash.slash(name="casco",
             description="Genera una imagen de avatar con un casco.",
             options=[
                 create_option(name="keko", description="Nombre del keko", option_type=3, required=True),
                 create_option(name="color", description="Color del casco", option_type=3, required=True,
                               choices=[
                                   {"name": "Amarillo", "value": "amarillo"},
                                   {"name": "Azul", "value": "azul"},
                                   {"name": "Rojo", "value": "rojo"},
                                   {"name": "Verde", "value": "verde"}
                               ])
             ])
async def slash_casco(ctx: SlashContext, keko: str, color: str):
    await ctx.defer()
    

    try:
        response = requests.get(f"https://www.habbo.es/api/public/users?name={keko}")
        response.raise_for_status()

        habbo = response.json()['figureString']

        url = "https://www.habbo.com/habbo-imaging/avatarimage?figure="+ habbo +"&action=none&direction=2&head_direction=2&gesture=std&size=m"
        img1 = Image.open(io.BytesIO(requests.get(url).content))
        img1 = img1.resize((64, 110), Image.ANTIALIAS)

        img2 = img1.copy()

        # Cargar la segunda imagen del casco en grande
        casco_grande = Image.open(r"imagenes_cascos/casco_"+color+".png").convert("RGBA") 
        casco_grande = casco_grande.resize((35, 36), Image.ANTIALIAS)

        # Posiciona la segunda imagen del casco en la imagen del avatar
        img1.paste(casco_grande, (13, 18), mask=casco_grande)

        # Guarda y envía la imagen combinada
        with io.BytesIO() as image_binary:
            img1.save(image_binary, 'PNG')
            image_binary.seek(0)

            await ctx.send(file=discord.File(fp=image_binary, filename='keko.png'))
    except requests.HTTPError as e:
        await ctx.send(f"No se encontró el keko {keko}.")
    except Exception as e:
        print(f"Error: {e}")
        await ctx.send("Se produjo un error al procesar la solicitud.")

@bot.event
async def on_ready():
    print("BOT listo!")

bot.run(config["tokendiscord"])
