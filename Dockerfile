# ベースイメージの指定
FROM python:3.8.6-slim

# ソースを置くディレクトリを変数として格納
ARG dir=/opt/app

WORKDIR $dir
RUN groupadd -r bot && useradd -r -g bot bot
ADD entrypoint.sh $dir
ADD requirements.txt $dir

# requirements.txtに記載されたパッケージをインストール
RUN pip install -r requirements.txt

ADD cogs $dir/cogs/
ADD assitantbot.py $dir
RUN chmod -R 755 $dir && chown -R bot:bot $dir
RUN rm -f /opt/app/cogs/modules/first_time

# user botで実行
USER bot

# 環境変数の定義
ENV LANG=ja_JP.UTF-8 \
LANGUAGE=ja_JP:ja_JP \
DISCORD_TOKEN=XXXXXXXXXX \ 
IS_DEBUG=True \ 
AUDIT_LOG_SEND_CHANNEL=99999999.99999999 \ 
IS_HEROKU=True 

WORKDIR $dir

# dockerコンテナが起動する際に実行されるコードファイル (`entrypoint.sh`)
ENTRYPOINT ["./entrypoint.sh"]