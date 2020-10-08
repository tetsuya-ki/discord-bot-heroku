
# ローカルでの動かし方

1. install modules

    mac: `pip3 install -r requirements.txt`  
    windows: `py -3 pip install -r requirements.txt`

2. create .env  
`.env.sample`を参考に`.env`を作成する  
BOTは[こちら](https://discord.com/developers/applications)で作成し、トークンを取得する（トークンは厳重に管理すること！）

3. start bot

    mac: `python3 assitantbot.py`  
    windows: `py -3 assitantbot.py`

# dockerでの動かし方

0. botを作っておく  
BOTは[こちら](https://discord.com/developers/applications)で作成し、トークンを取得する（トークンは厳重に管理すること！）

1. make docker image  
    `docker build --pull --rm -f Dockerfile -t discordbotheroku:latest .`

2. make .env-docker  
`.env-docker.sample`を参考に`.env-docker`を作成する(=の両端はスペース無しが良さそう。以下のスタイルなら動いた)  

    ```sh
    DISCORD_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    ...
    ```

3. run docker container  
    このBOTの場合、環境変数はファイル指定がオススメだが、普通に指定しても動くはず。  
    `docker run --env-file ./cogs/modules/files/.env-docker discordbotheroku:latest`
