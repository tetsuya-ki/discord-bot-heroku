import discord
import datetime
import asyncio
import aiohttp
from discord.ext import commands  # Bot Commands Frameworkのインポート
from discord import app_commands
from discord import Webhook
from logging import getLogger
from typing import Literal
from .modules.reactionchannel import ReactionChannel
from .modules import settings
from .onmessagecog import OnMessageCog

LOG = getLogger('assistantbot')

# コグとして用いるクラスを定義。
class ReactionChannelerCog(commands.Cog, name="リアクションチャンネラー"):
    """
    リアクションチャンネラー機能のカテゴリ(リアクションをもとに実行するアクション含む)。
    """
    SPLIT_SIZE = 1900
    TIMEOUT_TIME = 30.0
    SHOW_ME = '自分のみ'
    SHOW_ALL = '全員に見せる'

    # ReactionChannelerCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    def __init__(self, bot):
        self.bot = bot
        self.reaction_channel = None
        self.onmessagecog = None

    # cogが準備できたら読み込みする
    @commands.Cog.listener()
    async def on_ready(self):
        LOG.info(f"load reaction-channeler's guilds{self.bot.guilds}")
        self.reaction_channel = ReactionChannel(self.bot.guilds, self.bot)
        await self.reaction_channel.get_discord_attachment_file()
        self.onmessagecog = OnMessageCog(self.bot)

    # リアクションチャンネラーコマンド群
    reaction_channeler = app_commands.Group(name="reaction-channeler", description='リアクションチャンネラーを操作するコマンド（サブコマンド必須）')
    """
    リアクションチャンネラーを管理するコマンド群です。このコマンドだけでは管理できません。半角スペースの後、続けて以下のサブコマンドを入力ください。
    - リアクションチャンネラーを追加したい場合は、`add`を入力し、絵文字とチャンネル名を指定してください。
    - リアクションチャンネラーを削除したい場合は、`delete`を入力し、絵文字とチャンネル名を指定してください。
    - リアクションチャンネラーを**全て**削除したい場合は、`purge`を入力してください。
    - リアクションチャンネラーを確認したい場合は、`list`を入力してください。
    """

    # リアクションチャンネラー追加
    @reaction_channeler.command(
        name='add',
        description='リアクションチャンネラーを追加するサブコマンド')
    @app_commands.describe(
        reaction='リアクションしたらチャンネルに投稿する絵文字')
    @app_commands.describe(
        channel='投稿先のチャンネル(Webhookを利用する場合は未指定とすること)')
    @app_commands.describe(
        webhook_url='WebhookのURL')
    async def add(self,
                interaction: discord.Interaction,
                reaction: str,
                channel: discord.TextChannel = None,
                webhook_url: str = None):
        """
        リアクションチャンネラー（＊）で反応する絵文字を追加します。
        ＊指定した絵文字でリアクションされた時、チャンネルに通知する機能のこと
        """
        # Webhook URL、チャンネルがない場合は実施不可
        if webhook_url is None and channel is None:
            await interaction.response.send_message('チャンネルかWebhook URLを指定してください', ephemeral=True)
            return
        msg = await self.reaction_channel.add(interaction, reaction, channel, webhook_url)
        await interaction.response.send_message(msg, ephemeral=False)

    # リアクションチャンネラー確認
    @reaction_channeler.command(
        name='list',
        description='現在登録されているリアクションチャンネラーを確認するサブコマンド')
    @app_commands.describe(
        reply_is_hidden='Botの実行結果を全員に見せるどうか(デフォルトは全員に見せる)')
    async def list(self,
                interaction: discord.Interaction,
                reply_is_hidden: Literal['自分のみ', '全員に見せる'] = SHOW_ME):
        """
        リアクションチャンネラー（＊）で反応する絵文字とチャンネルのリストを表示します。
        ＊指定した絵文字でリアクションされた時、チャンネルに通知する機能のこと
        """
        hidden = True if reply_is_hidden == self.SHOW_ME else False
        msg = await self.reaction_channel.list(interaction)
        await interaction.response.send_message(msg, ephemeral=hidden)

    # リアクションチャンネラー全削除
    @reaction_channeler.command(
        name='purge',
        description='Guildのリアクションチャンネラーを全削除するサブコマンド')
    async def purge(self,
                interaction: discord.Interaction):
        """
        リアクションチャンネラー（＊）で反応する絵文字を全て削除します。
        30秒以内に👌(ok_hand)のリアクションをつけないと実行されませんので、素早く対応ください。
        ＊指定した絵文字でリアクションされた時、チャンネルに通知する機能のこと
        """
        command_author = interaction.user
        # 念の為、確認する
        confirm_text = f'全てのリアクションチャンネラーを削除しますか？\n 問題ない場合、30秒以内に👌(ok_hand)のリアクションをつけてください。'
        confirm_msg = await interaction.channel.send(confirm_text)
        await interaction.response.send_message(f'リアククションチャンネラー削除中です。チャンネルを確認してください。\n{confirm_msg.jump_url}', ephemeral=True)

        def check(reaction, user):
            return user == command_author and str(reaction.emoji) == '👌'

        # リアクション待ち
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=self.TIMEOUT_TIME, check=check)
        except asyncio.TimeoutError:
            await confirm_msg.reply('→リアクションがなかったので、リアクションチャンネラーの全削除をキャンセルしました！')
        else:
            msg = await self.reaction_channel.purge(interaction)
            await confirm_msg.reply(msg)

    # リアクションチャンネラー削除（１種類）
    @reaction_channeler.command(
        name='remove',
        description='リアクションチャンネラーを削除するサブコマンド')
    @app_commands.describe(
        reaction='リアクションしたらチャンネルに投稿する絵文字(削除対象)')
    @app_commands.describe(
        channel='投稿先のチャンネル(Webhookを利用する場合は未指定とすること)')
    @app_commands.describe(
        webhook_url='WebhookのURL')
    async def delete(self,
                interaction: discord.Interaction,
                reaction: str,
                channel: discord.TextChannel = None,
                webhook_url: str = None):
        """
        リアクションチャンネラー（＊）で反応する絵文字、チャンネルの組み合わせを削除します
        絵文字、チャンネルの記載が必須です。存在しない組み合わせを消す場合でもエラーにはなりません
        ＊指定した絵文字でリアクションされた時、チャンネルに通知する機能のこと
        """
        # Webhook URL、チャンネルがない場合は実施不可
        if webhook_url is None and channel is None:
            await interaction.response.send_message('チャンネルかWebhook URLを指定してください', ephemeral=True)
            return

        msg = await self.reaction_channel.delete(interaction, reaction, channel, webhook_url)
        await interaction.response.send_message(msg, ephemeral=False)

    # リアクション追加時に実行されるイベントハンドラを定義
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        loop = asyncio.get_event_loop()
        if payload.member.bot:# BOTアカウントは無視する
            return
        if payload.emoji.name == '👌':# ok_handは確認に使っているので無視する(と思っていたが別機能として使用)
            await self.save_file(payload)
            return
        await self.pin_message(payload)
        await self.reaction_to_send_channel(payload)

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
            await message.reply('ピン留めが解除されました', mention_author=False)

            return

    # リアクションをもとにチャンネルへ投稿する非同期関数を定義
    async def reaction_to_send_channel(self, payload: discord.RawReactionActionEvent):
        # リアクションチャンネラーを読み込む
        guild = self.bot.get_guild(payload.guild_id)
        await self.reaction_channel.set_rc(guild)

        # リアクションから絵文字を取り出す（ギルド絵文字への変換も行う）
        emoji = payload.emoji.name
        if payload.emoji.id is not None:
            emoji = f'<:{payload.emoji.name}:{payload.emoji.id}>'

        # 入力された絵文字でフィルターされたリストを生成する
        filtered_list = [rc for rc in self.reaction_channel.guild_reaction_channels if emoji in rc]

        LOG.debug(f'*****emoji***** {emoji}')

        # フィルターされたリストがある分だけ、チャンネルへ投稿する
        for reaction in filtered_list:
            from_channel = guild.get_channel(payload.channel_id)
            message = await from_channel.fetch_message(payload.message_id)

            LOG.debug('guild:'+ str(guild))
            LOG.debug('from_channel: '+ str(from_channel))
            LOG.debug('message: ' + str(message))

            # 設定によって、すでに登録されたリアクションは無視する
            if settings.FIRST_REACTION_CHECK:
                LOG.debug('reactions:'+ str(message.reactions))
                LOG.debug('reactions_type_count:'+ str(len(message.reactions)))
                for message_reaction in message.reactions:
                    if emoji == str(message_reaction) and message_reaction.count > 1:
                        LOG.debug('Already reaction added. emoji_count:'+ str(message_reaction.count))
                        return

            contents = [message.clean_content[i: i+1980] for i in range(0, len(message.clean_content), 1980)]
            if len(contents) == 0:
                return
            elif len(contents) > 1:
                contents[0] += ' ＊長いので分割しました＊'

            # 画像を設定
            img_url = None
            for embed in message.embeds:
                if embed.image.url:
                    img_url = embed.image.url
                    break
                dicted_data = embed.to_dict()
                if 'thumbnail' in dicted_data and 'url' in dicted_data['thumbnail']:
                    img_url = dicted_data['thumbnail']['url']
                    break

            is_webhook = False
            channel = ''
            # Webhookの場合
            if reaction[2] == '':
                is_webhook = True
                channel = f'{message.guild.name} / #{message.channel.name}'
            else:
                channel = f'<#{message.channel.id}>'

            embed = discord.Embed(description = contents[0], type='rich')
            embed.set_author(name=reaction[0] + ' :reaction_channeler', url='https://github.com/tetsuya-ki/discord-bot-heroku/')
            embed.set_thumbnail(url=message.author.display_avatar)
            if img_url is not None:
                embed.set_image(url=img_url)

            created_at = message.created_at.replace(tzinfo=datetime.timezone.utc)
            created_at_jst = created_at.astimezone(datetime.timezone(datetime.timedelta(hours=9)))

            embed.add_field(name='作成日時', value=created_at_jst.strftime('%Y/%m/%d(%a) %H:%M:%S'))
            embed.add_field(name='元のチャンネル', value=channel)

            if len(contents) != 1 :
                embed.set_footer(text=contents[1] + ' ＊長いので分割しました(以降省略)＊')

            # リアクションチャンネラーがWebhookだった場合の処理
            if is_webhook and '※' not in reaction[1]:
                async with aiohttp.ClientSession() as session:
                    webhook = Webhook.from_url(reaction[1], session=session)
                    try:
                        await webhook.send('ReactionChanneler(Webhook): ' + message.jump_url, embed=embed, username='ReactionChanneler', avatar_url=message.author.display_avatar)
                    except (discord.HTTPException,discord.NotFound,discord.Forbidden,discord.InvalidArgument) as e:
                        LOG.error(e)
            elif '※' in reaction[1]:
                LOG.info('環境変数に登録されていないWebhookIDをもつWebhookのため、実行されませんでした。')
            # 通常のリアクションチャンネラー機能の実行
            else:
                to_channel = guild.get_channel(int(reaction[2]))
                LOG.debug('setting:'+str(reaction[2]))
                LOG.debug('to_channel: '+str(to_channel))
                await to_channel.send(reaction[1] + ': ' + message.jump_url, embed=embed)

    # 画像を保存
    async def save_file(self, payload: discord.RawReactionActionEvent):
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        await self.onmessagecog.save_message_file(message)

# Bot本体側からコグを読み込む際に呼び出される関数。
async def setup(bot):
    await bot.add_cog(ReactionChannelerCog(bot)) # ReactionChannelerCogにBotを渡してインスタンス化し、Botにコグとして登録する