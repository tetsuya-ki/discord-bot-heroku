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
IS_HEROKU=False \
OHGIRI_JSON_URL=\
WORDWOLF_JSON_URL=\
NGWORD_GAME_JSON_URL=\
ENABLE_SLASH_COMMAND_GUILD_ID=\
APPLICATION_ID=\
USE_IF_AVAILABLE_FILE=True

WORKDIR $dir
RUN poetry update && poetry install

# dockerコンテナが起動する際に実行されるコードファイル (`entrypoint.sh`)
ENTRYPOINT ["./entrypoint.sh"]