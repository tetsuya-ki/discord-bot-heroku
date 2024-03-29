import aiohttp
import datetime, random, hashlib
import discord
import re
import mojimoji
from logging import getLogger
from enum import Enum

LOG = getLogger('assistantbot')

class Pref(Enum):
    """
    discordの制限で25までしか選べず...
    """
    北海道 = 'JP01'
    青森県 = 'JP02'
    秋田県 = 'JP05'
    福島県 = 'JP07'
    群馬県 = 'JP10'
    埼玉県 = 'JP11'
    東京都 = 'JP13'
    神奈川県 = 'JP14'
    新潟県 = 'JP15'
    石川県 = 'JP17'
    山梨県 = 'JP19'
    静岡県 = 'JP22'
    愛知県 = 'JP23'
    三重県 = 'JP24'
    京都府 = 'JP26'
    大阪府 = 'JP27'
    兵庫県 = 'JP28'
    鳥取県 = 'JP31'
    岡山県 = 'JP33'
    広島県 = 'JP34'
    香川県 = 'JP37'
    福岡県 = 'JP40'
    熊本県 = 'JP43'
    鹿児島県 = '4JP6'
    沖縄県 = 'JP47'

class Radiko:
    PREF_NAMES = ['北海道','青森県','岩手県','宮城県','秋田県','山形県','福島県','茨城県','栃木県','群馬県','埼玉県','千葉県','東京都','神奈川県','新潟県','富山県','石川県','福井県','山梨県','長野県','岐阜県','静岡県','愛知県','三重県','滋賀県','京都府','大阪府','兵庫県','奈良県','和歌山県','鳥取県','島根県','岡山県','広島県','山口県','徳島県','香川県','愛媛県','高知県','福岡県','佐賀県','長崎県','熊本県','大分県','宮崎県','鹿児島県','沖縄県']
    PREF_CD = {'北海道':'01','青森県':'02','岩手県':'03','宮城県':'04','秋田県':'05','山形県':'06','福島県':'07','茨城県':'08','栃木県':'09','群馬県':'10','埼玉県':'11','千葉県':'12','東京都':'13','神奈川県':'14','新潟県':'15','富山県':'16','石川県':'17','福井県':'18','山梨県':'19','長野県':'20','岐阜県':'21','静岡県':'22','愛知県':'23','三重県':'24','滋賀県':'25','京都府':'26','大阪府':'27','兵庫県':'28','奈良県':'29','和歌山県':'30','鳥取県':'31','島根県':'32','岡山県':'33','広島県':'34','山口県':'35','徳島県':'36','香川県':'37','愛媛県':'38','高知県':'39','福岡県':'40','佐賀県':'41','長崎県':'42','熊本県':'43','大分県':'44','宮崎県':'45','鹿児島県':'46','沖縄県':'47'}
    RADIKO_URL = 'http://radiko.jp/v3/api/program/search'
    RADIKO_TS_URL = 'https://radiko.jp/#!/ts'
    LIMIT_NUM = 5
    DEFAULT_AREA = 'JP13'

    def __init__(self):
        self.content = ''
        self.r_err = ''

    async def radiko_search(self, keyword='', filter='', areaName='', startDay='', endDay=''):
        # どっちも空文字になるなら、入れ替えて検索する
        if self.convert_filter(filter) == self.convert_prefCd(areaName) == '':
            filter,areaName = areaName,filter
        msg = 'keyword: ' + keyword + \
                ', filter: ' + self.convert_filter(filter) + \
                ', area: ' + self.convert_prefCd(areaName)
        if self.convert_day(startDay) is not None:
            msg += ', startDay: ' + self.convert_day(startDay)
        if self.convert_day(endDay) is not None:
            msg += ', endDay: ' + self.convert_day(endDay)
        LOG.debug(msg)
        response = await self.search_radiko_result(keyword, self.convert_filter(filter), self.convert_prefCd(areaName), self.convert_day(startDay), self.convert_day(endDay))

        if response is None:
            return

        result_count = response['meta']['result_count']
        self.content = f"検索結果は、{result_count}件です"
        if result_count > self.LIMIT_NUM:
            self.content += f'(ただし、{self.LIMIT_NUM}件を超えた部分については表示されません)'
        elif result_count == 0:
            return

        embed_field = ''

        count = 1
        for key in response['data']:
            data = ''
            data += f"**title:{key['title']}**"
            if key['start_time'][:10] == key['end_time'][:10]:
                start2end = key['start_time'][:16] + '-' + key['end_time'][11:16]
            else:
                start2end = key['start_time'][:16] + '-' + key['end_time'][:16]
            data += '\ndatetime:' + start2end
            data += '\nstation_id:' + key['station_id']
            data += '\nperformer:' + key['performer'] if key['performer'] != '' else '\nperformer:(なし)'
            data += '\nurl:' + key['program_url'] + ' / RadikoURL: ' +\
                    '/'.join([self.RADIKO_TS_URL, key['station_id'],str(key['start_time']).replace('-','').replace(':','').replace(' ','')])

            # descripton側しか入っていないデータを発見したため、対処
            info_data = key['info']
            if len(key['description']) > len(info_data):
                info_data = key['description']

            info_data = re.sub(r'<br *?/>', '@@', info_data) # 改行変換
            info_data = re.sub(r'<[^>]*?>', '', info_data) # タグ削除
            info_data = re.sub(r'\t|\n|(&[lg]t; *)', '', info_data) # タグ削除
            info_data = re.sub(r'@+ +?@+', '', info_data) # 意味のないスペース削除
            info_data = re.sub(r'@{2,}', ' ', info_data) # 改行削除
            info_data = info_data.strip()
            info_data = mojimoji.zen_to_han(info_data, kana=False)

            # データが1件以上ならinfoは省略
            if len(response['data']) > 1:
                info_data_ex = info_data[:100] + '(省略)'
                LOG.debug('文字数超で省略されたinfo:' + info_data)
            else:
                info_data_ex = info_data

            if len(embed_field + data + '\ninfo:' + info_data_ex) > 1700:
                data += '\ninfo:(文字数超えのため削除)'
                LOG.debug('文字数超で削除されたinfo:' + info_data)
            else:
                data += f'\ninfo:{info_data_ex}'

            embed_field += f'{str(count)}件目: {data}\n'
            count = count + 1
            if count > self.LIMIT_NUM:
                break

        embed = discord.Embed(title = f'keyword:{keyword}, filter:{filter}, areaName:{areaName} の結果です', description=embed_field, type='rich')
        return embed

    def generate_uid(self):
        """
        rdk_uid生成関数
        """
        rnd = random.random() * 1000000000
        ms = datetime.timedelta.total_seconds(datetime.datetime.now() - datetime.datetime(1970, 1, 1)) * 1000
        return hashlib.md5(str(rnd + ms).encode('utf-8')).hexdigest()

    def convert_prefCd(self, prefName):
        if ('都' in prefName or '道' in prefName or '府' in prefName or '県' in prefName):
            try:
                if self.PREF_CD[prefName].isdecimal():
                    return 'JP' + self.PREF_CD[prefName]
            except KeyError:
                return ''
        elif 'JP' in prefName:
            return prefName
        else:
            return ''

    def convert_filter(self, filter):
        if '未来' in filter or 'future' in filter:
            return 'future'
        elif '過去' in filter or 'past' in filter:
            return 'past'
        else:
            return ''

    def convert_day(self, day):
        now = datetime.datetime.now()
        now_yyyymmdd_string = now.strftime('%Y-%m-%d')
        now_yyyymm_string = now.strftime('%Y-%m-')
        now_yyyy_string = now.strftime('%Y-')

        if day is None:
            return ''
        if day <= 9: # 数日後として解釈
            conv_day = now + datetime.timedelta(days=day)
            return conv_day.strftime('%Y-%m-%d')
        if day <= 100: # 今月の日付部として解釈
            return now_yyyymm_string + str(day)
        elif len(str(day)) == 4: # 今年の月日として解釈
            return now_yyyy_string + str(day)[0:2] + '-' + str(day)[2:]
        else:
            return now_yyyymmdd_string

    async def search_radiko_result(self, keyword='', filter='', area_id=DEFAULT_AREA, startDay='', endDay=''):
        # ref. https://turtlechan.hatenablog.com/entry/2019/06/25/195451
        area_id_with_defalut_area = self.DEFAULT_AREA if area_id == '' else area_id
        params = {
            'key': keyword,
            'filter': filter,
            'start_day': startDay,
            'end_day': endDay,
            'area_id': area_id_with_defalut_area,
            'region_id': '',
            'cul_area_id': area_id_with_defalut_area,
            'page_idx': '0',
            'uid': self.generate_uid(),
            'row_limit': '10',
            'app_id': 'pc',
            'action_id': '0',
            }
        response = None

        async with aiohttp.ClientSession() as session:
            async with session.get(self.RADIKO_URL, params=params) as r:
                if r.status == 200:
                    response = await r.json()
                    return response
                else:
                    self.r_err = 'Radikoの番組表検索に失敗しました。'
                    LOG.warn(self.r_err)
                    LOG.warn(r)
                    return