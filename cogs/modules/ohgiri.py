import random
import discord
import re
import string
import json
import os
from os.path import join, dirname, exists
from logging import getLogger
from . import settings
from .savefile import SaveFile

logger = getLogger(__name__)

class OhgiriMember:
    """
    大喜利参加者クラス
    """
    def __init__(self):
        self.point = 0 
        self.cards = [] # カードのID

class Answer:
    def __init__(self, card_id, member):
        self.card_id = card_id # 回答カード配列の配列番号
        self.member = member # 回答者
        self.answer_index = None # 画面にある番号(画面に表示する前にまとめて採番して設定するのでinitではNone)

class Ohgiri:
    """
    大喜利ゲームのクラス
    """
    FILE = 'ohgiri.json'
    #{
    #"subject": ['今ちまたで人気のRPG、主人公が〇〇','いい年こいて親父が今ははまっているもの、〇〇','通っていた小学校の校訓、元気、本気、〇〇。今思うとおかしいよな']
    #"answer": ["入学式","修学旅行","卒業式","学校祭","体育祭","マラソン大会"],
    #}

    def __init__(self):
        self.members = {} # ゲームの参加者
        self.house = None # 今の親
        self.deck_odai = [] # 
        self.deck_ans = []
        self.odai = None # 場におかれているお題
        self.field = [] # 場におかれている回答
        self.discards_odai = [] # 捨て札(お題)
        self.discards_ans = [] # 捨て札(回答)
        self.winCardsList = []
        self.turn = 0
        self.description = ''
        self.max_hands = None
        self.ans_dict = {}
        self.savefile = SaveFile()

    async def init_card(self):
        json_data = {}

        json_path = join(dirname(__file__), 'files' + os.sep + 'temp' + os.sep + self.FILE)
        # 環境変数に大喜利用JSONのURLが登録されている場合はそちらを使用
        if settings.OHGIRI_JSON_URL:
            if not exists(json_path):
                file_path = await self.savefile.download_file(settings.OHGIRI_JSON_URL,  json_path)
            else:
                file_path = json_path
        else:
            file_path = join(dirname(__file__), 'files' + os.sep + self.FILE)

        try:
            with open(file_path, mode='r') as f:
                json_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, EOFError) as e:
            # JSON変換失敗、読み込みに失敗したらなにもしない
            logger.error(e)

        # お題配列を取り出してお題カード辞書を作る
        subject_index = 0
        self.deck_odai = json_data['subject']

        # 回答配列を取り出して回答カード辞書を作る
        answer_index = 0
        for answer in json_data['answer']:
            self.ans_dict[str(answer_index)] = answer
            self.deck_ans.append(str(answer_index))
            answer_index += 1

    async def setting(self, members, max_hands):
        """
        メンバーに大喜利メンバーをセットし、ゲームできるようにセッティングする
        """
        self.__init__()
        await self.init_card()
        self.max_hands = max_hands

        for member in members:
            ohgiriMember = OhgiriMember()
            self.members[member] = ohgiriMember
        self.house = random.choice(members)

    def shuffle(self):
        """
        デッキをシャッフルする（お題、回答両方）
        """
        random.shuffle(self.deck_odai)
        random.shuffle(self.deck_ans)
        message = 'シャッフルしました。\n'
        self.description += message
        logger.info(message)

    def deal(self):
        self.turn = self.turn + 1
        self.description = ''
        self.hands = []

        # 場に置かれるお題をひく
        self.odai =  self.deck_odai.pop()

        # お題の山札がなくなった場合の処理
        if len(self.deck_odai) == 0:
            self.retern_discards_to_deck(self.deck_odai, self.discards_odai)

        for member in self.members:
            # 手札が「手札の最大数 - メンバーのpoint」になるまでカードを配る
            while len(self.members[member].cards) < (self.max_hands - self.members[member].point):
                self.members[member].cards.append(self.deck_ans.pop())
                # カードが無くなった時の処理
                if len(self.deck_ans) == 0:
                    self.retern_discards_to_deck(self.discards_odai, self.deck_odai)

            self.members[member].cards = sorted(self.members[member].cards, key=int)

    def retern_discards_to_deck(self, target_discards, target_deck):
        message = 'お題カードがなくなったので山札と捨て札を混ぜて、'
        self.description += message
        logger.info(message)
        target_deck.extend(target_discards)
        target_discards = []
        self.shuffle()

    def receive_card(self, card_id, member):
        """
        メンバーからカードを受信したときの処理
        受信したカードを場に出す
        メンバーの手持ちから受信したカードを除去
        cardNum {Int}
        member self.membersから取り出すキー
        """

        self.field.append(Answer(card_id, member))

        # 受信したカード以外のカードをユーザに返す
        self.members[member].cards = [users_card_id for users_card_id in self.members[member].cards if users_card_id != card_id]

    def show_answer(self):
        # 山札からカードを引いてダミーの回答を作る
        self.field.append(Answer(self.deck_ans.pop(), 'dummy'))

        # 場に出た回答に画面表示用のランダムな番号を設定する。
        random_field = random.sample(self.field, len(self.field))
        for i in range(len(random_field)):
            random_field[i].answer_index = str(i)
        
        self.description = ''

        for sorted_answer in sorted(random_field, key=lambda answer: answer.answer_index):
            self.description += f'{str(sorted_answer.answer_index)}: {str(self.odai).replace("〇〇", "||" + self.ans_dict[sorted_answer.card_id] + "||")}\n'

    def choose_answer(self, answer_index):
        self.description = ''
        choosen_answer = [answer for answer in self.field if answer.answer_index == answer_index][0]

        if choosen_answer.member == 'dummy':
            # ダミーを選択したら親が減点
            self.description += 'ダミーを選択しました'
            house_member_obj = self.members[self.house]
            if house_member_obj.point > 0:
                house_member_obj.point += -1
                self.description += f'{self.house.display_name}のポイントが1点減りました。'

        else :
            # 選ばれた人が得点を得て、親になる
            self.members[choosen_answer.member].point += 1
            self.description += f'親から選ばれた、{choosen_answer.member.display_name}のポイントが1点増えました。'
            self.house = choosen_answer.member

        # 置換済みで回答と回答者を入れる
        win_word = f'{str(choosen_answer.answer_index)}: {str(self.odai).replace("〇〇", "**" + self.ans_dict[choosen_answer.card_id] + "**")} ({choosen_answer.member}さん)'
        self.winCardsList.append(win_word)
        self.description += win_word

    def show_info(self):        
        # 今の親
        self.description = f'現在の親: {self.house.display_name}さん'
        # 今のお題
        self.description += f'現在のお題: {self.house}'

        # 参加者の点数と回答済みかどうかを表示する
        for member in self.members:
            self.description += f'{member.display_name}さん：'
            self.description += f'{self.members[member].point}点：'

            if (len([answer for answer in self.field if answer.member == member]) == 0):
                self.description += "未回答"
            else:
                self.description += "回答済み"