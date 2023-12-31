# ベースイメージの指定
FROM python:3.8.6-slim

# ソースを置くディレクトリを変数として格納
ARG dir=/opt/app \
    home=/home
ENV POETRY_HOME=/opt/poetry \
    # POETRY_VIRTUALENVS_CREATE=false \
    # POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=1.1.14
ENV PATH=$PATH:$POETRY_HOME/bin
# poetry導入
RUN pip install poetry


WORKDIR $dir
RUN groupadd -r bot && useradd -r -g bot bot
ADD entrypoint.sh $dir

ADD . $dir
RUN chmod -R 755 $dir && chown -R bot:bot $dir
RUN chmod -R 755 $home && chown -R bot:bot $home
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
USE_IF_AVAILABLE_FILE=False\
USE_TWITTER_EXPANDED=True

WORKDIR $dir
RUN poetry update && poetry install

# dockerコンテナが起動する際に実行されるコードファイル (`entrypoint.sh`)
ENTRYPOINT ["./entrypoint.sh"]