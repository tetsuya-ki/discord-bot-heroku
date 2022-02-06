import os
import aiohttp
from logging import getLogger

logger = getLogger(__name__)

class SaveFile:
    def __init__(self):
        pass

    async def download_file(self, url, dst_path):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                logger.debug(url)
                logger.debug(r.status)
                if r.status == 200:
                    with open(dst_path, 'wb') as local_file:
                        web_file = await r.read()
                        local_file.write(web_file)
                        return os.path.basename(dst_path)

    def download_file_to_dir(self, url, dst_dir):
        return self.download_file(
            url,
            os.path.join(
                dst_dir,
                self.add_suffix_gazou(os.path.basename(url.replace(':large', ''))),
            ),
        )

    def add_suffix_gazou(self, path: str):
        if not path.endswith('.jpg') and 'jpg' in path or 'jpeg' in path:
            return path + '.jpg'
        elif not path.endswith('.png') and 'png' in path:
            return path + '.png'
        elif not path.endswith('.gif') and 'gif' in path:
            return path + '.gif'
        else:
            return path