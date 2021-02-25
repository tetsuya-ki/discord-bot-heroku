from logging import getLogger

import aiohttp
import datetime, random, hashlib
import discord
import re
import mojimoji

logger = getLogger(__name__)

class Radiko:
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
                logger.debug('文字数超で省略されたinfo:' + info_data)
            else:
                info_data_ex = info_data

            if len(embed_field + data + '\ninfo:' + info_data_ex) > 1700:
                data += '\ninfo:(文字数超えのため削除)'
                logger.debug('文字数超で削除されたinfo:' + info_data)
            else:
                data += f'\ninfo:{info_data_ex}'

            embed_field += f'{str(count)}件目: {data}\n'
            count = count + 1
            if count > self.LIMIT_NUM:
                break

        embed = discord.Embed(title = f'keyword:{keyword}, filter:{filter}, areaName:{areaName} の結果です', description=embed_field,type='rich', inline=False)
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

        # 文字列はtoday, tのみ許す
        if day == 'today' or day == 't':
            return now_yyyymmdd_string
        elif not day.isdecimal():
            return ''

        if len(day) == 1: # 数日後として解釈
            conv_day = now + datetime.timedelta(days=int(day))
            return conv_day.strftime('%Y-%m-%d')
        if len(day) == 2: # 今月の日付部として解釈
            return now_yyyymm_string + day
        elif len(day) == 4: # 今年の月日として解釈
            return now_yyyy_string + day[0:2] + '-' + day[2:]

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
                    logger.warn(self.r_err)
                    logger.warn(r)
                    return