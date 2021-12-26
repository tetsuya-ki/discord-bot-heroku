import discord
from discord.ext import commands  # Bot Commands Frameworkのインポート
from .modules.readjson import ReadJson
from logging import getLogger
from .modules.coyote import Coyote
from .modules.ohgiri import Ohgiri
from os.path import join, dirname
from .modules import settings
from .modules.savefile import SaveFile
from discord_slash import cog_ext, SlashContext
from discord_slash.utils import manage_commands  # Allows us to manage the command settings.
from discord_slash.utils.manage_components import ComponentContext
from .modules.members import Members
from .modules import gamebuttons

import asyncio
import random
import re
import os

LOG = getLogger('word_wolf')
POLL_CHAR = ['🇦','🇧','🇨','🇩','🇪','🇫','🇬','🇭','🇮','🇯','🇰','🇱','🇲','🇳','🇴','🇵','🇶','🇷','🇸','🇹']

# コグとして用いるクラスを定義。
class GameCog(commands.Cog, name='ゲーム用'):
    """
    ゲーム機能のカテゴリ。
    """
    guilds = [] if settings.ENABLE_SLASH_COMMAND_GUILD_ID_LIST is None else list(
        map(int, settings.ENABLE_SLASH_COMMAND_GUILD_ID_LIST.split(';')))
    MAX_TIME = 10
    DEFAULT_TIME = 2

    # GameCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    def __init__(self, bot):
        self.bot = bot
        self.coyoteGames = {}
        self.ohgiriGames = {}
        self.wordWolfJson = None
        self.ngWordGameJson = None
        self.savefile = SaveFile()
        self.ww_members = {}
        self.ng_members = {}
        self.cy_members = {}
        self.oh_members = {}

    # cogが準備できたら読み込みする
    @commands.Cog.listener()
    async def on_ready(self):
        self.ohgiriGames['default'] = Ohgiri()
        await self.ohgiriGames['default'].on_ready()
        await self.wordWolf_setting()
        await self.ngWordGame_setting()

    async def wordWolf_setting(self):
        wordWolf_filepath = None
        if settings.WORDWOLF_JSON_URL:
            wordWolf_filepath = await self.json_setting(settings.WORDWOLF_JSON_URL, 'wordwolf.json')
        # ファイルを読み込み、ワードウルフ用のデータを作成
        read_json = ReadJson()
        read_json.readJson(wordWolf_filepath)
        self.wordWolfJson = read_json

    async def ngWordGame_setting(self):
        ngWordGame_filepath = None
        if settings.NGWORD_GAME_JSON_URL:
            ngWordGame_filepath = await self.json_setting(settings.NGWORD_GAME_JSON_URL, 'ngword_game.json')
        # ファイルを読み込み、NGワードゲーム用のデータを作成
        read_json = ReadJson()
        read_json.readJson(ngWordGame_filepath)
        self.ngWordGameJson = read_json

    async def json_setting(self, json_url=None, file_name='no_name.json'):
        json_path = join(dirname(__file__), 'modules' + os.sep + 'files' + os.sep + 'temp' + os.sep + file_name)
        # URLが設定されている場合はそちらを使用
        if json_url:
            file_path = await self.savefile.download_file(json_url,  json_path)
            LOG.info(f'JSONのURLが登録されているため、JSONを保存しました。\n{file_path}')
            return file_path

    # ワードウルフ機能
    @cog_ext.cog_slash(
    name='start-word-wolf',
    # guild_ids=guilds,
    description='ワードウルフ機能(少数派のワードを与えられた人を当てるゲーム)',
    options=[
        manage_commands.create_option(name='answer_minutes',
                                    description='投票開始までの時間（3などの正数。単位は「分」）を与えることができます。デフォルトは2分です',
                                    option_type=3,
                                    required=False)
    ])
    async def wordWolf(self, ctx, answer_minutes=None):
        """
        コマンド実行者が参加しているボイスチャンネルでワードウルフ始めます（BOTからDMが来ますがびっくりしないでください）
        引数(answer_minutes)として投票開始までの時間（3などの正数。単位は「分」）を与えることができます。デフォルトは2分です。
        3人増えるごとにワードウルフは増加します(3−5人→ワードウルフは1人、6−8人→ワードウルフは2人)
        """
        if answer_minutes is None:
            answer_minutes = self.DEFAULT_TIME
        elif answer_minutes.isdecimal():
            answer_minutes = int(answer_minutes)
        else:
            answer_minutes = self.DEFAULT_TIME

        if answer_minutes > self.MAX_TIME:
            msg = f'ワードウルフはそんなに長い時間するものではないです(現在、{answer_minutes}分を指定しています。{self.MAX_TIME}分以内にして下さい)'
            await ctx.send(msg, hidden = True)
            return
        if ctx.guild_id in self.ww_members:
            self.ww_members[ctx.guild_id].set_minutes(answer_minutes)
        else:
            self.ww_members[ctx.guild_id] = Members()
            self.ww_members[ctx.guild_id].set_minutes(answer_minutes)

        msg =   'ワードウルフを始めます(3人以上必要です)！　この中に、**ワードウルフ**が紛れ込んでいます(本人も知りません！)。\n'\
                'DMでお題が配られますが、**ワードウルフだけは別のお題**が配られます(お題は2種類あります)。会話の中で不審な言動を察知し、みごとに'\
                '投票でワードウルフを当てることができたら、市民の勝ち。**間違えて「市民をワードウルフ」だと示してしまった場合、ワードウルフの勝ち**です！！\n'\
                '参加する場合、以下のボタンを押してください。'
        await ctx.send(msg)
        await ctx.send('ボタン', components=[gamebuttons.ww_join_action_row])

    @commands.Cog.listener()
    async def on_component(self, ctx: ComponentContext):
        # ワードウルフ
        wordwolf_components = [gamebuttons.ww_join_action_row,gamebuttons.ww_leave_action_row,gamebuttons.ww_start_action_row,gamebuttons.ww_purge_action_row]
        if ctx.custom_id == gamebuttons.CUSTOM_ID_JOIN_WORD_WOLF:
            if ctx.guild_id in self.ww_members:
                self.ww_members[ctx.guild_id].add_member(ctx.author)
            else:
                self.ww_members[ctx.guild_id] = Members()
                self.ww_members[ctx.guild_id].add_member(ctx.author)
            LOG.debug(f'追加:{ctx.author.display_name}')
            await ctx.edit_origin(content=f'{ctx.author.display_name}が参加しました!(参加人数:{self.ww_members[ctx.guild_id].len})', components=wordwolf_components)
        if ctx.custom_id == gamebuttons.CUSTOM_ID_LEAVE_WORD_WOLF:
            if ctx.guild_id in self.ww_members:
                self.ww_members[ctx.guild_id].remove_member(ctx.author)
            else:
                self.ww_members[ctx.guild_id] = Members()
            LOG.debug(f'削除:{ctx.author.display_name}')
            await ctx.edit_origin(content=f'{ctx.author.display_name}が離脱しました!(参加人数:{self.ww_members[ctx.guild_id].len})', components=wordwolf_components)
        if ctx.custom_id == gamebuttons.CUSTOM_ID_EXTEND_WORD_WOLF:
            if ctx.guild_id in self.ww_members:
                self.ww_members[ctx.guild_id].add_minutes(1)
            else:
                self.ww_members[ctx.guild_id] = Members()
            LOG.debug(f'1分追加:{ctx.author.display_name}より依頼')
        if ctx.custom_id == gamebuttons.CUSTOM_ID_PURGE_WORD_WOLF:
            self.ww_members[ctx.guild_id] = Members()
            LOG.debug(f'参加者クリア:{ctx.author.display_name}')
            await ctx.edit_origin(content=f'参加者がクリアされました(参加人数:{self.ww_members[ctx.guild_id].len})', components=wordwolf_components)
        if ctx.custom_id == gamebuttons.CUSTOM_ID_START_WORD_WOLF:
            LOG.debug(f'開始:{ctx.author.display_name}より依頼')
            if ctx.guild_id not in self.ww_members:
                msg = f'ゲームが始まっていません。`/start-word-wolf`でゲームを開始してください。'
                self.ww_members[ctx.guild_id] = Members()
                await ctx.edit_origin(content=msg, components=wordwolf_components)
                return
            # ワードウルフ開始
            if self.ww_members[ctx.guild_id].len < 3:
                msg = f'ワードウルフを楽しむには3人以上のメンバーが必要です(現在、{self.ww_members[ctx.guild_id].len}人しかいません)'
                await ctx.edit_origin(content=msg, components=wordwolf_components)
                return

            #　お題の選定
            choiced_item = random.choice(self.wordWolfJson.list)
            odai = self.wordWolfJson.dict[choiced_item]
            citizen_odai, wolf_odai = random.sample(odai, 2)

            # ワードウルフの数設定
            wolf_numbers = self.ww_members[ctx.guild_id].len // 3
            msg =   f'この中に、**{wolf_numbers}人のワードウルフ**が紛れ込んでいます(本人も知りません！)。\n'\
                    f'DMに送られたお題を確認し、**{self.ww_members[ctx.guild_id].minutes}分話し合いののち、投票を実施**してください！！　今から開始します！'
            start_msg =  await ctx.send(msg) #(msg, components=[gamebuttons.ww_extend_action_row])

            # メンバーをシャッフル
            random.shuffle(self.ww_members[ctx.guild_id].get_members())
            netabare_msg = f'**ワードウルフのお題は||「{wolf_odai}」||**でした！\nワードウルフは'

            # それぞれに役割をDMで送信
            for player in self.ww_members[ctx.guild_id].get_members():
                if wolf_numbers > 0:
                    player_odai = wolf_odai
                    wolf_numbers = wolf_numbers - 1
                    netabare_msg += f'||{player.display_name}||さん '
                else:
                    player_odai = citizen_odai
                dm = await player.create_dm()
                await dm.send(f'{player.mention}さんのワードは**「{player_odai}」**です！\n開始メッセージへのリンク: {start_msg.jump_url}')

            netabare_msg += 'でした！　お疲れ様でした！'

            voting_msg = '投票の時間が近づいてきました。下記のメッセージで投票をお願いします。\n'\
                        '`/simple-poll 誰がワードウルフ？'
            for player in self.ww_members[ctx.guild_id].get_members():
                voting_msg += f'/"{player.display_name}"'
            voting_msg += '`'

            # 投票のお願いメッセージを作成し、チャンネルに貼り付け
            voting_time = self.ww_members[ctx.guild_id].minutes * 50
            await self.delayedMessage(ctx, voting_msg, voting_time)

            # ワードウルフのネタバレメッセージを作成し、チャンネルに貼り付け
            await self.delayedMessage(ctx, netabare_msg, (self.ww_members[ctx.guild_id].minutes * 60) - voting_time)

        # NGワードゲーム
        ngwordgame_componets = [gamebuttons.ng_join_action_row,gamebuttons.ng_leave_action_row,gamebuttons.ng_start_action_row,gamebuttons.ng_purge_action_row]
        if ctx.custom_id == gamebuttons.CUSTOM_ID_JOIN_NGGAME:
            if ctx.guild_id in self.ng_members:
                self.ng_members[ctx.guild_id].add_member(ctx.author)
            else:
                self.ng_members[ctx.guild_id] = Members()
                self.ng_members[ctx.guild_id].add_member(ctx.author)
                return
            LOG.debug(f'追加:{ctx.author.display_name}')
            await ctx.edit_origin(content=f'{ctx.author.display_name}が参加しました!(参加人数:{self.ng_members[ctx.guild_id].len})', components=ngwordgame_componets)
        if ctx.custom_id == gamebuttons.CUSTOM_ID_LEAVE_NGGAME:
            if ctx.guild_id in self.ng_members:
                self.ng_members[ctx.guild_id].remove_member(ctx.author)
            else:
                self.ng_members[ctx.guild_id] = Members()
                return
            LOG.debug(f'削除:{ctx.author.display_name}')
            await ctx.edit_origin(content=f'{ctx.author.display_name}が離脱しました!(参加人数:{self.ng_members[ctx.guild_id].len})', components=ngwordgame_componets)
        if ctx.custom_id == gamebuttons.CUSTOM_ID_EXTEND_NGGAME:
            if ctx.guild_id in self.ng_members:
                self.ng_members[ctx.guild_id].add_minutes(1)
            else:
                self.ng_members[ctx.guild_id] = Members()
                return
            LOG.debug(f'1分追加:{ctx.author.display_name}より依頼')
        if ctx.custom_id == gamebuttons.CUSTOM_ID_PURGE_NGGAME:
            self.ng_members[ctx.guild_id] = Members()
            LOG.debug(f'参加者クリア:{ctx.author.display_name}')
            await ctx.edit_origin(content=f'参加者がクリアされました(参加人数:{self.ng_members[ctx.guild_id].len})', components=ngwordgame_componets)
        if ctx.custom_id == gamebuttons.CUSTOM_ID_START_NGGAME:
            if ctx.guild_id not in self.ng_members:
                msg = f'ゲームが始まっていません。`/start-ng-word-game`でゲームを開始してください。'
                self.ng_members[ctx.guild_id] = Members()
                await ctx.edit_origin(content=msg, components=ngwordgame_componets)
                return
            if self.ng_members[ctx.guild_id].len < 2:
                msg = f'NGワードゲームを楽しむには2人以上のメンバーが必要です(現在、{self.ng_members[ctx.guild_id].len}人しかいません)'
                await ctx.edit_origin(content=msg, components=ngwordgame_componets)
                return

            msg = f'まず、DMに送られたNGワードを確認し、相手が「NGワードを喋ってしまう」ようにトークしてください！**{self.ng_members[ctx.guild_id].minutes}分で終了**です！　今から開始します！！'
            start_msg = await ctx.send(msg)

            netabare_msg = ''
            # どの項目から選ぶかを最初に決め、その中からお題を振る
            choiced_item = random.choice(self.ngWordGameJson.list)
            # それぞれに役割をDMで送信
            for player in self.ng_members[ctx.guild_id].get_members():
                #　お題の選定
                odai = self.ngWordGameJson.dict[choiced_item]
                ngword = random.choice(odai)
                netabare_msg += f'{player.display_name}さん:||{ngword}||, '

            for player in self.ng_members[ctx.guild_id].get_members():
                dm = await player.create_dm()
                rpl_msg_del = f'{player.display_name}さん:(\|\|.+?\|\|, )'
                dm_msg = re.sub(rpl_msg_del, '', netabare_msg)
                dm_msg_open = dm_msg.replace('|', '').replace(', ', '\n')
                await dm.send(f'{player.mention}さん 他の人のNGワードはこちらです！\n{dm_msg_open}開始メッセージへのリンク: {start_msg.jump_url}')

            netabare_msg = re.sub(', $', '', netabare_msg)

            # NGワードゲームのネタバレメッセージを作成し、チャンネルに貼り付け
            await self.delayedMessage(ctx, 'NGワードゲームのネタバレです！\nそれぞれ、' + netabare_msg + 'でした！', self.ng_members[ctx.guild_id].minutes * 60)

        # コヨーテ
        coyote_components=[gamebuttons.cy_join_action_row,gamebuttons.cy_leave_action_row]
        if ctx.guild_id in self.coyoteGames:
            if self.coyoteGames[ctx.guild_id].set_deck_flg:
                coyote_components.append(gamebuttons.cyw_start_action_row)
            else:
                coyote_components.append(gamebuttons.cy_start_action_row)
            coyote_components.append(gamebuttons.cy_purge_action_row)

        if ctx.custom_id == gamebuttons.CUSTOM_ID_JOIN_COYOTE:
            if ctx.guild_id in self.cy_members:
                self.cy_members[ctx.guild_id].add_member(ctx.author)
            else:
                self.coyoteGames[ctx.guild_id] = Coyote()
                self.cy_members[ctx.guild_id] = Members()
                self.cy_members[ctx.guild_id].add_member(ctx.author)
            LOG.debug(f'追加:{ctx.author.display_name}')
            await ctx.edit_origin(content=f'{ctx.author.display_name}が参加しました!(参加人数:{self.cy_members[ctx.guild_id].len})', components=coyote_components)
        if ctx.custom_id == gamebuttons.CUSTOM_ID_LEAVE_COYOTE:
            if ctx.guild_id in self.cy_members:
                self.cy_members[ctx.guild_id].remove_member(ctx.author)
            else:
                self.coyoteGames[ctx.guild_id] = Coyote()
                self.cy_members[ctx.guild_id] = Members()
            LOG.debug(f'削除:{ctx.author.display_name}')
            await ctx.edit_origin(content=f'{ctx.author.display_name}が離脱しました!(参加人数:{self.cy_members[ctx.guild_id].len})', components=coyote_components)
        if ctx.custom_id == gamebuttons.CUSTOM_ID_PURGE_COYOTE:
            self.coyoteGames[ctx.guild_id] = Coyote()
            self.cy_members[ctx.guild_id] = Members()
            LOG.debug(f'参加者クリア:{ctx.author.display_name}')
            await ctx.edit_origin(content=f'参加者がクリアされました(参加人数:{self.cy_members[ctx.guild_id].len})', components=coyote_components)
        if ctx.custom_id == gamebuttons.CUSTOM_ID_START_COYOTE:
            if ctx.guild_id not in self.cy_members:
                msg = f'ゲームが始まっていません。`/start-coyote-game`でゲームを開始してください。'
                self.cy_members[ctx.guild_id] = Members()
                self.coyoteGames[ctx.guild_id] = Coyote()
                await ctx.edit_origin(content=msg, components=coyote_components)
                return
            if self.cy_members[ctx.guild_id].len < 2:
                msg = f'コヨーテを楽しむには2人以上のメンバーが必要です(現在、{self.cy_members[ctx.guild_id].len}人しかいません)'
                await ctx.edit_origin(content=msg, components=coyote_components)

                return
            await self.startCoyote(ctx)
            if self.coyoteGames[ctx.guild_id].start_description == 'Normal':
                """
                説明が程よいバージョン
                - コヨーテのルールが分かる程度に省略しています。
                """
                await self.coyoteLittleMessage(ctx)
            elif self.coyoteGames[ctx.guild_id].start_description == 'All':
                """
                説明が多いバージョン
                - 初心者はこちらのコマンドを実行してください。
                - コヨーテのルールが分かるように書いてありますが、一旦説明を見ながらゲームしてみると良いと思います。
                """
                await self.coyoteAllMessage(ctx)
            elif self.coyoteGames[ctx.guild_id].start_description == 'Nothing':
                """
                コヨーテを始めるコマンド（説明なし）
                - 上級者向けの機能です。ルールを説明されずとも把握している場合にのみ推奨します。
                """
                msg = self.coyoteGames[ctx.guild_id].create_description(True)
                await ctx.send(msg)
            await self.dealAndMessage(ctx)
        if ctx.custom_id == gamebuttons.CUSTOM_ID_START_COYOTE_SET_DECK:
            if ctx.guild_id not in self.cy_members:
                msg = f'ゲームが始まっていません。`/start-coyote-game-set-deck`でゲームを開始してください。'
                self.cy_members[ctx.guild_id] = Members()
                self.coyoteGames[ctx.guild_id] = Coyote()
                await ctx.edit_origin(content=msg, components=coyote_components)
                return
            if self.cy_members[ctx.guild_id].len < 2:
                msg = f'コヨーテを楽しむには2人以上のメンバーが必要です(現在、{self.cy_members[ctx.guild_id].len}人しかいません)'
                await ctx.edit_origin(content=msg, components=coyote_components)
                return
            self.coyoteGames[ctx.guild_id].set(self.cy_members[ctx.guild_id].get_members())
            self.coyoteGames[ctx.guild_id].shuffle()
            msg = self.coyoteGames[ctx.guild_id].create_description(True)
            await ctx.send(msg)
            await self.dealAndMessage(ctx)
        if ctx.custom_id == gamebuttons.CUSTOM_ID_DEAL_COYOTE:
            if await self.coyoteStartCheckNG(ctx):
                return
            await self.dealAndMessage(ctx)
        if ctx.custom_id == gamebuttons.CUSTOM_ID_DESC_CARD_COYOTE:
            if ctx.guild_id not in self.cy_members:
                self.coyoteGames[ctx.guild_id] = Coyote()
                self.cy_members[ctx.guild_id] = Members()
            msg = self.coyoteGames[ctx.guild_id].create_description_card()
            await ctx.edit_origin(content=msg)
        if ctx.custom_id == gamebuttons.CUSTOM_ID_DESC_TURN_COYOTE:
            if await self.coyoteStartCheckNG(ctx, True):
                return
            msg = self.coyoteGames[ctx.guild_id].create_description()
            await ctx.edit_origin(content=msg)

        # 大喜利
        ohgiri_components = [gamebuttons.oh_join_action_row,gamebuttons.oh_leave_action_row,gamebuttons.oh_start_action_row,gamebuttons.oh_purge_action_row]
        if ctx.custom_id == gamebuttons.CUSTOM_ID_JOIN_OHGIRI:
            if ctx.guild_id in self.oh_members:
                self.oh_members[ctx.guild_id].add_member(ctx.author)
            else:
                self.oh_members[ctx.guild_id] = Members()
                self.ohgiriGames[ctx.guild_id] = Ohgiri()
                self.ohgiriGames[ctx.guild_id].file_path = self.ohgiriGames['default'].file_path
                self.oh_members[ctx.guild_id].add_member(ctx.author)
            LOG.debug(f'追加:{ctx.author.display_name}')
            await ctx.edit_origin(content=f'{ctx.author.display_name}が参加しました!(参加人数:{self.oh_members[ctx.guild_id].len})', components=ohgiri_components)
        if ctx.custom_id == gamebuttons.CUSTOM_ID_LEAVE_OHGIRI:
            if ctx.guild_id in self.oh_members:
                self.oh_members[ctx.guild_id].remove_member(ctx.author)
            else:
                self.oh_members[ctx.guild_id] = Members()
                self.ohgiriGames[ctx.guild_id] = Ohgiri()
                self.ohgiriGames[ctx.guild_id].file_path = self.ohgiriGames['default'].file_path
            LOG.debug(f'削除:{ctx.author.display_name}')
            await ctx.edit_origin(content=f'{ctx.author.display_name}が離脱しました!(参加人数:{self.oh_members[ctx.guild_id].len})', components=ohgiri_components)
        if ctx.custom_id == gamebuttons.CUSTOM_ID_PURGE_OHGIRI:
            self.oh_members[ctx.guild_id] = Members()
            self.ohgiriGames[ctx.guild_id] = Ohgiri()
            LOG.debug(f'参加者クリア:{ctx.author.display_name}')
            await ctx.edit_origin(content=f'参加者がクリアされました(参加人数:{self.oh_members[ctx.guild_id].len})', components=ohgiri_components)
        if ctx.custom_id == gamebuttons.CUSTOM_ID_START_OHGIRI:
            if ctx.guild_id not in self.oh_members:
                msg = f'ゲームが始まっていません。`/start-ohgiri-game`でゲームを開始してください。'
                self.oh_members[ctx.guild_id] = Members()
                self.ohgiriGames[ctx.guild_id] = Ohgiri()
                self.ohgiriGames[ctx.guild_id].file_path = self.ohgiriGames['default'].file_path
                await ctx.edit_origin(content=msg, components=ohgiri_components)
                return
            if self.oh_members[ctx.guild_id].len < 2:
                msg = f'大喜利を楽しむには2人以上のメンバーが必要です(現在、{self.oh_members[ctx.guild_id].len}人しかいません)'
                await ctx.edit_origin(content=msg, components=ohgiri_components)
                return
            await self.startOhgiri(ctx)

    # NGワードゲーム機能
    @cog_ext.cog_slash(
    name='start-ng-word-game',
    # guild_ids=guilds,
    description='NGワードゲーム機能(禁止された言葉を喋ってはいけないゲーム)',
    options=[
        manage_commands.create_option(name='answer_minutes',
                                    description='投票開始までの時間（3などの正数。単位は「分」）を与えることができます。デフォルトは2分です',
                                    option_type=3,
                                    required=False)
    ])
    async def ngWordGame(self, ctx, answer_minutes=None):
        """
        コマンド実行者が参加しているボイスチャンネルでNGワードゲームを始めます（BOTからDMが来ますがびっくりしないでください）
        引数(answer_minutes)として終了までの時間（3などの正数。単位は「分」）を与えることができます。デフォルトは2分です。
        """
        if answer_minutes is None:
            answer_minutes = self.DEFAULT_TIME
        elif answer_minutes.isdecimal():
            answer_minutes = int(answer_minutes)
        else:
            answer_minutes = self.DEFAULT_TIME
        if ctx.guild_id in self.ng_members:
            self.ng_members[ctx.guild_id].set_minutes(answer_minutes)
        else:
            self.ng_members[ctx.guild_id] = Members()

        if answer_minutes > self.MAX_TIME:
            msg = f'NGワードゲームはそんなに長い時間するものではないです(現在、{answer_minutes}分を指定しています。{self.MAX_TIME}分以内にして下さい)'
            await ctx.send(msg, hidden=True)
            return

        msg =   'NGワードゲームを始めます(2人以上必要です)！　これからDMでそれぞれのNGワードを配ります！(**自分のNGワードのみ分かりません**)\n'\
                '配られた後に**雑談し、誰かがNGワードを口走ったら、「ドーン！！！」と指摘**してください。すぐさまNGワードが妥当か話し合いください(カッコがある場合は、どちらもNGワードです)。\n'\
                '妥当な場合、NGワード発言者はお休みです。残った人で続けます。**最後のひとりになったら勝利**です！！\n'\
                '参加する場合、以下のボタンを押してください。'
        await ctx.send(msg)
        await ctx.send('ボタン', components=[gamebuttons.ng_join_action_row])

    @cog_ext.cog_slash(
    name='start-coyote-game',
    # guild_ids=guilds,
    description='コヨーテ機能(場にある数値の合計を推測しつつ遊ぶゲーム)',
    options=[
        manage_commands.create_option(name='description',
                                    description='コヨーテを始める際の説明',
                                    option_type=3,
                                    required=False,
                                        choices=[
                                            manage_commands.create_choice(
                                            name='普通',
                                            value=Coyote.DESCRPTION_NORMAL),
                                            manage_commands.create_choice(
                                            name='詳しく',
                                            value=Coyote.DESCRPTION_ALL),
                                            manage_commands.create_choice(
                                            name='無し',
                                            value=Coyote.DESCRPTION_NOTHING)
                                        ])
    ])
    async def start(self, ctx, description: str = Coyote.DESCRPTION_NORMAL):
        msg = 'コヨーテを始めます(2人以上必要です)！\n参加する場合、以下のボタンを押してください。'
        await ctx.send(msg)
        await ctx.send('ボタン', components=[gamebuttons.cy_join_action_row])
        self.coyoteGames[ctx.guild_id] = Coyote()
        self.cy_members[ctx.guild_id] = Members()
        self.coyoteGames[ctx.guild_id].set_deck_flg = False
        self.coyoteGames[ctx.guild_id].start_description = description

    @cog_ext.cog_slash(
    name='start-coyote-game-set-deck',
    # guild_ids=guilds,
    description='【上級者向け】デッキを指定しコヨーテを開始 :例：`/start-coyote-game-set-deck 20,0(Night),-5,*2(Chief), Max->0(Fox),?(Cave)`',
    options=[
        manage_commands.create_option(name='deck',
                                    description='デッキを「,」(コンマ)で区切って指定(例：`/start-coyote-game-set-deck 20,0,0(Night),-5,*2(Chief), Max->0(Fox),?(Cave)`)',
                                    option_type=3,
                                    required=True)
    ])
    async def setDeckAndStart(self, ctx, deck=None):
        """
        デッキを指定してコヨーテを始めるコマンド（説明なし）
        - 上級者向けの機能です。ルールを説明されずとも把握している場合にのみ推奨します。
        - デッキを「,」(コンマ)で区切って指定します。二重引用符などは不要です。
        例：`/coyoteGame setDeckAndStart 20, 15, 15, 1, 1, 1, 1, 0, 0, 0, 0(Night), -5, -5, -10, *2(Chief), Max->0(Fox), ?(Cave), ?(Cave)`
        """
        msg = 'デッキを指定してコヨーテを始めます(2人以上必要です)！\n参加する場合、以下のボタンを押してください。'
        await ctx.send(msg)
        await ctx.send('ボタン', components=[gamebuttons.cy_join_action_row])
        self.coyoteGames[ctx.guild_id] = Coyote()
        self.cy_members[ctx.guild_id] = Members()
        self.coyoteGames[ctx.guild_id].setDeck(deck)

    @cog_ext.cog_slash(
    name='coyote-game-coyote',
    # guild_ids=guilds,
    description='コヨーテ！(前プレイヤーの数字がコヨーテの合計数を超えたと思った場合のコマンド)',
    options=[
        manage_commands.create_option(name='target_id',
                                    description='プレイヤーのID（@マークを打つと入力しやすい）',
                                    option_type=3,
                                    required=True)
        , manage_commands.create_option(name='number',
                                    description='前プレイヤーの宣言した数',
                                    option_type=3,
                                    required=True)
    ])
    async def coyote(self, ctx, target_id=None, number=0):
        """
        コヨーテ中に実行できる行動。「コヨーテ！」を行う
        - 「コヨーテ！」は前プレイヤーの宣言を疑う行動
        - 「前プレイヤーの宣言した数」が「実際にこの場にいるコヨーテの数よりも**大きい（オーバーした）**」と思う場合に実行してください
        引数は2つあり、どちらも必須です
        - 1.プレイヤーのID（@マークを打つと入力しやすい）
        - 2.前プレイヤーの宣言した数
        """
        if number.isdecimal():
            number = int(number)
        else:
            number = 0

        if target_id is None:
            msg = '「コヨーテする相手」(@で指定)と「コヨーテを言われた人の数字」を指定してください。例：`coyote-game-coyote @you 99`'
            await ctx.send(msg, hidden=True)
            return
        if number <= 0:
            msg = '「コヨーテを言われた人の数字」は「1以上の整数」(0もダメです)を指定してください。例：`coyote-game-coyote @you 99`'
            await ctx.send(msg, hidden=True)
            return
        if await self.coyoteStartCheckNG(ctx):
            return
        # コヨーテ！した相手のメンバー情報を取得。取得できない場合はエラーを返す
        target_id = re.sub(r'[<@!>]', '', target_id)
        if target_id.isdecimal():
            target_id = int(target_id)
            you = ctx.guild.get_member(target_id)
        else:
            # IDから取得を試みる
            keys = [k for k, v in self.coyoteGames[ctx.guild_id].members.items() if v.id == str(target_id).upper()]
            if len(keys) == 0:
                msg = '「コヨーテする相手」(@で指定するか、IDで指定(aなど))と「コヨーテを言われた人の数字」を指定してください。例：`coyote-game-coyote @you 99`'
                await ctx.send(msg)
                return
            else:
                you = keys.pop()
        if you not in self.coyoteGames[ctx.guild_id].members:
            msg = 'ゲームに存在する相手を選び、「コヨーテ！」してください(ゲームしている相手にはいません)。'
            await ctx.send(msg)
            return

        self.coyoteGames[ctx.guild_id].coyote(ctx.author, you, number)
        await ctx.send(self.coyoteGames[ctx.guild_id].description)
        await ctx.send('ボタン', components=[gamebuttons.cy_deal_action_row, gamebuttons.cy_desc_card_action_row, gamebuttons.cy_desc_turn_action_row])

    @cog_ext.cog_slash(
    name='coyote-game-deal',
    # guild_ids=guilds,
    description='ディール(次のターンを始める)')
    async def deal(self, ctx):
        """
        コヨーテ中に実行できる行動。カードを引いて、プレイヤーに配ります
        """
        if await self.coyoteStartCheckNG(ctx):
            return
        await self.dealAndMessage(ctx)

    @cog_ext.cog_slash(
    name='coyote-game-description',
    # guild_ids=guilds,
    description='状況説明orカード能力の説明します',
    options=[
        manage_commands.create_option(name='description_target',
                                            description='状況説明or状況説明(ネタバレ)orカード能力説明',
                                            option_type=3,
                                            required=True,
                                            choices=[
                                                manage_commands.create_choice(
                                                name='状況説明(ターン数,HP,山札の数,捨て札の数,捨て札)',
                                                value='Description-Normal'),
                                                manage_commands.create_choice(
                                                name='【ネタバレ】状況説明(全て/場のカードも分かる)',
                                                value='Description-All'),
                                                manage_commands.create_choice(
                                                name='カードの説明',
                                                value='Description-Cards')
                                            ])
        , manage_commands.create_option(name='reply_is_hidden',
                                            description='Botの実行結果を全員に見せるどうか(他の人に説明を見せたい場合、全員に見せる方がオススメです))',
                                            option_type=3,
                                            required=False,
                                            choices=[
                                                manage_commands.create_choice(
                                                name='自分のみ',
                                                value='True'),
                                                manage_commands.create_choice(
                                                name='全員に見せる',
                                                value='False')
                                            ])
    ])
    async def description(self, ctx, description_target, reply_is_hidden:str = None):
        hidden = True if reply_is_hidden == 'True' else False
        if description_target == 'Description-Cards':
            """カードの能力を説明します。"""
            msg = self.coyoteGames[ctx.guild_id].create_description_card()
            await ctx.send(msg, hidden=hidden)
            return
        else:
            if await self.coyoteStartCheckNG(ctx, True):
                return
            if description_target == 'Description-Normal':
                """
                状況を説明します。
                - ターン数、生き残っている人の数、それぞれのHP
                - 山札の数、捨て札の数、捨て札の中身
                """
                msg = self.coyoteGames[ctx.guild_id].create_description()
            elif description_target == 'Description-All':
                """
                状況を全て説明します（場のカードもわかります）。
                - ターン数、生き残っている人の数、それぞれのHP
                - 山札の数、山札の中身、捨て札の数、捨て札の中身、場のカード
                """
                msg = self.coyoteGames[ctx.guild_id].create_description(True)
            await ctx.send(msg, hidden=hidden)

    @cog_ext.cog_slash(
    name='roll',
    # guild_ids=guilds,
    description='ダイスを振る(さいころを転がす)',
    options=[
        manage_commands.create_option(name='dice_and_num',
                                    description='`/roll 1d6`のように、左側にダイスの数、右側にダイスの種類(最大値)を指定してください',
                                    option_type=3,
                                    required=True)
        , manage_commands.create_option(name='reply_is_hidden',
                                    description='Botの実行結果を全員に見せるどうか(デフォルトは全員に見せる))',
                                    option_type=3,
                                    required=False,
                                    choices=[
                                        manage_commands.create_choice(
                                        name='自分のみ',
                                        value='True'),
                                        manage_commands.create_choice(
                                        name='全員に見せる',
                                        value='False')
                                    ])
    ])
    async def roll(self, ctx, dice_and_num, reply_is_hidden:str = None):
        """
        ダイスを振る(さいころを転がす)コマンド
        - `/roll 1d6`のように、左側にダイスの数、右側にダイスの種類(最大値)を指定してください
        """
        hidden = True if reply_is_hidden == 'True' else False
        default_error_msg = '`/roll 1d6`のように指定してください。'
        if dice_and_num is None:
            await ctx.send(default_error_msg, hidden=False)
            return
        diceAndNum = str(dice_and_num).lower()
        if 'd' not in diceAndNum:
            msg = 'dが必ず必要です。'
            await ctx.send(msg + default_error_msg, hidden=False)
            return
        list = str(diceAndNum).split('d')
        if len(list) != 2:
            await ctx.send(default_error_msg, hidden=False)
            return
        elif len(list) == 2:
            msg = ''
            sum = 0
            # ダイスの数、ダイスの最大値についてのチェックと数値化
            if list[0].isdecimal():
                dice_num = int(list[0])
            else:
                msg = 'dの左側が数字ではありません。'
                await ctx.send(msg + default_error_msg, hidden=False)
                return
            if list[1].isdecimal():
                max_num = int(list[1])
            else:
                msg = 'dの右側が数字ではありません。'
                await ctx.send(msg + default_error_msg, hidden=False)
                return
            if max_num < 1 or dice_num < 1:
                msg = 'dの左右は1以上である必要があります。'
                await ctx.send(msg + default_error_msg, hidden=False)
                return
            for i in range(dice_num):
                value = random.randint(1, max_num)
                msg += f' {value}'
                sum += value
            else:
                if dice_num > 1:
                    msg += f' → {sum}'
                await ctx.send(msg, hidden=hidden)

    async def startCoyote(self, ctx):
        self.coyoteGames[ctx.guild_id].setInit(self.cy_members[ctx.guild_id].get_members())
        self.coyoteGames[ctx.guild_id].shuffle()

    async def dealAndMessage(self, ctx):
        self.coyoteGames[ctx.guild_id].deal()
        start_msg = await ctx.send(f'カードを配りました。DMをご確認ください。{self.coyoteGames[ctx.guild_id].description}')
        dm_msg_all = ''
        # 全員分のメッセージを作成
        for player in self.coyoteGames[ctx.guild_id].members:
            dm_msg_all += f'{player.display_name}さん: {self.coyoteGames[ctx.guild_id].members[player].card}\n'
        # DM用メッセージを作成(送付する相手の名前が記載された行を削除)
        for player in self.coyoteGames[ctx.guild_id].members:
            dm = await player.create_dm()
            rpl_msg_del = f'{player.display_name}さん:.+\n'
            dm_msg = re.sub(rpl_msg_del, '', dm_msg_all)
            await dm.send(f'{player.mention}さん 他の人のコヨーテカードはこちらです！\n{dm_msg}開始メッセージへのリンク: {start_msg.jump_url}')
        self.coyoteGames[ctx.guild_id].description = ''

    async def coyoteAllMessage(self, ctx):
        msg1 = 'コヨーテ：ゲーム目的\n**自分以外のプレイヤーのカード(DMに送られる)を見て、少なくとも何匹のコヨーテがこの場にいるかを推理します。**\n'\
            'もしも宣言した数だけ居なかったら......コヨーテに命を奪われてしまいます！ インディアン、嘘つかない。コヨーテだって、嘘が大キライなのです。\n'\
            'ライフは一人3ポイントあります。3回殺されたらゲームから退場します。\n'\
            'コヨーテの鳴き声（想像してね）が上手いプレイヤーから始めます。'
        await ctx.send(msg1)

        msg2 = '最初のプレイヤーはDMに送られる他の人のカードを見て、この場に「少なくとも」何匹のコヨーテがいるか(DMを見て数字を加算し)推理し、コヨーテの数を宣言します。\n'\
            '★宣言する数に上限はありませんが、**1以上の整数である必要**があります（つまり、0や負数はダメです）\n'\
            'ゲームは時計回りに進行(ボイスチャンネルを下に進むこと)します。\n'\
            '次のプレイヤーは次のふたつのうち、「どちらか」の行動をとってください。\n'\
            '1: 数字を上げる → 前プレイヤーの宣言した数が実際にこの場にいるコヨーテの数**以下（オーバー）していない**と思う場合、**前プレイヤーより大きな数**を宣言します。\n'\
            '2: 「コヨーテ！」→ 前プレイヤーの宣言を疑います。つまり、前プレイヤーの宣言した数が実際にこの場にいるコヨーテの数よりも**大きい（オーバーした）**と思う場合、**「コヨーテ！」**と宣言します\n'\
            '2の場合、例：`coyote-game-coyote @you 99`のように(`@you`はidでもOK)**Discordに書き込んで**ください！（Botが結果を判定します！）\n'\
            '**誰かが「コヨーテ！」と宣言するまで**、時計回りで順々に交代しながら宣言する数字を上げていきます\n'
        await ctx.send(msg2)

        msg3 = '「コヨーテ！」と宣言された場合、直前のプレイヤーが宣言した数が当たっていたかどうか判定します。\n'\
            '★前述の通り、Botが計算します（例：`coyote-game-coyote @you 99`のように書き込んでくださいね）\n'\
            'まず基本カードを集計したあと、特殊カード分を計算します。\n'\
            '「コヨーテ！」を**宣言された数がコヨーテの合計数をオーバー**していた場合、**「コヨーテ！」を宣言した人**の勝ち（数値を宣言した人の負け）\n'\
            '「コヨーテ！」を**宣言された数がコヨーテの合計数以下**の場合、**数値を宣言**した人の勝ち（「コヨーテ！」を宣言した人の負け）\n'\
            '負けたプレイヤーはダメージを受けます（ライフが減ります）。\n'\
            '使ったカードを捨て札にして、次の回を始めます（**今回負けた人から開始**します）。\n'\
            '次の回を始めるには、`/coyote-game-deal `をDiscordに書き込んでください。\n'\
            '負けたプレイヤーがその回を最後に**ゲームから脱落した場合、その回の勝者から**次の回を始めます。\n'\
            'ライフが0になったプレイヤーはゲームから脱落します。最後まで生き残ったプレイヤーが勝利です。\n'\
            'なお、コヨーテは絶賛販売中です(1,800円くらい)。気に入った方はぜひ買って遊んでみてください（このBotは許可を得て作成したものではありません）。販売:合同会社ニューゲームズオーダー, 作者:Spartaco Albertarelli, 画:TANSANFABRIK\n'\
            'サイト: <http://www.newgamesorder.jp/games/coyote>'
        await ctx.send(msg3)

        msg4 = self.coyoteGames[ctx.guild_id].create_description(True)
        await ctx.send(msg4)
        card_msg = self.coyoteGames[ctx.guild_id].create_description_card()
        await ctx.send(card_msg)

    async def coyoteLittleMessage(self, ctx):
        msg = 'コヨーテ：ゲーム目的\n**自分以外のプレイヤーのカード(DMに送られる)を見て、少なくとも何匹のコヨーテがこの場にいるかを推理します。**\n'\
            'もしも宣言した数だけ居なかったら......コヨーテに命を奪われてしまいます！ インディアン、嘘つかない。コヨーテだって、嘘が大キライなのです。\n'\
            'ライフは一人3ポイントあります。3回殺されたらゲームから退場します。\n'\
            '最初のプレイヤー:「少なくとも」何匹のコヨーテがいるか推理し、コヨーテの数を宣言(**1以上の整数**)します。\n'\
            'ゲームは時計回りに進行(ボイスチャンネルを下に進むこと)\n'\
            '次のプレイヤー：は次のふたつのうち、「どちらか」の行動をとってください。\n'\
            '1: 数字を上げる → 前プレイヤーの宣言した数が実際にこの場にいるコヨーテの数**以下（オーバー）していない**と思う場合、**前プレイヤーより大きな数**を宣言します。\n'\
            '2: 「コヨーテ！」→ 前プレイヤーの宣言を疑います。つまり、前プレイヤーの宣言した数が実際にこの場にいるコヨーテの数よりも**大きい（オーバーした）**と思う場合、**「コヨーテ！」**と宣言します\n'\
            '2の場合、例：`coyote-game-coyote @you 99`のように(`@you`はidでもOK)**Discordに書き込んで**ください！（Botが結果を判定します！）\n'\
            '**誰かが「コヨーテ！」と宣言するまで**、時計回り(ボイスチャンネルを下に進む)で順々に交代しながら宣言する**数字を上げて**いきます\n'\
            '次の回を始めるには、`/coyote-game-deal `をDiscordに書き込んでください（**今回負けた人から開始**します）。\n'\
            '負けたプレイヤーがその回を最後に**ゲームから脱落した場合、その回の勝者から**次の回を始めます。\n'\
            'ライフが0になったプレイヤーはゲームから脱落します。最後まで生き残ったプレイヤーが勝利です。\n'\
            'なお、コヨーテは絶賛販売中です(1,800円くらい)。気に入った方はぜひ買って遊んでみてください（このBotは許可を得て作成したものではありません）。販売:合同会社ニューゲームズオーダー, 作者:Spartaco Albertarelli, 画:TANSANFABRIK\n'\
            'サイト: <http://www.newgamesorder.jp/games/coyote>'
        await ctx.send(msg)
        msg2 = self.coyoteGames[ctx.guild_id].create_description(True)
        await ctx.send(msg2)
        card_msg = self.coyoteGames[ctx.guild_id].create_description_card()
        await ctx.send(card_msg)

    async def coyoteStartCheckNG(self, ctx, desc=False):
        if ctx.guild_id not in self.coyoteGames or self.coyoteGames[ctx.guild_id] is None or (len(self.coyoteGames[ctx.guild_id].members) <= 1 and not desc):
            msg = 'コヨーテを始めてから実行できます。コヨーテを始めたい場合は、`/start-coyote-game`を入力してください。'
            await ctx.send(msg, hidden=True)
            return True
        # 終わった後に説明が見たい場合は許す
        elif len(self.coyoteGames[ctx.guild_id].members) == 1 and desc:
            return False
        else:
            return False

    @cog_ext.cog_slash(
    name='start-ohgiri-game',
    # guild_ids=guilds,
    description='大喜利を開始(親が好みのネタをカードから選んで優勝するゲーム)',
    options=[
        manage_commands.create_option(name='win_point',
                                    description='勝利扱いとするポイント(デフォルトは5ポイント)',
                                    option_type=3,
                                    required=False)
    ])
    async def start_ohgiriGame(self, ctx, win_point=5):
        """
        大喜利を開始
        - win_point: 勝利扱いとするポイント(デフォルトは5ポイント)
        """
        # win_pointが数字でなかったり、MAX_WIN_POINTを超えたり、0以下の場合は、デフォルトの値を使用する
        self.ohgiriGames[ctx.guild_id] = Ohgiri()
        self.ohgiriGames[ctx.guild_id].file_path = self.ohgiriGames['default'].file_path
        self.oh_members[ctx.guild_id] = Members()
        if not str(win_point).isdecimal or 1 > int(win_point) or int(win_point) > self.ohgiriGames[ctx.guild_id].MAX_WIN_POINT:
            win_point = self.ohgiriGames[ctx.guild_id].DEFAULT_WIN_POINT
        self.ohgiriGames[ctx.guild_id].win_point = int(win_point)

        msg =   '大喜利を始めます(2人以上必要です)！\n参加する場合、以下のボタンを押してください。'
        await ctx.send(msg)
        await ctx.send('ボタン', components=[gamebuttons.oh_join_action_row])

    @cog_ext.cog_slash(
    name='ohgiri-game-answer',
    # guild_ids=guilds,
    description='【子】回答者がお題に提出する回答を設定',
    options=[
        manage_commands.create_option(name='card_id',
                                    description='回答として設定する値(数字で指定)',
                                    option_type=3,
                                    required=True)
        , manage_commands.create_option(name='second_card_id',
                                    description='回答として設定する値(数字で指定)',
                                    option_type=3,
                                    required=False)
    ])
    async def answer(self, ctx, card_id=None, second_card_id=None):
        """
        回答者が回答として提出するカードを設定
        - ans_number: 回答として設定する値(数字で指定)
        例:`/ohgiri-game-answer 1`
        """
        # 始まっているかのチェック
        if ctx.guild_id not in self.ohgiriGames or len(self.ohgiriGames[ctx.guild_id].members) == 0 or self.ohgiriGames[ctx.guild_id].game_over:
            await ctx.send('ゲームが起動していません！', hidden=True)
        # コマンド実行者のチェック(親は拒否)
        elif ctx.author == self.ohgiriGames[ctx.guild_id].house:
            await ctx.send('親は回答を提出できません！', hidden=True)
        # 引数が設定されているかチェック
        elif card_id is None:
            await ctx.send('引数`card_id`を指定してください！', hidden=True)
        # 参加者かチェック
        elif self.ohgiriGames[ctx.guild_id].members.get(ctx.author) is None:
            await ctx.send(f'{ctx.author.display_name}は、参加者ではありません！', hidden=True)
        # コマンド実行者が所持しているかチェック
        elif card_id not in self.ohgiriGames[ctx.guild_id].members[ctx.author].cards:
            await ctx.send(f'{card_id}は{ctx.author.display_name}の所持しているカードではありません！', hidden=True)
        elif self.ohgiriGames[ctx.guild_id].required_ans_num == 1 and second_card_id is not None:
            await ctx.send('お題で2つ設定するように指定がないので、回答は1つにしてください！', hidden=True)
        elif self.ohgiriGames[ctx.guild_id].required_ans_num == 2 and second_card_id is None:
            await ctx.send('2つめの引数`second_card_id`が設定されていません！(もう一つ数字を設定してください)', hidden=True)
        elif self.ohgiriGames[ctx.guild_id].required_ans_num == 2 and second_card_id not in self.ohgiriGames[ctx.guild_id].members[ctx.author].cards:
            await ctx.send(f'{second_card_id}は{ctx.author.display_name}の所持しているカードではありません！', hidden=True)
        else:
            LOG.debug('回答を受け取ったよ！')
            # 既に回答したメンバーから再度回答を受けた場合、入れ替えた旨お知らせする
            if self.ohgiriGames[ctx.guild_id].members[ctx.author].answered:
                await ctx.send(f'{ctx.author.mention} 既に回答を受け取っていたため、そちらのカードと入れ替えますね！', hidden=True)
            # カードの受領処理
            self.ohgiriGames[ctx.guild_id].receive_card(card_id, ctx.author, second_card_id)
            # 回答者が出そろった場合、場に出す(親は提出できないので引く)
            if (len(self.ohgiriGames[ctx.guild_id].members) - 1)  == len(self.ohgiriGames[ctx.guild_id].field):
                self.ohgiriGames[ctx.guild_id].show_answer()
                LOG.info('回答者が出揃ったので、場に展開！')
                msg = self.ohgiriGames[ctx.guild_id].description + f'\n{self.ohgiriGames[ctx.guild_id].house.mention} 回答を読み上げたのち、好きな回答を`/ohgiri-game-choice <数字>`で選択してください！'
                await ctx.send(msg)
            else:
                await ctx.send('回答ありがとうございます', hidden=True)

    @cog_ext.cog_slash(
    name='ohgiri-game-choice',
    # guild_ids=guilds,
    description='【親】回答者がお題に提出する回答を設定',
    options=[
        manage_commands.create_option(name='ans_index',
                                    description='気に入ったカードの回答番号を設定する値(数字で指定)',
                                    option_type=3,
                                    required=True)
    ])
    async def choice(self, ctx, ans_index=None):
        """
        親が気に入ったカードを選択する
        - ans_index: 気に入ったカードの回答番号を設定する値(数字で指定)
        例:`/ohgiri-game-choice 1`
        """
        # 始まっているかのチェック
        if ctx.guild_id not in self.ohgiriGames or len(self.ohgiriGames[ctx.guild_id].members) == 0 or self.ohgiriGames[ctx.guild_id].game_over:
            await ctx.send('ゲームが起動していません！', hidden=True)
        # コマンド実行者のチェック(親以外は拒否)
        elif ctx.author != self.ohgiriGames[ctx.guild_id].house:
            await ctx.send('親以外が秀逸な回答を選択することはできません！', hidden=True)
        elif ans_index is None or not ans_index.isdecimal():
            await ctx.send('`ans_index`が選択されていません！', hidden=True)
        # 回答が出揃っているかチェック
        elif (len(self.ohgiriGames[ctx.guild_id].members) - 1)  > len(self.ohgiriGames[ctx.guild_id].field):
            await ctx.send(f'回答が出揃っていません。あと{len(self.ohgiriGames[ctx.guild_id].members) - len(self.ohgiriGames[ctx.guild_id].field) -1}人提出が必要です。', hidden=True)

        else:
            # 場にある数かどうかのチェック
            if int(ans_index) > len(self.ohgiriGames[ctx.guild_id].members) - 1:
                await ctx.send(f'{ans_index}は場に出ている最大の選択数({len(self.ohgiriGames[ctx.guild_id].members) - 1})を超えています！', hidden=True)
                return

            # 結果を表示
            self.ohgiriGames[ctx.guild_id].choose_answer(ans_index)
            await ctx.send(self.ohgiriGames[ctx.guild_id].description)

            # ゲームが終了していない場合、次のターンを開始
            if not self.ohgiriGames[ctx.guild_id].game_over:
                await self.dealAndNextGame(ctx)

    @cog_ext.cog_slash(
    name='ohgiri-game-description',
    # guild_ids=guilds,
    description='現在の状況を説明')
    async def description_ohgiriGame(self, ctx):
        """現在の状況を説明します"""
        # 始まっているかのチェック
        if ctx.guild_id not in self.ohgiriGames or len(self.ohgiriGames[ctx.guild_id].members) == 0:
            await ctx.send('ゲームが起動していません！', hidden=True)
            return
        self.ohgiriGames[ctx.guild_id].show_info()
        await ctx.send(self.ohgiriGames[ctx.guild_id].description)

    @cog_ext.cog_slash(
    name='ohgiri-game-discard_hand',
    # guild_ids=guilds,
    description='ポイントを1点減点し、手札をすべて捨て、山札からカードを引く(いい回答カードがない時に使用ください)',
    options=[
        manage_commands.create_option(name='ans_index',
                                    description='気に入ったカードの回答番号を設定する値(数字で指定)',
                                    option_type=3,
                                    required=False)
    ])
    async def discard_hand(self, ctx):
        """
        ポイントを1点減点し、手札をすべて捨て、山札からカードを引く（いい回答カードがない時に使用ください）
        """
        # 始まっているかのチェック
        if ctx.guild_id not in self.ohgiriGames or len(self.ohgiriGames[ctx.guild_id].members) == 0 or self.ohgiriGames[ctx.guild_id].game_over:
            await ctx.send('ゲームが起動していません！', hidden=True)
            return
        self.ohgiriGames[ctx.guild_id].discard_hand(ctx.author)
        await ctx.send(self.ohgiriGames[ctx.guild_id].description, hidden=True)
        await self.send_ans_dm(ctx, ctx.author)

    async def startOhgiri(self, ctx):
        # 参加者と手札の数を設定
        await self.ohgiriGames[ctx.guild_id].setting(self.oh_members[ctx.guild_id].get_members(), 12, self.ohgiriGames[ctx.guild_id].win_point)
        self.ohgiriGames[ctx.guild_id].shuffle()
        msg = 'お題が提供されるので**「親」はお題を声に出して読み上げ**てください（"○○"は「まるまる」、"✕✕"は「ばつばつ」と読む）。ほかのプレイヤーは読み上げられた**お題に相応しいと思う回答**を`/ohgiri-game-answer <数字>`で選びます。\n'\
            + '全員が回答したら、**「親」はもっとも秀逸な回答**を`/ohgiri-game-choice <番号>`で選択します。「親」から選ばれたプレイヤーは1点もらえます。ただし、山札から1枚カードが混ざっており、それを選択すると親はポイントが減算されます。\n'\
            + f'今回のゲームの勝利点は{self.ohgiriGames[ctx.guild_id].win_point}点です。'
        await ctx.send(msg)
        await self.dealAndNextGame(ctx)

    async def dealAndNextGame(self, ctx):
        self.ohgiriGames[ctx.guild_id].deal()

        # お題を表示
        odai_msg = await ctx.send(f'お題：{self.ohgiriGames[ctx.guild_id].odai}')

        # DMで回答カードを示す
        for player in self.ohgiriGames[ctx.guild_id].members:
            await self.send_ans_dm(ctx, player, odai_msg)

        msg = f'カードを配りました。DMをご確認ください。{self.ohgiriGames[ctx.guild_id].description}\n親は{self.ohgiriGames[ctx.guild_id].house.display_name}です！'
        if self.ohgiriGames[ctx.guild_id].required_ans_num == 2:
            msg += '\n(回答は**2つ**設定するようにしてください！ 例:`/ohgiri-game-answer 1 2`'
        await ctx.send(msg)

    async def send_ans_dm(self, ctx, player: discord.member, odai_msg:discord.message=None):
        dm_msg  = ''
        if self.ohgiriGames[ctx.guild_id].house == player:
            dm_msg = 'あなたは親です！　カード選択はできません。回答が出揃った後、お好みの回答を選択ください。\n'
        dm = await player.create_dm()
        for card_id in self.ohgiriGames[ctx.guild_id].members[player].cards:
            card_message = self.ohgiriGames[ctx.guild_id].ans_dict[card_id]
            dm_msg += f'{card_id}: {card_message}\n'
        # お題のメッセージが指定されている場合、リンクを付与
        if odai_msg is not None:
            dm_msg += f'お題へのリンク: {odai_msg.jump_url}'
        await dm.send(f'{player.mention}さん あなたの手札はこちらです！\n{dm_msg}')

    # poll機能
    @cog_ext.cog_slash(
    name='simple-poll',
    # guild_ids=guilds,
    description='簡易的な投票機能です(/で分割されます。「/がない」場合と「/がある」場合で動作が変わります)',
    options=[
        manage_commands.create_option(name='poll_message',
                                    description='タイトル/回答1/回答2/...のスタイルで入力ください(タイトルのみの場合、Yes/Noで投票されます)',
                                    option_type=3,
                                    required=True)
    ])
    async def poll(self, ctx, poll_message):
        """
        このコマンドを実行すると、リアクションを利用し簡易的な投票ができます。
        ＊1人1票にはできません。リアクションの制限で20を超える設問は不可能です。
        """
        usage = '/simple-pollの使い方\n複数選択（1〜20まで）: \n `/simple-poll 今日のランチは？/お好み焼き/カレーライス`\n Yes/No: \n`/poll 明日は晴れる？`'
        args_all = poll_message.split('/')
        msg = f'🗳 **{args_all[0]}**'
        if len(args_all)  == 1:
            message = await ctx.send(msg)
            await message.add_reaction('⭕')
            await message.add_reaction('❌')
        elif len(args_all) > 21:
            await ctx.send(f'複数選択の場合、引数は1〜20にしてください。（{len(args_all)-1}個与えられています。）')
        else:
            args = args_all[1:]
            embed = discord.Embed()
            for  emoji, arg in zip(POLL_CHAR, args):
                embed.add_field(name=emoji, value=arg) # inline=False
            message = await ctx.send(msg, embed=embed)

            for  emoji, arg in zip(POLL_CHAR, args):
                await message.add_reaction(emoji)

    @commands.Cog.listener()
    async def on_slash_command_error(self, ctx, ex):
        '''
        slash_commandでエラーが発生した場合の動く処理
        '''
        try:
            raise ex
        except discord.ext.commands.PrivateMessageOnly:
            await ctx.send(f'エラーが発生しました(DM(ダイレクトメッセージ)でのみ実行できます)', hidden = True)
        except discord.ext.commands.NoPrivateMessage:
            await ctx.send(f'エラーが発生しました(ギルドでのみ実行できます(DMやグループチャットでは実行できません))', hidden = True)
        except discord.ext.commands.NotOwner:
            await ctx.send(f'エラーが発生しました(Botのオーナーのみ実行できます)', hidden = True)
        except discord.ext.commands.MissingPermissions:
            if ex.missing_perms[0] == 'administrator':
                await ctx.send(f'エラーが発生しました(ギルドの管理者のみ実行できます)', hidden = True)
        except:
            await ctx.send(f'エラーが発生しました({ex})', hidden = True)

    async def delayedMessage(self, ctx, messsage, delayed_seconds=None):
        await asyncio.sleep(delayed_seconds)
        await ctx.send(messsage)

def setup(bot):
    bot.add_cog(GameCog(bot)) # GameCogにBotを渡してインスタンス化し、Botにコグとして登録する
