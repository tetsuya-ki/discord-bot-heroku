import discord
import settings
import datetime

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

# ピン留めする非同期関数を定義
async def pin_message(payload):
    # 絵文字が異なる場合は対応しない
    if (payload.emoji.name != '📌') and (payload.emoji.name != '📍'):
        return
    if (payload.emoji.name == '📌') or (payload.emoji.name == '📍'):
        channel = client.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        await message.pin()
        return

# ピン留め解除する非同期関数を定義
async def unpin_message(payload):
    # 絵文字が異なる場合は対応しない
    if (payload.emoji.name != '📌') and (payload.emoji.name != '📍'):
        return
    if (payload.emoji.name == '📌') or (payload.emoji.name == '📍'):
        channel = client.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        await message.unpin()
        return


# あれする非同期関数を定義
async def reaction_channeler(payload):
    # 絵文字が異なる場合は対応しない
    if ((payload.emoji.name != '💯') and (payload.emoji.name != '🔔') and payload.emoji.name != '🏁'):
        return

    if ((payload.emoji.name == '💯') or (payload.emoji.name == '🔔') or (payload.emoji.name == '🏁')):
        from_channel = client.get_channel(payload.channel_id)
        message = await from_channel.fetch_message(payload.message_id)

        embed = discord.Embed(title = message.content, description = "<#" + str(message.channel.id) + ">", type="rich")
        embed.set_author(name=payload.emoji.name + ":reaction_channeler", url="https://github.com/tetsuya-ki/discord-bot-heroku/blob/master/bot.py")
        embed.set_thumbnail(url=message.author.avatar_url)

        created_at = message.created_at.replace(tzinfo=datetime.timezone.utc)
        created_at_jst = created_at.astimezone(datetime.timezone(datetime.timedelta(hours=9)))

        embed.add_field(name="作成日時", value=created_at_jst.strftime('%Y/%m/%d(%a) %H:%M:%S'))

    if (payload.emoji.name == '🔔'):
        to_channel = client.get_channel(settings.REACTION_CHANNELER_BELL)
        await to_channel.send("news: " + message.jump_url, embed=embed)
        return

    if (payload.emoji.name == '🏁'):
        to_channel = client.get_channel(settings.REACTION_CHANNELER_FLAG)
        await to_channel.send("general: " + message.jump_url, embed=embed)
        return

    if (payload.emoji.name == '💯'):
        to_channel = client.get_channel(settings.REACTION_CHANNELER_100)
        await to_channel.send("★注目★: " + message.jump_url, embed=embed)
        return

# リアクション追加時に実行されるイベントハンドラを定義
@client.event
async def on_raw_reaction_add(payload):
    await pin_message(payload)
    await reaction_channeler(payload)

# リアクション削除時に実行されるイベントハンドラを定義
@client.event
async def on_raw_reaction_remove(payload):
    await unpin_message(payload)

# メッセージ送付時に実行されるイベントハンドラを定義
@client.event
async def on_message(message):
    # BOTだったらなにもしない
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

client.run(settings.DISCORD_TOKEN)