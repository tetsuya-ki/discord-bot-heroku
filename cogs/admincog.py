import discord
import datetime
import asyncio
from discord import app_commands
from discord.ext import commands  # Bot Commands Frameworkのインポート
from logging import getLogger, DEBUG
from typing import Literal
from .modules import settings
from .modules.auditlogchannel import AuditLogChannel

LOG = getLogger('assistantbot')

# コグとして用いるクラスを定義。
class AdminCog(commands.Cog):
    """
    管理用の機能です。
    """
    TIMEOUT_TIME = 30.0
    SHOW_ME = '自分のみ'
    SHOW_ALL = '全員に見せる'

    # AdminCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    def __init__(self, bot):
        self.bot = bot
        self.command_author = None
        self.audit_log_channel = AuditLogChannel()

    # 監査ログの取得
    @app_commands.command(
        name='get-audit-log',
        description='監査ログを取得します')
    @app_commands.describe(
        limit_num='指定された場合、新しいものを先頭にその件数だけ取得(未指定の場合はふるいものを先頭に3,000件取得')
    async def getAuditLog(self, interaction: discord.Interaction, limit_num: str=None):
        """
        監査ログを取得します。ただし、とても読みづらい形式です。。。
        引数が未指定の場合、古いものを先頭に3,000件分取得し、チャンネルに投稿します。
        引数が指定された場合、新しいものを先頭に指定された件数取得し、チャンネルに投稿します。
        """
        first_entry_times = 0
        oldest_first_flag = True
        audit_log = 0
        await interaction.response.defer()

        if limit_num is None:
            limit_num = 3000
            oldest_first_flag = True
            first_entry_times = first_entry_times + 1
        elif limit_num.isdecimal():
            limit_num = int(limit_num)
            oldest_first_flag = False

        if await self.audit_log_channel.get_ch(interaction.guild) is False:
            LOG.debug(self.audit_log_channel.alc_err)
            return
        else:
            to_channel = self.audit_log_channel.channel

        start = f'start getAuditLog ({audit_log}回で開始)'

        LOG.debug(f'oldest_first_flag:{oldest_first_flag}')
        LOG.debug(f'limit_num:{limit_num}')
        if (settings.LOG_LEVEL == DEBUG):
            await to_channel.send(start)

        LOG.debug(start)
        first_entry_list = [audit_logs async for audit_logs in  interaction.guild.audit_logs(limit=1, oldest_first=oldest_first_flag)]
        first_entry = first_entry_list[0]

        LOG.debug(f'{audit_log}: (fet:{first_entry_times}) {first_entry}')

        async for entry in interaction.guild.audit_logs(limit=limit_num, oldest_first=oldest_first_flag):
            if first_entry.id == entry.id:
                first_entry_times = first_entry_times + 1

            audit_log = audit_log + 1
            await self.sendAuditLogEntry(to_channel, entry, audit_log)

            LOG.debug(f'{audit_log}: (fet:{first_entry_times}) {entry}')

            if first_entry_times > 1:
                break

        end = f'end getAuditLog ({audit_log}回で終了)'
        if (settings.LOG_LEVEL == DEBUG):
            await to_channel.send(end)
        LOG.debug(end)
        await interaction.followup.send("処理完了", ephemeral=False)

    # 監査ログをチャンネルに送信
    async def sendAuditLogEntry(self, to_channel, entry, audit_log_times):
        created_at = entry.created_at.replace(tzinfo=datetime.timezone.utc)
        created_at_jst = created_at.astimezone(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y/%m/%d(%a) %H:%M:%S')
        msg = '{1}: {0.user} did **{0.action}** to {0.target}'.format(entry, created_at_jst)
        embed = None

        if entry.changes is not None:
            embed = discord.Embed(title = 'entry_changes', description = f'entry.id: {entry.id}, audit_log_times: {audit_log_times}')
            embed.set_author(name='sendAuditLogEntry', url='https://github.com/tetsuya-ki/discord-bot-heroku/')

            if hasattr(entry, 'changes'):
                embed.add_field(name='changes', value=entry.changes)
            if hasattr(entry.changes.after, 'overwrites'):
                embed.add_field(name='after.overwrites', value=entry.changes.after.overwrites)
            if hasattr(entry.changes.before, 'roles'):
                embed.add_field(name='before.roles', value=entry.changes.before.roles)
            if hasattr(entry.changes.after, 'roles'):
                embed.add_field(name='after.roles', value=entry.changes.after.roles)
                LOG.debug(entry.changes.after.roles)
            if hasattr(entry.changes.before, 'channel'):
                embed.add_field(name='before.channel', value=entry.changes.before.channel)
            if hasattr(entry.changes.after, 'channel'):
                embed.add_field(name='after.channel', value=entry.changes.after.channel)

        LOG.debug(msg)
        LOG.debug(entry.changes)

        await to_channel.send(msg, embed=embed)

    # メッセージの削除
    @app_commands.command(
        name='purge',
        description='メッセージを削除します')
    @app_commands.describe(
        limit_num='削除するメッセージの数')
    @app_commands.describe(
        reply_is_hidden='Botの実行結果を全員に見せるどうか(デフォルトは全員に見せる)')
    async def purge(self,
                    interaction: discord.Interaction,
                    limit_num: app_commands.Range[int, 1, 1000],
                    reply_is_hidden: Literal['自分のみ', '全員に見せる'] = SHOW_ME):
        """
        自分かBOTのメッセージを削除します。
        削除するメッセージの数が必要です。
        なお、BOTにメッセージの管理権限、メッセージの履歴閲覧権限、メッセージの閲覧権限がない場合は失敗します。
        """
        hidden = True if reply_is_hidden == self.SHOW_ME else False
        self.command_author = interaction.user
        # botかコマンドの実行主かチェック
        def is_me(m):
            return (self.command_author == m.author \
                    or (m.author.bot and settings.PURGE_TARGET_IS_ME_AND_BOT)) \
                    and m.type == discord.MessageType.default

        await interaction.response.defer()
        deleted = await interaction.channel.purge(limit=limit_num, check=is_me)
        await interaction.followup.send(content='{0}個のメッセージを削除しました。'.format(len(deleted)), ephemeral=hidden)

    # チャンネル管理コマンド群
    channel = app_commands.Group(name="channel", description='チャンネルを操作するコマンド（サブコマンド必須）')

    # channelコマンドのサブコマンドmake
    # チャンネルを作成する
    @channel.command(
        name='make',
        description='チャンネルを作成します（コマンドを打ったチャンネルの所属するカテゴリに作成されます）')
    @app_commands.describe(
        channel_name='チャンネル名')
    async def make(self, interaction: discord.Interaction, channel_name: str=None):
        """
        引数に渡したチャンネル名でテキストチャンネルを作成します（コマンドを打ったチャンネルの所属するカテゴリに作成されます）。
        30秒以内に👌(ok_hand)のリアクションをつけないと実行されませんので、素早く対応ください。
        """
        self.command_author = interaction.user
        # チャンネル名がない場合は実施不可
        if channel_name is None:
            await interaction.response.send_message('チャンネル名を指定してください。', ephemeral=True)
            return

        # メッセージの所属するカテゴリを取得
        guild = interaction.channel.guild
        category_id = interaction.channel.category_id
        category = guild.get_channel_or_thread(category_id)

        # カテゴリーが存在するなら、カテゴリーについて確認メッセージに記載する
        category_text = ''
        if category is not None:
            category_text = f'カテゴリー「**{category.name}**」に、\n';

        # 念の為、確認する
        confirm_text = f'{category_text}パブリックなチャンネル **{channel_name}** を作成してよろしいですか？ 問題ない場合、30秒以内に👌(ok_hand)のリアクションをつけてください。'
        try:
            confirm_msg = await interaction.channel.send(confirm_text)
            await interaction.response.send_message(f'チャンネル作成中です。チャンネルを確認してください。\n{confirm_msg.jump_url}', ephemeral=True)
        except (discord.HTTPException,discord.NotFound,discord.Forbidden) as e:
            dm = await interaction.user.create_dm()
            confirm_text2 = f'チャンネルに送信できないのでDMで失礼します。\n{confirm_text}'
            confirm_msg = await dm.send(confirm_text2)
            await interaction.response.send_message(f'チャンネル作成中です。DMを確認してください。\n{confirm_msg.jump_url}', ephemeral=True)

        def check(reaction, user):
            return user == self.command_author and str(reaction.emoji) == '👌'

        # リアクション待ち
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=self.TIMEOUT_TIME, check=check)
        except asyncio.TimeoutError:
            await confirm_msg.reply('リアクションがなかったのでチャンネル作成をキャンセルしました！')
        else:
            try:
                # カテゴリが存在しない場合と存在する場合で処理を分ける
                if category is None:
                    new_channel = await guild.create_text_channel(name=channel_name)
                else:
                    # メッセージの所属するカテゴリにテキストチャンネルを作成する
                    new_channel = await category.create_text_channel(name=channel_name)
            except discord.errors.Forbidden:
                await confirm_msg.reply('権限がないため、チャンネル作成できませんでした！')
            else:
                await confirm_msg.reply(f'<#{new_channel.id}>を作成しました！')

    # channelコマンドのサブコマンドprivateMake
    # チャンネルを作成する
    @channel.command(
        name='private-make',
        description='プライベートチャンネルチャンネルを作成します（コマンドを打ったチャンネルの所属するカテゴリに作成されます）')
    @app_commands.describe(
        channel_name='チャンネル名')
    async def privateMake(self, interaction: discord.Interaction, channel_name: str=None):
        """
        引数に渡したチャンネル名でプライベートなテキストチャンネルを作成します（コマンドを打ったチャンネルの所属するカテゴリに作成されます）。
        30秒以内に👌(ok_hand)のリアクションをつけないと実行されませんので、素早く対応ください。
        """
        self.command_author = interaction.user

        # チャンネル名がない場合は実施不可
        if channel_name is None:
            await interaction.response.send_message('チャンネル名を指定してください。', ephemeral=True)
            return

        # トップロールが@everyoneの場合は実施不可
        if self.command_author.top_role.position == 0:
            await interaction.response.send_message('everyone権限しか保持していない場合、このコマンドは使用できません。', ephemeral=True)
            return

        # メッセージの所属するカテゴリを取得
        guild = interaction.guild
        category_id = interaction.channel.category_id
        category = guild.get_channel_or_thread(category_id)

        # カテゴリーが存在するなら、カテゴリーについて確認メッセージに記載する
        category_text = ''
        if category is not None:
            category_text = f'カテゴリー「**{category.name}**」に、\n';

        # Guildのロールを取得し、@everyone以外のロールで最も下位なロール以上は書き込めるような辞書型overwritesを作成
        permissions = []
        for guild_role in guild.roles:
            # authorのeveryoneの1つ上のロールよりも下位のポジションの場合
            if guild_role.position < self.command_author.roles[1].position:
                permissions.append(discord.PermissionOverwrite(read_messages=False))
            else:
                permissions.append(discord.PermissionOverwrite(read_messages=True))
        overwrites = dict(zip(guild.roles, permissions))

        LOG.debug('-----author\'s role-----------------------------------------------------------')
        for author_role in self.command_author.roles:
            LOG.debug(f'id:{author_role.id}, name:{author_role.name}, position:{author_role.position}')
        LOG.debug('-----------------------------------------------------------------')
        LOG.debug('-----Guild\'s role-----------------------------------------------------------')
        for guild_role in guild.roles:
            LOG.debug(f'id:{guild_role.id}, name:{guild_role.name}, position:{guild_role.position}')
        LOG.debug('-----------------------------------------------------------------')

        # 念の為、確認する
        confirm_text = f'{category_text}プライベートなチャンネルを作成してよろしいですか()？ 問題ない場合、30秒以内に👌(ok_hand)のリアクションをつけてください。'
        try:
            confirm_msg = await interaction.channel.send(confirm_text)
            await interaction.response.send_message(f'プライベートなチャンネル(**{channel_name}**)作成中です。確認のため、チャンネルを確認してください。\n{confirm_msg.jump_url}', ephemeral=True)
        except (discord.HTTPException,discord.NotFound,discord.Forbidden) as e:
            dm = await interaction.user.create_dm()
            confirm_text2 = f'チャンネルに送信できないのでDMで失礼します。\n{confirm_text}'
            confirm_msg = await dm.send(confirm_text2)
            await interaction.response.send_message(f'プライベートなチャンネル(**{channel_name}**)作成中です。確認のため、DMを確認してください。\n{confirm_msg.jump_url}', ephemeral=True)

        def check(reaction, user):
            return user == self.command_author and str(reaction.emoji) == '👌'

        # リアクション待ち
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=self.TIMEOUT_TIME, check=check)
        except asyncio.TimeoutError:
            await confirm_msg.reply('＊リアクションがなかったのでキャンセルしました！(プライベートなチャンネルを立てようとしていました。)')
        else:
            try:
                # カテゴリが存在しない場合と存在する場合で処理を分ける
                if category is None:
                    new_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)
                else:
                    # メッセージの所属するカテゴリにテキストチャンネルを作成する
                    new_channel = await category.create_text_channel(name=channel_name, overwrites=overwrites)
            except discord.errors.Forbidden:
                await confirm_msg.reply('＊権限がないため、実行できませんでした！(プライベートなチャンネルを立てようとしていました。)')
            else:
                await confirm_msg.reply(f'`/channel private-make`コマンドでプライベートなチャンネルを作成しました！')

    # channelコマンドのサブコマンドtopic
    # チャンネルのトピックを設定する
    @channel.command(
        name='topic',
        description='チャンネルにトピックを設定します')
    @app_commands.describe(
        topic_word='トピック')
    async def topic(self, interaction: discord.Interaction, topic_word: str=None):
        """
        引数に渡した文字列でテキストチャンネルのトピックを設定します。
        30秒以内に👌(ok_hand)のリアクションをつけないと実行されませんので、素早く対応ください。
        """
        self.command_author = interaction.user
        # トピックがない場合は実施不可
        if topic_word is None:
            await interaction.response.send_message('トピックを指定してください。', ephemeral=True)
            return

        # 念の為、確認する
        original_topic = ''
        if interaction.channel.topic is not None:
            original_topic = f'このチャンネルには、トピックとして既に**「{interaction.channel.topic}」**が設定されています。\nそれでも、'
        confirm_text = f'{original_topic}このチャンネルのトピックに**「{topic_word}」** を設定しますか？ 問題ない場合、30秒以内に👌(ok_hand)のリアクションをつけてください。'
        try:
            confirm_msg = await interaction.channel.send(confirm_text)
            await interaction.response.send_message(f'トピック設定中です。確認のため、チャンネルを確認してください。\n{confirm_msg.jump_url}', ephemeral=True)
        except (discord.HTTPException,discord.NotFound,discord.Forbidden) as e:
            dm = await interaction.user.create_dm()
            confirm_text2 = f'チャンネルに送信できないのでDMで失礼します。\n{confirm_text}'
            confirm_msg = await dm.send(confirm_text2)
            await interaction.response.send_message(f'トピック設定中です。確認のため、DMを確認してください。\n{confirm_msg.jump_url}', ephemeral=True)

        def check(reaction, user):
            return user == self.command_author and str(reaction.emoji) == '👌'

        # リアクション待ち
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=self.TIMEOUT_TIME, check=check)
        except asyncio.TimeoutError:
            await confirm_msg.reply('リアクションがなかったので、トピックの設定をキャンセルしました！')
        else:
            # チャンネルにトピックを設定する
            try:
                await interaction.channel.edit(topic=topic_word)
            except discord.errors.Forbidden:
                await confirm_msg.reply('権限がないため、トピックを設定できませんでした！')
            else:
                await confirm_msg.reply(f'チャンネル「{interaction.channel.name}」のトピックに**「{topic_word}」**を設定しました！')

    # channelコマンドのサブコマンドroleDel
    # チャンネルのロールを削除する（テキストチャンネルが見えないようにする）
    @channel.command(
        name='role-delete',
        description='チャンネルのロールを削除します')
    @app_commands.describe(
        target_role='見れなくする対象のロール(このロール以下が見られなくなる)')
    async def roleDelete(self, interaction: discord.Interaction, target_role: str=None):
        """
        指定したロールがテキストチャンネルを見れないように設定します（自分とおなじ権限まで指定可能（ただしチャンネルに閲覧できるロールがない場合、表示されなくなります！））。
        30秒以内に👌(ok_hand)のリアクションをつけないと実行されませんので、素早く対応ください。
        """
        self.command_author = interaction.user
        # 対象のロールがない場合は実施不可
        if target_role is None:
            await interaction.response.send_message('チャンネルから削除するロールを指定してください。', ephemeral=True)
            return
        # トップロールが@everyoneの場合は実施不可
        if self.command_author.top_role.position == 0:
            await interaction.response.send_message('everyone権限しか保持していない場合、このコマンドは使用できません。', ephemeral=True)
            return

        author = discord.utils.find(lambda m: m.name == self.command_author.name, interaction.guild.members)
        underRoles = [guild_role.name for guild_role in interaction.guild.roles if guild_role.position <= author.top_role.position]
        underRolesWithComma = ",".join(underRoles).replace('@', '')
        print(underRolesWithComma)

        role = discord.utils.get(interaction.guild.roles, name=target_role)
        # 指定したロール名がeveryoneの場合、@everyoneとして処理する
        if target_role == 'everyone':
            role = interaction.guild.default_role

        # 削除対象としたロールが、実行者のトップロールより大きい場合は実施不可(ロールが存在しない場合も実施不可)
        if role is None:
            await interaction.response.send_message(f'**存在しない**ロールのため、実行できませんでした(大文字小文字を正確に入力ください)。\n＊削除するロールとして{underRolesWithComma}が指定できます。', ephemeral=True)
            return
        elif role > self.command_author.top_role:
            await interaction.response.send_message(f'**削除対象のロールの方が権限が高い**ため、実行できませんでした(大文字小文字を正確に入力ください)。\n＊削除するロールとして{underRolesWithComma}が指定できます。', ephemeral=True)
            return

        # 読み書き権限を削除したoverwritesを作る
        overwrite = discord.PermissionOverwrite(read_messages=False)

        # botのロール確認
        botRoleUpdateFlag = False
        botUser = self.bot.user
        botMember = discord.utils.find(lambda m: m.name == botUser.name, interaction.guild.members)

        bot_role,bot_overwrite = None, None
        attention_text = ''
        if botMember.top_role.position == 0:
            if target_role == 'everyone':
                attention_text = f'＊＊これを実行するとBOTが書き込めなくなるため、**権限削除に成功した場合でもチャンネルに結果が表示されません**。\n'
        else:
            bot_role = botMember.top_role
            bot_overwrites_pair = interaction.channel.overwrites_for(bot_role).pair()
            LOG.debug(bot_overwrites_pair)
            # 権限が初期設定なら
            if (bot_overwrites_pair[0].value == 0) and (bot_overwrites_pair[1].value == 0):
                bot_overwrite = discord.PermissionOverwrite(read_messages=True,read_message_history=True)
                botRoleUpdateFlag = True
            if target_role == bot_role.name:
                attention_text = f'＊＊これを実行するとBOTが書き込めなくなるため、**権限削除に成功した場合でもチャンネルに結果が表示されません**。\n'

        # 念の為、確認する
        confirm_text = f'{attention_text}このチャンネルから、ロール**「{target_role}」** を削除しますか？\n（{target_role}はチャンネルを見ることができなくなります。）\n 問題ない場合、30秒以内に👌(ok_hand)のリアクションをつけてください。'
        try:
            confirm_msg = await interaction.channel.send(confirm_text)
            await interaction.response.send_message(f'権限変更中です。確認のため、チャンネルを確認してください。\n{confirm_msg.jump_url}', ephemeral=True)
        except (discord.HTTPException,discord.NotFound,discord.Forbidden) as e:
            dm = await interaction.user.create_dm()
            confirm_text2 = f'チャンネルに送信できないのでDMで失礼します。\n{confirm_text}'
            confirm_msg = await dm.send(confirm_text2)
            await interaction.response.send_message(f'権限変更中です。確認のため、DMを確認してください。\n{confirm_msg.jump_url}', ephemeral=True)

        def check(reaction, user):
            return user == self.command_author and str(reaction.emoji) == '👌'

        # リアクション待ち
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=self.TIMEOUT_TIME, check=check)
        except asyncio.TimeoutError:
            await confirm_msg.reply('リアクションがなかったのでチャンネルのロール削除をキャンセルしました！')
        else:
            # チャンネルに権限を上書きする
            try:
                if botRoleUpdateFlag:
                    await interaction.channel.set_permissions(bot_role, overwrite=bot_overwrite)
                await interaction.channel.set_permissions(role, overwrite=overwrite)
            except discord.errors.Forbidden:
                await confirm_msg.reply('権限がないため、チャンネルのロールを削除できませんでした！')
            else:
                await confirm_msg.reply(f'チャンネル「{interaction.channel.name}」からロール**「{target_role}」**の閲覧権限を削除しました！')

    # 指定した文章を含むメッセージを削除するコマンド
    @channel.command(
        name='delete-message',
        description='指定した文章を含むメッセージを削除します')
    @app_commands.describe(
        keyword='削除対象のキーワード(必須)')
    @app_commands.describe(
        limit_num='削除対象とするメッセージの数(任意。デフォルトは1)')
    @app_commands.describe(
        reply_is_hidden='Botの実行結果を全員に見せるどうか(デフォルトは全員に見せる)')
    async def deleteMessage(self,
                            interaction: discord.Interaction,
                            keyword :str=None, limit_num: str='1',
                            reply_is_hidden: Literal['自分のみ', '全員に見せる'] = SHOW_ME):
        """
        自分かBOTの指定した文章を含むメッセージを削除します。
        削除対象のキーワード(必須)、削除対象とするメッセージの数(任意。デフォルトは1)
        なお、BOTにメッセージの管理権限、メッセージの履歴閲覧権限、メッセージの閲覧権限がない場合は失敗します。
        """
        hidden = True if reply_is_hidden == self.SHOW_ME else False
        self.command_author = interaction.user
        # botかコマンドの実行主かチェックし、キーワードを含むメッセージのみ削除
        def is_me_and_contain_keyword(m):
            return (self.command_author == m.author or (m.author.bot and settings.PURGE_TARGET_IS_ME_AND_BOT)) and keyword in m.clean_content

        # 指定がない、または、不正な場合は、コマンドを削除。そうではない場合、コマンドを削除し、指定数だけメッセージを走査し、キーワードを含むものだけ削除する
        if keyword is None:
            await interaction.response.send_message('削除対象のキーワードを指定してください(削除対象とするメッセージ数を続けて指定してください)。', ephemeral=True)
            return
        if limit_num.isdecimal():
            limit_num = int(limit_num)
        else:
            await interaction.response.send_message('有効な数字ではないようです。削除数は1以上の数値を指定してください。', ephemeral=True)
            return

        if limit_num > 1000:
            limit_num = 1000
        elif limit_num < 1:
            await interaction.response.send_message('削除数は1以上の数値を指定してください。', ephemeral=True)
            return

        await interaction.response.defer()
        deleted = await interaction.channel.purge(limit=limit_num, check=is_me_and_contain_keyword)
        await interaction.followup.send(content='{0}個のメッセージを削除しました。'.format(len(deleted)), ephemeral=hidden)

    # チャンネル作成時に実行されるイベントハンドラを定義
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        event_text = '作成'
        await self.on_guild_channel_xxx(channel, event_text)

    # チャンネル削除時に実行されるイベントハンドラを定義
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        event_text = '削除'
        await self.on_guild_channel_xxx(channel, event_text)

    # チャンネル作成/削除時のメッセージを作成
    async def on_guild_channel_xxx(self, channel: discord.abc.GuildChannel, event_text):
        guild = channel.guild
        str = 'id: {0}, name: {1}, type:{2}が{3}されました'.format(channel.id, channel.name, channel.type, event_text)

        if isinstance(channel, discord.TextChannel):
            str = 'id: {0}, name: #{1}, type:{2}が{3}されました'.format(channel.id, channel.name, channel.type, event_text)
            category = guild.get_channel_or_thread(channel.category_id)
            if category is not None:
                str += '\nCategory: {0}, channel: <#{1}>'.format(category.name, channel.id)
            else:
                str += '\nchannel: <#{0}>'.format(channel.id)
        elif isinstance(channel, discord.VoiceChannel):
            category = guild.get_channel_or_thread(channel.category_id)
            if category is not None:
                str += '\nCategory: {0}'.format(category.name)
        LOG.info(f'***{str}***')
        await self.sendGuildChannel(guild, str, channel.created_at)

    # メンバーGuild参加時に実行されるイベントハンドラを定義
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        event_text = '参加'
        await self.on_member_xxx(member, event_text, member.joined_at)

    # メンバーGuild脱退時に実行されるイベントハンドラを定義
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        event_text = '脱退'
        now = datetime.datetime.now()
        now_tz = now.astimezone(datetime.timezone(datetime.timedelta(hours=0)))
        await self.on_member_xxx(member, event_text, now_tz)

    # メンバーの参加/脱退時のメッセージを作成
    async def on_member_xxx(self, member: discord.Member, event_text: str, dt: datetime):
        guild = member.guild
        str = 'member: {0}が{1}しました'.format(member, event_text)

        LOG.info(f'***{str}***')

        await self.sendGuildChannel(guild, str, dt)

    # 監査ログをチャンネルに送信
    async def sendGuildChannel(self, guild: discord.Guild, str: str, dt: datetime):
        if await self.audit_log_channel.get_ch(guild) is False:
            LOG.debug(self.audit_log_channel.alc_err)
            return
        else:
            to_channel = self.audit_log_channel.channel
        dt_tz = dt.replace(tzinfo=datetime.timezone.utc)
        dt_jst = dt_tz.astimezone(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y/%m/%d(%a) %H:%M:%S')
        msg = '{1}: {0}'.format(str, dt_jst)
        await to_channel.send(msg)

async def setup(bot):
    await bot.add_cog(AdminCog(bot)) # AdminCogにBotを渡してインスタンス化し、Botにコグとして登録する