import os
import urllib.error
import urllib.request

class SaveFile:
    def __init__(self):
        print

    def download_file(self, url, dst_path):
        try:
            with urllib.request.urlopen(url) as web_file, open(dst_path, 'wb') as local_file:
                local_file.write(web_file.read())
                return dst_path
        except urllib.error.URLError as e:
            print(e)

    def download_file_to_dir(self, url, dst_dir):
        return self.download_file(url, os.path.join(dst_dir, os.path.basename(url)))