import random
import discord
import re
import string
from logging import getLogger

logger = getLogger(__name__)

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

    def __init__(self):
        self.members = {}
        self.body = []
        self.deck = self.DEFAULT_DECK.copy()
        self.hands = []
        self.discards = []
        self.turn = 0
        self.description = ''

    def set(self, members):
        self.members = {}
        self.body = []
        self.deck = self.DEFAULT_DECK.copy()
        self.hands = []
        self.discards = []
        self.turn = 0
        self.description = ''
        for id, member in zip(self.ID_LIST ,members):
            coyoteMember = CoyoteMember()
            coyoteMember.setId(id)
            self.members[member] = coyoteMember

    def setDeck(self, deck:str):
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

    def shuffle(self):
        self.deck.extend(self.discards)
        self.discards = []
        random.shuffle(self.deck)
        message = 'シャッフルしました。\n'
        self.description += message
        logger.info(message)

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
                logger.info(message)
                self.shuffle()

    def coyote(self, me: discord.Member, you: discord.Member, number):
        # 計算
        coyotes = self.calc()

        #　コヨーテの結果の判定
        if number > coyotes:
            self.members[you].damage(1)
            message = f'{number} > {coyotes} → 「コヨーテ！」の勝ち({me.display_name}が正しい！)\n'\
                    f'{you.display_name}に1点ダメージ。次の手番は{you.display_name}(敗者)からです。\n'
            self.description += message
            logger.info(message)
            if self.members[you].isDead:
                self.body.append(self.members.pop(you))
                message = f'{you.display_name}は死にました。\n'
                if len(self.members) > 1:
                    message += f'**次は{me.display_name}(勝者)から手番を開始**してください。\n'
                self.description += message
                logger.info(message)
        else:
            self.members[me].damage(1)
            message = f'{number} <= {coyotes} → 「コヨーテ！」の負け({you.display_name}が正しい！)\n'\
                    f'{me.display_name}に1点ダメージ。次の手番は{me.display_name}(敗者)からです。\n'
            self.description += message
            logger.info(message)
            if self.members[me].isDead:
                self.body.append(self.members.pop(me))
                message = f'{me.display_name}は死にました。\n'
                if len(self.members) > 1:
                    message += f'**次は{you.display_name}(勝者)から手番を開始**してください。\n'
                self.description += message
                logger.info(message)

        # 一人になったら、勝利
        if len(self.members) == 1:
            for member in self.members:
                message = f'{member.display_name}の勝ちです！　おめでとうございます！！'
                self.description += message
                logger.info(message)
        else:
            self.description += '現在の状況:'
            for member in self.members:
                self.description += f'{member.display_name}さん(ID:{self.members[member].id}, HP:{self.members[member].HP}) '
            self.description += '\n`/coyoteGame deal`で次のターンを開始します。'

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
                    logger.info(message)
                except IndexError:
                    message = 'カードがなくなったので、'
                    self.description += message
                    logger.info(message)
                    self.shuffle()
                    break
                deck_plus_discards_set = set(map(str, self.discards + self.deck))
                deck_plus_discards_set = {str.upper() for str in deck_plus_discards_set}

                if 'CAVE' in str(additional_card).upper():
                    cave_count = cave_count + 1
                    self.discards.append(additional_card)
                    message = f'Caveを引いたため、引き直し。\n'
                    self.description += message
                    logger.info(message)
                    if len(self.deck) == 0:
                        message = 'カードがなくなったので、'
                        self.description += message
                        logger.info(message)
                        self.shuffle()

                    if cave_count > 2:
                        # 3回以上繰り返した場合は無視する
                        message = f'★Caveを3回以上引き続けたため、無視します。\n'
                        self.description += message
                        logger.info(message)
                        break
                    else:
                        if len(deck_plus_discards_set) == 1 and 'CAVE' in deck_plus_discards_set.pop():
                            message = f'山札/捨て札にCaveしかない不正な状況のため、処理を終了。\n'
                            self.description += message
                            logger.info(message)
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
                        logger.info(message)
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
                logger.info(message)

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
                logger.info(message)

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
            logger.info(message)

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