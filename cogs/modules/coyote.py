import random
import discord
import re
import string
from logging import getLogger
from .members import Members
from typing import  Optional


LOG = getLogger(__name__)

class CoyoteStart(discord.ui.View):
    def __init__(self, cy_members, coyoteGames, msg, description):
        super().__init__(timeout=300)
        self.cy_members = cy_members
        self.coyoteGames = coyoteGames
        self.msg = msg
        self.description = description

    @discord.ui.button(label='参加する', style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.guild_id in self.cy_members:
            self.cy_members[interaction.guild_id].add_member(interaction.user)
        else:
            self.coyoteGames[interaction.guild_id] = Coyote()
            self.cy_members[interaction.guild_id] = Members()
            self.cy_members[interaction.guild_id].add_member(interaction.user)
        LOG.debug(f'追加:{interaction.user.display_name}')
        await interaction.response.edit_message(content=f'{self.msg}\n\n{interaction.user.display_name}が参加しました!(参加人数:{self.cy_members[interaction.guild_id].len})', view=self)

    @discord.ui.button(label='離脱する', style=discord.ButtonStyle.red)
    async def leave(self, interaction, button: discord.ui.Button):
        if interaction.guild_id in self.cy_members:
            self.cy_members[interaction.guild_id].remove_member(interaction.user)
        else:
            self.coyoteGames[interaction.guild_id] = Coyote()
            self.cy_members[interaction.guild_id] = Members()
        LOG.debug(f'削除:{interaction.user.display_name}')
        await interaction.response.edit_message(content=f'{self.msg}\n\n{interaction.user.display_name}が離脱しました!(参加人数:{self.cy_members[interaction.guild_id].len})', view=self)

    @discord.ui.button(label='開始する', style=discord.ButtonStyle.blurple)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.guild_id not in self.cy_members:
            msg = f'ゲームが始まっていません。`/start-coyote-game`でゲームを開始してください。'
            self.coyoteGames[interaction.guild_id] = Coyote()
            self.cy_members[interaction.guild_id] = Members()
            self.coyoteGames[interaction.guild_id].set_deck_flg = False
            await interaction.response.edit_message(content=msg, view=self)
            return
        if self.cy_members[interaction.guild_id].len < 2:
            msg = f'コヨーテを楽しむには2人以上のメンバーが必要です(現在、{self.cy_members[interaction.guild_id].len}人しかいません)'
            await interaction.response.edit_message(content=msg, view=self)
            return
        await self.startCoyote(interaction)

    @discord.ui.button(label='デッキを構築して開始する', style=discord.ButtonStyle.red)
    async def start_deck(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.guild_id not in self.cy_members:
            msg = f'ゲームが始まっていません。`/start-coyote-game`でゲームを開始してください。'
            self.coyoteGames[interaction.guild_id] = Coyote()
            self.cy_members[interaction.guild_id] = Members()
            self.coyoteGames[interaction.guild_id].set_deck_flg = False
            await interaction.response.edit_message(content=msg, view=self)
            return
        if self.cy_members[interaction.guild_id].len < 2:
            msg = f'コヨーテを楽しむには2人以上のメンバーが必要です(現在、{self.cy_members[interaction.guild_id].len}人しかいません)'
            await interaction.response.edit_message(content=msg, view=self)
            return
        await interaction.response.send_modal(CoyoteDeckModal(self))

    @discord.ui.button(label='参加者をクリアする', style=discord.ButtonStyle.grey)
    async def clear(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.coyoteGames[interaction.guild_id] = Coyote()
        self.cy_members[interaction.guild_id] = Members()
        LOG.debug(f'参加者クリア:{interaction.user.display_name}')
        await interaction.response.edit_message(content=f'参加者がクリアされました(参加人数:{self.cy_members[interaction.guild_id].len})', view=self)

    async def startCoyote(self, interaction: discord.Interaction):
        self.coyoteGames[interaction.guild_id].setInit(self.cy_members[interaction.guild_id].get_members())
        self.coyoteGames[interaction.guild_id].start_description = self.description
        self.coyoteGames[interaction.guild_id].shuffle()
        if self.coyoteGames[interaction.guild_id].start_description == 'Normal':
            """
            説明が程よいバージョン
            - コヨーテのルールが分かる程度に省略しています。
            """
            await self.coyoteLittleMessage(interaction)
        elif self.coyoteGames[interaction.guild_id].start_description == 'All':
            """
            説明が多いバージョン
            - 初心者はこちらのコマンドを実行してください。
            - コヨーテのルールが分かるように書いてありますが、一旦説明を見ながらゲームしてみると良いと思います。
            """
            await self.coyoteAllMessage(interaction)
        elif self.coyoteGames[interaction.guild_id].start_description == 'Nothing':
            """
            コヨーテを始めるコマンド（説明なし）
            - 上級者向けの機能です。ルールを説明されずとも把握している場合にのみ推奨します。
            """
            msg = self.coyoteGames[interaction.guild_id].create_description(True)
            await interaction.response.send_message(msg)
        await self.dealAndMessage(interaction)

    async def dealAndMessage(self, interaction: discord.Interaction):
        self.coyoteGames[interaction.guild_id].deal()
        # ボタン(相手のカードを表示する、コヨーテ！、カード能力説明、状況説明、ネタバレ説明)を作成
        view = CoyoteAnswer(self.coyoteGames[interaction.guild_id])
        await interaction.followup.send(f'カードを配りました。「相手のカードを表示する」ボタンを押してご確認ください。{self.coyoteGames[interaction.guild_id].description}', view=view)

    async def coyoteAllMessage(self, interaction: discord.Interaction):
        msg1 = 'コヨーテ：ゲーム目的\n**自分以外のプレイヤーのカード(DMに送られる)を見て、少なくとも何匹のコヨーテがこの場にいるかを推理します。**\n'\
            'もしも宣言した数だけ居なかったら......コヨーテに命を奪われてしまいます！ インディアン、嘘つかない。コヨーテだって、嘘が大キライなのです。\n'\
            'ライフは一人3ポイントあります。3回殺されたらゲームから退場します。\n'\
            'コヨーテの鳴き声（想像してね）が上手いプレイヤーから始めます。'
        await interaction.response.send_message(msg1)

        msg2 = '最初のプレイヤーはDMに送られる他の人のカードを見て、この場に「少なくとも」何匹のコヨーテがいるか(DMを見て数字を加算し)推理し、コヨーテの数を宣言します。\n'\
            '★宣言する数に上限はありませんが、**1以上の整数である必要**があります（つまり、0や負数はダメです）\n'\
            'ゲームは時計回りに進行(ボイスチャンネルを下に進むこと)します。\n'\
            '次のプレイヤーは次のふたつのうち、「どちらか」の行動をとってください。\n'\
            '1: 数字を上げる → 前プレイヤーの宣言した数が実際にこの場にいるコヨーテの数**以下（オーバー）していない**と思う場合、**前プレイヤーより大きな数**を宣言します。\n'\
            '2: 「コヨーテ！」→ 前プレイヤーの宣言を疑います。つまり、前プレイヤーの宣言した数が実際にこの場にいるコヨーテの数よりも**大きい（オーバーした）**と思う場合、**「コヨーテ！」**と宣言します\n'\
            '2の場合、例：`coyote-game-coyote @you 99`のように(`@you`はidでもOK)**Discordに書き込んで**ください！（Botが結果を判定します！）\n'\
            '**誰かが「コヨーテ！」と宣言するまで**、時計回りで順々に交代しながら宣言する数字を上げていきます\n'
        await interaction.followup.send(msg2)

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
        await interaction.followup.send(msg3)

        msg4 = self.coyoteGames[interaction.guild_id].create_description(True)
        await interaction.followup.send(msg4)
        card_msg = self.coyoteGames[interaction.guild_id].create_description_card()
        await interaction.followup.send(card_msg)

    async def coyoteLittleMessage(self, interaction: discord.Interaction):
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
        await interaction.response.send_message(msg)
        msg2 = self.coyoteGames[interaction.guild_id].create_description(True)
        await interaction.followup.send(msg2)
        card_msg = self.coyoteGames[interaction.guild_id].create_description_card()
        await interaction.followup.send(card_msg)

class CoyoteModal(discord.ui.Modal):
    def __init__(
        self,
        title: str = "コヨーテ！",
        *,
        timeout: int = 300,
        input_label: str = "コヨーテするID",
        input_style: discord.TextStyle = discord.TextStyle.short,
        input_placeholder: Optional[str] = 'コヨーテ対象のIDを入力(Aなど)',
        coyote,
        msg: str
    ):
        super().__init__(title=title, timeout=timeout, custom_id='wait_for_modal')
        self.value: Optional[str] = None
        self.interaction: Optional[discord.Interaction] = None
        self.coyote = coyote
        self.msg = msg

        self.setsumei = discord.ui.TextInput(
            label = 'こちらは入力不要です(下記の説明) ',
            style = discord.TextStyle.long,
            default=self.msg,
            required=False,
            custom_id = self.custom_id + '_input_field_setsumei',
        )

        self.target_id = discord.ui.TextInput(
            label = input_label,
            style = input_style,
            placeholder = input_placeholder,
            max_length = 1,
            min_length = 1,
            required=True,
            custom_id = self.custom_id + '_input_field_target_id',
        )

        self.number = discord.ui.TextInput(
            label = 'コヨーテ相手の数字を入力してください',
            placeholder = '10などの数字',
            max_length = 3,
            min_length = 1,
            style = input_style,
            required=True,
            custom_id = self.custom_id + '_input_field_number',
        )
        self.add_item(self.setsumei)
        self.add_item(self.target_id)
        self.add_item(self.number)

    async def on_submit(self, interaction: discord.Interaction):
        """
            コヨーテ中に実行できる行動。「コヨーテ！」を行う
            - 「コヨーテ！」は前プレイヤーの宣言を疑う行動
            - 「前プレイヤーの宣言した数」が「実際にこの場にいるコヨーテの数よりも**大きい（オーバーした）**」と思う場合に実行してください
            引数は2つあり、どちらも必須です
            - 1.プレイヤーのID
            - 2.前プレイヤーの宣言した数
        """
        number = self.number.value
        target_id = self.target_id.value

        if number.isdecimal():
            number = int(number)
        else:
            number = 0

        if target_id is None:
            msg = '「コヨーテする相手」(IDで指定(aなど))と「コヨーテを言われた人の数字」を指定してください'
            await interaction.response.send_message(msg, ephemeral=True)
            return
        if number <= 0:
            msg = '「コヨーテを言われた人の数字」は「1以上の整数」(0もダメです)を指定してください'
            await interaction.response.send_message(msg, ephemeral=True)
            return
        if self.coyote.coyoteStartCheckNG():
            msg = 'コヨーテを始めてから実行できます。コヨーテを始めたい場合は、`/start-coyote-game`を入力してください。'
            await interaction.response.send_message(msg, ephemeral=True)
            return
        # コヨーテ！した相手のメンバー情報を取得。取得できない場合はエラーを返す
        # IDから取得を試みる
        keys = [k for k, v in self.coyote.members.items() if v.id == str(target_id).upper()]
        if len(keys) == 0:
            msg = '「コヨーテする相手」(IDで指定(aなど))と「コヨーテを言われた人の数字」を指定してください'
            await interaction.response.send_message(msg, ephemeral=True)
            return
        else:
            you = keys.pop()
        if you not in self.coyote.members:
            msg = 'ゲームに存在する相手を選び、「コヨーテ！」してください(ゲームしている相手にはいません)。'
            await interaction.response.send_message(msg, ephemeral=True)
            return

        # コヨーテ！した結果を表示しつつ、次のターンを始めるボタンを用意
        self.coyote.coyote(interaction.user, you, number)
        # ボタン(ディールする(次のターン)、ネタバレ説明)を作成
        view = CoyoteDeal(self.coyote)
        await interaction.response.send_message(self.coyote.description, view=view)

class CoyoteAnswer(discord.ui.View):
    def __init__(self, coyote):
        super().__init__(timeout=300)
        self.coyote = coyote

    @discord.ui.button(label='相手のカードを表示する', style=discord.ButtonStyle.green)
    async def display(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg = self.coyote.display_other(interaction.user)
        await interaction.response.send_message(f'他の人のコヨーテカードはこちらです！\n{msg}', ephemeral=True)
        # self.coyote.description = ''

    @discord.ui.button(label='コヨーテ！', style=discord.ButtonStyle.blurple)
    async def answer(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg = self.coyote.show_members(interaction.user)
        msg += '確認できるカードは以下。'
        msg += self.coyote.display_other(interaction.user)
        await interaction.response.send_modal(CoyoteModal(msg=msg, coyote=self.coyote))

    @discord.ui.button(label='カード能力説明', style=discord.ButtonStyle.gray)
    async def description_card(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        カードの能力を説明します。
        """
        if self.coyote.coyoteStartCheckNG(True):
            msg = 'コヨーテを始めてから実行できます。コヨーテを始めたい場合は、`/start-coyote-game`を入力してください。'
            await interaction.response.send_message(msg, ephemeral=True)
            return
        msg = self.coyote.create_description_card()
        await interaction.response.send_message(msg, ephemeral=True)

    @discord.ui.button(label='状況説明', style=discord.ButtonStyle.gray)
    async def description_normal(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        状況を説明します。
        - ターン数、生き残っている人の数、それぞれのHP
        - 山札の数、捨て札の数、捨て札の中身
        """
        if self.coyote.coyoteStartCheckNG(True):
            msg = 'コヨーテを始めてから実行できます。コヨーテを始めたい場合は、`/start-coyote-game`を入力してください。'
            await interaction.response.send_message(msg, ephemeral=True)
            return
        msg = self.coyote.create_description()
        await interaction.response.send_message(msg, ephemeral=True)

    @discord.ui.button(label='状況確認', style=discord.ButtonStyle.gray)
    async def description(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        状況を全て説明します（場のカードもわかります）。
        - ターン数、生き残っている人の数、それぞれのHP
        - 山札の数、山札の中身、捨て札の数、捨て札の中身、場のカード
        """
        if self.coyote.coyoteStartCheckNG(True):
            msg = 'コヨーテを始めてから実行できます。コヨーテを始めたい場合は、`/start-coyote-game`を入力してください。'
            await interaction.response.send_message(msg, ephemeral=True)
            return
        msg = self.coyote.create_description(True)
        await interaction.response.send_message(msg, ephemeral=True)

    @discord.ui.button(label='状況説明(全て)', style=discord.ButtonStyle.gray)
    async def description(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        状況を全て説明します（場のカードもわかります）。
        - ターン数、生き残っている人の数、それぞれのHP
        - 山札の数、山札の中身、捨て札の数、捨て札の中身、場のカード
        """
        if self.coyote.coyoteStartCheckNG(True):
            msg = 'コヨーテを始めてから実行できます。コヨーテを始めたい場合は、`/start-coyote-game`を入力してください。'
            await interaction.response.send_message(msg, ephemeral=True)
            return
        msg = self.coyote.create_description(True)
        await interaction.response.send_message(msg, ephemeral=True)

class CoyoteDeal(discord.ui.View):
    def __init__(self, coyote):
        super().__init__(timeout=300)
        self.coyote = coyote

    @discord.ui.button(label='ディール(次のターンを始める)', style=discord.ButtonStyle.blurple)
    async def deal(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        コヨーテ中に実行できる行動。カードを引いて、プレイヤーに配ります
        """
        if self.coyote.coyoteStartCheckNG():
            msg = 'コヨーテを始めてから実行できます。コヨーテを始めたい場合は、`/start-coyote-game`を入力してください。'
            await interaction.response.send_message(msg, ephemeral=True)
            return

        self.coyote.deal()
        # ボタン(相手のカードを表示する、コヨーテ！、カード能力説明、状況説明、ネタバレ説明)を作成
        view = CoyoteAnswer(self.coyote)
        try:
            await interaction.response.send_message(f'カードを配りました。「相手のカードを表示する」ボタンを押してご確認ください。{self.coyote.description}', view=view)
        except discord.errors.InteractionResponded as e:
            await interaction.followup.send(f'カードを配りました。「相手のカードを表示する」ボタンを押してご確認ください。{self.coyote.description}', view=view)
        return

    @discord.ui.button(label='状況説明(全て)', style=discord.ButtonStyle.gray)
    async def description(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        状況を全て説明します（場のカードもわかります）。
        - ターン数、生き残っている人の数、それぞれのHP
        - 山札の数、山札の中身、捨て札の数、捨て札の中身、場のカード
        """
        if self.coyote.coyoteStartCheckNG(True):
            msg = 'コヨーテを始めてから実行できます。コヨーテを始めたい場合は、`/start-coyote-game`を入力してください。'
            await interaction.response.send_message(msg, ephemeral=True)
            self.stop()
            return
        msg = self.coyote.create_description(True)
        await interaction.response.send_message(msg, ephemeral=True)

class CoyoteDeckModal(discord.ui.Modal):
    def __init__(self, coyoteStart):
        super().__init__(title='デッキを構築', timeout=500, custom_id='coyote_deck_modal')
        self.coyoteStart = coyoteStart

    deck = discord.ui.TextInput(
        label='デッキを「,」(コンマ)で区切って指定します。二重引用符は不要',
        style=discord.TextStyle.long,
        placeholder='20, 11, 0, 0, 0(Night), -5, *2(Chief), Max->0(Fox), ?(Cave), ?(Cave)',
        required=True,
        default='20, 15, 15, 10, 10, 10, 5, 5, 5, 5, 4, 4, 4, 4, 3, 3, 3, 3, 2, 2, 2, 2, 1, 1, 1, 1, 0, 0, 0, 0(Night), -5, -5, -10, *2(Chief), Max->0(Fox), ?(Cave)',
        max_length=400,
        custom_id='coyote_deck_modal_input_field_deck'
    )

    async def on_submit(self, interaction: discord.Interaction):
        self.coyoteStart.coyoteGames[interaction.guild_id].setInit(self.coyoteStart.cy_members[interaction.guild_id].get_members())
        self.coyoteStart.coyoteGames[interaction.guild_id].setDeck(self.deck.value)
        self.coyoteStart.coyoteGames[interaction.guild_id].shuffle()
        msg = self.coyoteStart.coyoteGames[interaction.guild_id].create_description(True)
        await interaction.response.send_message(msg)
        await self.coyoteStart.dealAndMessage(interaction)

class CoyoteMember:
    DEFAULT_HP = 3
    def __init__(self):
        self.HP = self.DEFAULT_HP
        self.card = ''
        self.isDead = False
        self.id = ''

    def setCard(self, card: str):
        self.card = card

    def damage(self, number: int):
        self.HP = self.HP - number
        if self.HP == 0:
            self.isDead = True

    def setId(self, id: str):
        self.id = id

class Coyote:
    DEFAULT_DECK = [20, 15, 15, 10, 10, 10, 5, 5, 5, 5, 4, 4, 4, 4, 3, 3, 3, 3, 2, 2, 2, 2, 1, 1, 1, 1, 0, 0, 0, '0(Night)', -5, -5, -10, '*2(Chief)', 'Max->0(Fox)', '?(Cave)']
    ID_LIST = list(string.ascii_uppercase)
    DESCRPTION_NORMAL = 'Normal'
    DESCRPTION_ALL = 'All'
    DESCRPTION_NOTHING = 'Nothing'

    def __init__(self):
        self.members = {}
        self.body = []
        self.deck = self.DEFAULT_DECK.copy()
        self.hands = []
        self.discards = []
        self.turn = 0
        self.description = ''
        self.start_description = ''
        self.set_deck_flg = False
        self.before_deck = []

    def setInit(self, members):
        self.__init__()
        self.before_deck = self.DEFAULT_DECK.copy()
        self.set_deck_flg = False
        for id, member in zip(self.ID_LIST ,members):
            coyoteMember = CoyoteMember()
            coyoteMember.setId(id)
            self.members[member] = coyoteMember

    def set(self, members):
        self.members = {}
        self.body = []
        self.deck = self.before_deck.copy()
        self.hands = []
        self.discards = []
        self.turn = 0
        self.description = ''
        for id, member in zip(self.ID_LIST ,members):
            coyoteMember = CoyoteMember()
            coyoteMember.setId(id)
            self.members[member] = coyoteMember

    def setDeck(self, deck:str):
        self.set_deck_flg = True
        self.deck = []
        deck = deck.replace('"','').replace("'","").replace(' ','').replace('　','')
        card_list = deck.split(',')

        for card in card_list:
            if self.is_num(card):
                self.deck.append(int(card))
            elif card == '':
                continue
            else:
                self.deck.append(str(card))
        self.before_deck = self.deck.copy()

    def shuffle(self):
        self.deck.extend(self.discards)
        self.discards = []
        random.shuffle(self.deck)
        message = 'シャッフルしました。\n'
        self.description += message
        LOG.info(message)

    def deal(self):
        self.turn = self.turn + 1
        self.description = ''
        self.hands = []

        for member in self.members:
            card = self.deck.pop()
            self.members[member].setCard(card)
            self.hands.append(card)
            if len(self.deck) == 0:
                message = 'カードがなくなったので、'
                self.description += message
                LOG.info(message)
                self.shuffle()

    def coyote(self, me: discord.Member, you: discord.Member, number):
        # 計算
        coyotes = self.calc()

        # コヨーテの結果の判定
        if number > coyotes:
            self.members[you].damage(1)
            message = f'**入力値({number})** > {coyotes} → 「コヨーテ！」の勝ち(**{me.display_name}が正しい！**)\n'\
                    f'{you.display_name}に1点ダメージ。次の手番は{you.display_name}(敗者)からです。\n'
            self.description += message
            LOG.info(message)
            if self.members[you].isDead:
                self.body.append(self.members.pop(you))
                message = f'{you.display_name}は死にました。\n'
                if len(self.members) > 1:
                    message += f'**次は{me.display_name}(勝者)から手番を開始**してください。\n'
                self.description += message
                LOG.info(message)
        else:
            self.members[me].damage(1)
            message = f'**入力値({number})** <= {coyotes} → 「コヨーテ！」の負け({you.display_name}が正しい！)\n'\
                    f'{me.display_name}に1点ダメージ。**次の手番は{me.display_name}(敗者)から**です。\n'
            self.description += message
            LOG.info(message)
            if self.members[me].isDead:
                self.body.append(self.members.pop(me))
                message = f'**{me.display_name}は死にました。**\n'
                if len(self.members) > 1:
                    message += f'**次は{you.display_name}(勝者)から手番を開始**してください。\n'
                self.description += message
                LOG.info(message)

        # 一人になったら、勝利
        if len(self.members) == 1:
            for member in self.members:
                message = f'{member.display_name}の勝ちです！　おめでとうございます！！'
                self.description += message
                LOG.info(message)
        else:
            self.description += '現在の状況:'
            for member in self.members:
                self.description += f'{member.display_name}さん(ID:{self.members[member].id}, HP:{self.members[member].HP}) '
            self.description += '\nボタンを押すと、次のターンが始まります。'

    def calc(self):
        normal_hands = [i for i in self.hands if self.is_num(i)]
        special_hands = [i for i in self.hands if not self.is_num(i)]
        shuffle_flg = False

        # Caveカードの効果
        cave_hands = [i for i in special_hands if ('CAVE' in str(i).upper())]
        cave_count = 0
        for card in cave_hands:
            while(True):
                self.discards.append(card)
                try:
                    additional_card = self.deck.pop()
                    message = f'{card}の効果で、1枚山札から引いた(値は{additional_card})。\n'
                    self.description += message
                    LOG.info(message)
                except IndexError:
                    message = 'カードがなくなったので、'
                    self.description += message
                    LOG.info(message)
                    self.shuffle()
                    break
                deck_plus_discards_set = set(map(str, self.discards + self.deck))
                deck_plus_discards_set = {str.upper() for str in deck_plus_discards_set}

                if 'CAVE' in str(additional_card).upper():
                    cave_count = cave_count + 1
                    self.discards.append(additional_card)
                    message = f'Caveを引いたため、引き直し。\n'
                    self.description += message
                    LOG.info(message)
                    if len(self.deck) == 0:
                        message = 'カードがなくなったので、'
                        self.description += message
                        LOG.info(message)
                        self.shuffle()

                    if cave_count > 2:
                        # 3回以上繰り返した場合は無視する
                        message = f'★Caveを3回以上引き続けたため、無視します。\n'
                        self.description += message
                        LOG.info(message)
                        break
                    else:
                        if len(deck_plus_discards_set) == 1 and 'CAVE' in deck_plus_discards_set.pop():
                            message = f'山札/捨て札にCaveしかない不正な状況のため、処理を終了。\n'
                            self.description += message
                            LOG.info(message)
                            break
                        else:
                            continue
                else:
                    self.hands.append(additional_card)

                    # 引いたもので再計算
                    normal_hands = [i for i in self.hands if self.is_num(i)]
                    special_hands = [i for i in self.hands if (not self.is_num(i) and not ('CAVE' in str(i).upper()))]
                    if len(self.deck) == 0:
                        message = 'カードがなくなったので、'
                        self.description += message
                        LOG.info(message)
                        self.shuffle()
                    if not 'CAVE' in str(additional_card).upper():
                        break

        # Chiefカードを集計
        chief_hands = [i for i in special_hands if ('CHIEF' in str(i).upper())]
        special_hands = [i for i in special_hands if not 'CHIEF' in str(i).upper()]

        fox_hands = []
        for card in special_hands:
            card = str(card)

            # Nightカードの効果
            if 'NIGHT'in card.upper():
                self.discards.append(card)
                normal_hands.append(0)
                shuffle_flg = True
                message = f'{card}の効果で、計算終了後に山札/捨て札を混ぜてシャッフルする。\n'
                self.description += message
                LOG.info(message)

            # Foxカードの効果
            if 'FOX' in card.upper():
                self.discards.append(card)
                num_hands = [i for i in normal_hands if self.is_num(i) and i > 0]
                if len(num_hands) == 0:
                    max_num = 0
                else:
                    max_num = max(num_hands)
                fox_hands.append(-max_num)
                message = f'{card}の効果で、コヨーテカードの最大値である{max_num}を0にした。\n'
                self.description += message
                LOG.info(message)

        # 計算
        coyotes = 0
        self.description += '通常カードの計算：'
        for card in normal_hands:
            self.discards.append(card)
            coyotes += card
            if card >= 0:
                self.description += f'+ {str(card)}'
            else:
                self.description += f'{str(card)}'
        for fcard in fox_hands:
            coyotes += fcard
            if fcard >= 0:
                self.description += f'+ {str(fcard)}'
            else:
                self.description += f'{str(fcard)}'
        self.description += '\n'

        # Chiefカードの効果
        for card in chief_hands:
            self.discards.append(card)
            coyotes = coyotes * 2
            message = f'{card}の効果で、2倍にした。\n'
            self.description += message
            LOG.info(message)

        if shuffle_flg:
            self.shuffle()

        return coyotes

    def is_num(self, num):
        num_check = re.compile(r'-?\d+')
        m = re.fullmatch(num_check, str(num))
        if m is None:
            return False
        else:
            return True

    def create_description(self, all_flg=False):
        msg = f'ターン数：{self.turn}\n'
        msg += f'生き残っている人の数：{len(self.members)}\n'
        for member in self.members:
            msg += f'`{member.display_name}さん(id:{self.members[member].id}) → HP:{self.members[member].HP}`\n'
        if all_flg:
            msg += f'山札の数：{len(self.deck)}枚 → `'
            deck_list = sorted(map(str, self.deck))
            deck = ','.join(deck_list)
            msg += deck + '`\n'
        else:
            msg += f'山札の数：{len(self.deck)}枚, '
        msg += f'捨て札：{len(self.discards)}枚'
        if len(self.discards) > 0:
            msg += ' → `'
            discards_list = map(str, self.discards)
            discards = ','.join(discards_list)
            msg += discards + '\n`'
        else:
            msg += '\n'

        if all_flg:
            msg += f'場のカード：{len(self.hands)}枚'
            if len(self.hands) > 0:
                msg += ' → '
                hands_list = map(str, self.hands)
                hands = ','.join(hands_list)
                msg += f'||{hands}||'

        return msg

    def create_description_card(self):
        msg = 'ナンバーカードには、「基本カード」と「特殊カード」の2種類が存在します。\n'
        msg += '■基本カード\n'
        msg += 'コヨーテカード: 1以上の数値を持ったカード, 兵隊カード: −1以下の数値を持ったカード(兵隊に退治されコヨーテが減ります), おばけカード: 0のカード（数に加えません）\n'
        msg += '■特殊カード\n'       
        msg += '\*2(Chief): 酋長カード...すべての基本カードの数値を2倍にします。\n'
        msg += '0(Night): 夜カード...0です。計算終了後、山札・捨て札を混ぜてシャッフルします（山札がリセットされる）。\n'
        msg += '?(Cave): ほらあなカード...計算時に山札からナンバーカードを1枚引き、その数を加えます。\n'
        msg += 'Max->0(Fox): キツネカード...この回で出た最大のコヨーテカードの数値を「0」にします。\n'
        return msg

    def display_other(self, me):
        msg_all = ''
        # 全員分のメッセージを作成
        for player in self.members:
            msg_all += f'{player.display_name}さん: {self.members[player].card}\n'
        # 送付する相手の名前が記載された行を削除
        rpl_msg_del = f'{me.display_name}さん:.+\n'
        return re.sub(rpl_msg_del, '', msg_all)

    def show_members(self, me):
        # 自分以外のメンバーとそのIDを表示
        msg = ''
        for member in self.members:
            if me != member:
                msg += f'{member.display_name}さん(id:{self.members[member].id}) → HP:{self.members[member].HP}\n'
        return msg

    def coyoteStartCheckNG(self, desc=False):
        if len(self.members) >= 2:
            return False
        # 終わった後に説明が見たい場合は許す
        elif len(self.members) == 1 and desc:
            return False
        else:
            return True
