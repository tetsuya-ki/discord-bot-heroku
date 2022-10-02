import discord, random, asyncio, re
from .members import Members
from logging import getLogger
from typing import List

LOG = getLogger('assistantbot')
POLL_CHAR = ['🇦','🇧','🇨','🇩','🇪','🇫','🇬','🇭','🇮','🇯','🇰','🇱','🇲','🇳','🇴','🇵','🇶','🇷','🇸','🇹']

class defaultStart(discord.ui.View):
    def __init__(self):
        super().__init__()

    async def delayedMessage(self, interaction, messsage, delayed_seconds=None):
        message = interaction.message
        await asyncio.sleep(delayed_seconds)
        await message.reply(messsage)

    async def delayedPoll(self, interaction, messsage, players, delayed_seconds=None):
        message = interaction.message
        await asyncio.sleep(delayed_seconds)
        embed = discord.Embed()
        nicknames = []
        for player in players:
            nicknames.append(player.display_name)
        for  emoji, arg in zip(POLL_CHAR, nicknames):
            embed.add_field(name=emoji, value=arg) # inline=False
        message = await message.reply(messsage, embed=embed)
        for  emoji, arg in zip(POLL_CHAR, nicknames):
            await message.add_reaction(emoji)

    def rewrite_link_at_me(self, link:str='', guild_id:int=None):
        """
        スレッドの中のリンク取得が想定外(一応遷移できるが)のため、修正
        こうあるべき: https://discord.com/channels/<guild_id>/<channel_id>/<message_id>
        実際: https://discord.com/channels/@me//<channel_id>/<message_id>
        """
        if guild_id:
            return str(link).replace('@me', str(guild_id))
        else:
            return ''

class WordwolfStart(defaultStart):
    def __init__(self, ww_members, wordWolfJson, msg):
        super().__init__()
        self.ww_members = ww_members
        self.wordWolfJson = wordWolfJson
        self.msg = msg

    @discord.ui.button(label='参加する', style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.guild_id in self.ww_members:
            self.ww_members[interaction.guild_id].add_member(interaction.user)
        else:
            self.ww_members[interaction.guild_id] = Members()
            self.ww_members[interaction.guild_id].add_member(interaction.user)
        LOG.debug(f'追加:{interaction.user.display_name}')
        message = self.msg + f'\n\n{interaction.user.display_name}が参加しました(参加人数:{self.ww_members[interaction.guild_id].len})'
        await interaction.response.edit_message(content=message, view=self)

    @discord.ui.button(label='離脱する', style=discord.ButtonStyle.red)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        # ボタンを押した人をゲームから除外
        if interaction.guild_id in self.ww_members:
            self.ww_members[interaction.guild_id].remove_member(interaction.user)
        else:
            self.ww_members[interaction.guild_id] = Members()
        LOG.debug(f'削除:{interaction.user.display_name}')
        # ボタンを押した人を表示し、参加人数を記載
        message = self.msg + f'\n\n{interaction.user.display_name}が離脱しました(参加人数:{self.ww_members[interaction.guild_id].len})'
        await interaction.response.edit_message(content=message, view=self)

    @discord.ui.button(label='開始する', style=discord.ButtonStyle.blurple)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        LOG.debug(f'開始:{interaction.user.display_name}より依頼')
        if interaction.guild_id not in self.ww_members:
            msg = f'ゲームが始まっていません。`/start-word-wolf`でゲームを開始してください。'
            self.ww_members[interaction.guild_id] = Members()
            await interaction.response.edit_message(content=msg, view=self)
            return
        # ワードウルフ開始
        if self.ww_members[interaction.guild_id].len < 3:
            message = self.msg + f'\n\nワードウルフを楽しむには3人以上のメンバーが必要です(現在、{self.ww_members[interaction.guild_id].len}人しかいません)'
            await interaction.response.edit_message(content=message, view=self)
            return

        # お題の選定
        choiced_item = random.choice(self.wordWolfJson.list)
        odai = self.wordWolfJson.dict[choiced_item]
        citizen_odai, wolf_odai = random.sample(odai, 2)

        # ワードウルフの数設定
        wolf_numbers = self.ww_members[interaction.guild_id].len // 3
        msg =   f'この中に、**{wolf_numbers}人のワードウルフ**が紛れ込んでいます(本人も知りません！)。\n'\
                f'DMに送られたお題を確認し、**{self.ww_members[interaction.guild_id].minutes}分話し合いののち、投票を実施**してください！！　今から開始します！'
        await interaction.response.send_message(msg)

        # メンバーをシャッフル
        random.shuffle(self.ww_members[interaction.guild_id].get_members())
        netabare_msg = f'**ワードウルフのお題は||「{wolf_odai}」||**でした！\nワードウルフは'

        # それぞれに役割をDMで送信
        for player in self.ww_members[interaction.guild_id].get_members():
            if wolf_numbers > 0:
                player_odai = wolf_odai
                wolf_numbers = wolf_numbers - 1
                netabare_msg += f'||{player.display_name}||さん '
            else:
                player_odai = citizen_odai
            dm = await player.create_dm()
            await dm.send(f'{player.mention}さんのワードは**「{player_odai}」**です！\n開始メッセージへのリンク: {self.rewrite_link_at_me(interaction.channel.jump_url, interaction.guild_id)}')
        netabare_msg += 'でした！  お疲れ様でした！'

        # 投票のお願いメッセージを作成し、チャンネルに貼り付け
        voting_msg = '投票を行なってください。誰がワードウルフだったでしょうか？'
        voting_time = self.ww_members[interaction.guild_id].minutes * 50
        await self.delayedPoll(interaction, voting_msg, self.ww_members[interaction.guild_id].get_members(), voting_time)

        # ワードウルフのネタバレメッセージを作成し、チャンネルに貼り付け
        await self.delayedMessage(interaction, netabare_msg, (self.ww_members[interaction.guild_id].minutes * 60) - voting_time)

    @discord.ui.button(label='参加者をクリアする', style=discord.ButtonStyle.grey)
    async def clear(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.ww_members[interaction.guild_id] = Members()
        LOG.debug(f'参加者クリア:{interaction.user.display_name}')
        message = f'参加者がクリアされました(参加人数:{self.ww_members[interaction.guild_id].len})'
        await interaction.response.edit_message(content=message, view=self)

class NgWordGameStart(defaultStart):
    def __init__(self, ng_members, ngWordGameJson, msg):
        super().__init__()
        self.ng_members = ng_members
        self.ngWordGameJson = ngWordGameJson
        self.msg = msg

    @discord.ui.button(label='参加する', style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.guild_id in self.ng_members:
            self.ng_members[interaction.guild_id].add_member(interaction.user)
        else:
            self.ng_members[interaction.guild_id] = Members()
            self.ng_members[interaction.guild_id].add_member(interaction.user)
        LOG.debug(f'追加:{interaction.user.display_name}')
        message = self.msg + f'\n\n{interaction.user.display_name}が参加しました(参加人数:{self.ng_members[interaction.guild_id].len})'
        await interaction.response.edit_message(content=message, view=self)

    @discord.ui.button(label='離脱する', style=discord.ButtonStyle.red)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        # ボタンを押した人をゲームから除外
        if interaction.guild_id in self.ng_members:
            self.ng_members[interaction.guild_id].remove_member(interaction.user)
        else:
            self.ng_members[interaction.guild_id] = Members()
        LOG.debug(f'削除:{interaction.user.display_name}')
        # ボタンを押した人を表示し、参加人数を記載
        message = self.msg + f'\n\n{interaction.user.display_name}が離脱しました(参加人数:{self.ng_members[interaction.guild_id].len})'
        await interaction.response.edit_message(content=message, view=self)

    @discord.ui.button(label='開始する', style=discord.ButtonStyle.blurple)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        LOG.debug(f'開始:{interaction.user.display_name}より依頼')
        if interaction.guild_id not in self.ng_members:
            msg = f'ゲームが始まっていません。`/start-ng-word-game`でゲームを開始してください。'
            self.ng_members[interaction.guild_id] = Members()
            await interaction.response.edit_message(content=msg, view=self)
            return
        if self.ng_members[interaction.guild_id].len < 2:
            message = self.msg + f'\n\nNGワードゲームを楽しむには2人以上のメンバーが必要です(現在、{self.ng_members[interaction.guild_id].len}人しかいません)'
            await interaction.response.edit_message(content=message, view=self)
            return

        msg = f'まず、DMに送られたNGワードを確認し、相手が「NGワードを喋ってしまう」ようにトークしてください！**{self.ng_members[interaction.guild_id].minutes}分で終了**です！　今から開始します！！'
        await interaction.response.send_message(msg)

        netabare_msg = ''
        # どの項目から選ぶかを最初に決め、その中からお題を振る
        choiced_item = random.choice(self.ngWordGameJson.list)
        # それぞれに役割をDMで送信
        for player in self.ng_members[interaction.guild_id].get_members():
            # お題の選定
            odai = self.ngWordGameJson.dict[choiced_item]
            ngword = random.choice(odai)
            netabare_msg += f'{player.display_name}さん:||{ngword}||, '

        for player in self.ng_members[interaction.guild_id].get_members():
            dm = await player.create_dm()
            rpl_msg_del = f'{player.display_name}さん:(\|\|.+?\|\|, )'
            dm_msg = re.sub(rpl_msg_del, '', netabare_msg)
            dm_msg_open = dm_msg.replace('|', '').replace(', ', '\n')
            await dm.send(f'{player.mention}さん 他の人のNGワードはこちらです！\n{dm_msg_open}開始メッセージへのリンク: {self.rewrite_link_at_me(interaction.channel.jump_url, interaction.guild_id)}')

        netabare_msg = re.sub(', $', '', netabare_msg)

        # NGワードゲームのネタバレメッセージを作成し、チャンネルに貼り付け
        await self.delayedMessage(interaction, 'NGワードゲームのネタバレです！\nそれぞれ、' + netabare_msg + 'でした！', self.ng_members[interaction.guild_id].minutes * 60)

    @discord.ui.button(label='参加者をクリアする', style=discord.ButtonStyle.grey)
    async def clear(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.ng_members[interaction.guild_id] = Members()
        LOG.debug(f'参加者クリア:{interaction.user.display_name}')
        message = f'参加者がクリアされました(参加人数:{self.ng_members[interaction.guild_id].len})'
        await interaction.response.edit_message(content=message, view=self)