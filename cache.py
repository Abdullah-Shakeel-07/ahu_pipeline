import os

class CacheManager:
    ROOT_PATH = './cache'

    def __init__(self, base_path=''):
        self.base_folder_name = base_path
        self.base_path = os.path.join(self.ROOT_PATH, base_path)
        self.counter = 0
        if not os.path.exists(self.ROOT_PATH):
            print(f"[INFO] Creating root cache directory at {self.ROOT_PATH}")
            os.mkdir(self.ROOT_PATH)
        if not os.path.exists(self.base_path):
            os.mkdir(self.base_path)

    @staticmethod
    def normalize_key(key):
        if not key:
            return key
        return str(key).replace('/', '')

    def save(self, key, data):
        try:
            if not key:
                return
            key = self.normalize_key(key)
            file_path = os.path.join(self.base_path, f"{key}.html")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(data)
        except Exception as exc:
            print(f'Exception in saving cache for key {key}')
            return None

    def get(self, key):
        try:
            if not key:
                return None
            key = self.normalize_key(key)
            file_path = os.path.join(self.base_path, f"{key}.html")
            if not os.path.exists(file_path):
                return None
            return True
        except:
            return None

    def get_data(self, key):
        try:
            if not key:
                return None
            key = self.normalize_key(key)
            file_path = os.path.join(self.base_path, f"{key}.html")
            if not os.path.exists(file_path):
                return None
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return None