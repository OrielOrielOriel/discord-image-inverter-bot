import discord, io, requests
from PIL import Image, ImageOps

BOT_TOKEN = ''

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

client = discord.Client(intents=intents)

def resolve_format(content_type: str) -> str:
    match content_type:
        case "image/jpeg":
            return 'jpeg'
        case "image/png":
            return 'png'

    return ''

def invert_image(file, target, format):
    i = Image.open(io.BytesIO(file))
    inverted_image = ImageOps.invert(i)

    inverted_image.save(target, format=format)
    target.seek(0)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_raw_reaction_add(payload):
    if not payload.emoji.name == 'invert':
        return

    channel = await client.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    user = await client.fetch_user(payload.user_id)

    if message.attachments:
        f_raw = await message.attachments[0].read()
        f_type = resolve_format(message.attachments[0].content_type)
        f_name = 'inverted_' + message.attachments[0].filename
        f_inverted = io.BytesIO()

        invert_image(f_raw, f_inverted, f_type)

        dm_payload = discord.File(f_inverted, f_name)
        await user.send(file=dm_payload)

    elif message.embeds:
        f_url = message.embeds[0].image.url
        r = requests.get(f_url)

        f_raw = r.content
        f_type = resolve_format(r.headers['content-type'])
        f_name = 'inverted.' + f_type
        f_inverted = io.BytesIO()

        invert_image(f_raw, f_inverted, f_type)

        dm_payload = discord.File(f_inverted, f_name)
        await user.send(file=dm_payload)

    return

client.run(BOT_TOKEN)
