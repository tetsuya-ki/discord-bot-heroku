import discord
from discord.ext import commands # Bot Commands Frameworkのインポート
import datetime
from .modules import settings

# コグとして用いるクラスを定義。
class EventCog(commands.Cog):

    # EventCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    def __init__(self, bot):
        self.bot = bot

    # リアクション追加時に実行されるイベントハンドラを定義
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.member.bot:# BOTアカウントは無視する
            return
        await self.pin_message(payload)
        await self.reaction_channeler(payload)

    # リアクション削除時に実行されるイベントハンドラを定義
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if member.bot:# BOTアカウントは無視する
            return
        await self.unpin_message(payload)

    # ピン留めする非同期関数を定義
    async def pin_message(self, payload: discord.RawReactionActionEvent):
        # 絵文字が異なる場合は対応しない
        if (payload.emoji.name != '📌') and (payload.emoji.name != '📍'):
            return
        if (payload.emoji.name == '📌') or (payload.emoji.name == '📍'):
            guild = self.bot.get_guild(payload.guild_id)
            channel = guild.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            await message.pin()
            return

    # ピン留め解除する非同期関数を定義
    async def unpin_message(self, payload: discord.RawReactionActionEvent):
        # 絵文字が異なる場合は対応しない
        if (payload.emoji.name != '📌') and (payload.emoji.name != '📍'):
            return
        if (payload.emoji.name == '📌') or (payload.emoji.name == '📍'):
            guild = self.bot.get_guild(payload.guild_id)
            channel = guild.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            await message.unpin()
            return


    # あれする非同期関数を定義
    async def reaction_channeler(self, payload: discord.RawReactionActionEvent):
        # 絵文字が異なる場合は対応しない
        if ((payload.emoji.name != '💯') and (payload.emoji.name != '🔔') and payload.emoji.name != '🏁'):
            return

        if ((payload.emoji.name == '💯') or (payload.emoji.name == '🔔') or (payload.emoji.name == '🏁')):
            guild = self.bot.get_guild(payload.guild_id)
            from_channel = guild.get_channel(payload.channel_id)
            message = await from_channel.fetch_message(payload.message_id)

            if settings.IS_DEBUG:
                print("guild:"+ str(guild))
                print("from_channel: "+ str(from_channel))
                print("message: " + str(message))

            contents = [message.clean_content[i: i+200] for i in range(0, len(message.clean_content), 200)]
            if len(contents) != 1 :
                contents[0] += " ＊長いので分割しました＊"
            embed = discord.Embed(title = contents[0], description = "<#" + str(message.channel.id) + ">", type="rich")
            embed.set_author(name=payload.emoji.name + ":reaction_channeler", url="https://github.com/tetsuya-ki/discord-bot-heroku/")
            embed.set_thumbnail(url=message.author.avatar_url)

            created_at = message.created_at.replace(tzinfo=datetime.timezone.utc)
            created_at_jst = created_at.astimezone(datetime.timezone(datetime.timedelta(hours=9)))

            embed.add_field(name="作成日時", value=created_at_jst.strftime('%Y/%m/%d(%a) %H:%M:%S'))

            if len(contents) != 1 :
                for addText in contents[1:]:
                    embed.add_field(name="addText", value=addText + " ＊長いので分割しました＊", inline=False)

        if (payload.emoji.name == '🔔'):
            to_channel = guild.get_channel(settings.REACTION_CHANNELER_BELL)
            if settings.IS_DEBUG:
                print("setting:"+str(settings.REACTION_CHANNELER_BELL))
                print("to_channel: "+str(to_channel))

            await to_channel.send("news: " + message.jump_url, embed=embed)
            return

        if (payload.emoji.name == '🏁'):
            to_channel = guild.get_channel(settings.REACTION_CHANNELER_FLAG)
            await to_channel.send("general: " + message.jump_url, embed=embed)
            return

        if (payload.emoji.name == '💯'):
            to_channel = guild.get_channel(settings.REACTION_CHANNELER_100)
            await to_channel.send("★注目★: " + message.jump_url, embed=embed)
            return

# Bot本体側からコグを読み込む際に呼び出される関数。
def setup(bot):
    bot.add_cog(EventCog(bot)) # TestCogにBotを渡してインスタンス化し、Botにコグとして登録する