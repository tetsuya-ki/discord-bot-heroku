# ベースイメージの指定
FROM python:3.8.6-slim

# ソースを置くディレクトリを変数として格納
ARG dir=/opt/app
ARG POETRY_VERSION=1.1.13
ARG POETRY_HOME=/opt/poetry
# poetry導入
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=${POETRY_HOME} python3 - --version=${POETRY_VERSION}
ENV PATH ${PATH}:${POETRY_HOME}/bin


WORKDIR $dir
RUN groupadd -r bot && useradd -r -g bot bot
ADD entrypoint.sh $dir
ADD requirements.txt $dir

# requirements.txtに記載されたパッケージをインストール
RUN pip install -r requirements.txt

ADD . $dir
RUN chmod -R 755 $dir && chown -R bot:bot $dir
RUN rm -f $dir/cogs/modules/first_time

# user botで実行
USER bot

# 環境変数の定義
ENV LANG=ja_JP.UTF-8 \
LANGUAGE=ja_JP:ja_JP \
DISCORD_TOKEN=XXXXXXXXXX \
LOG_LEVEL=INFO \
AUDIT_LOG_SEND_CHANNEL=99999999.99999999 \
IS_HEROKU=False \
SAVE_FILE_MESSAGE=Twitter \
FIRST_REACTION_CHECK=True \
SCRAPBOX_SID_AND_PROJECTNAME1=xxx:sid@pjname \
PURGE_TARGET_IS_ME_AND_BOT=False \
OHGIRI_JSON_URL=\
REACTION_CHANNELER_PERMIT_WEBHOOK_ID=99999999\
WORDWOLF_JSON_URL=\
NGWORD_GAME_JSON_URL=\
ENABLE_SLASH_COMMAND_GUILD_ID=\
APPLICATION_ID=\
USE_IF_AVAILABLE_FILE=True

WORKDIR $dir

# dockerコンテナが起動する際に実行されるコードファイル (`entrypoint.sh`)
ENTRYPOINT ["./entrypoint.sh"]