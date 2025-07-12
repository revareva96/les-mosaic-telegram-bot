from time import time

from infrastructure.integations.file_storage.abstractions import IStorage
from telegram import File


class FSStorage(IStorage):

    def __init__(self, path: str, ext: str):
        self._path = path
        self._base_ext = ext

    async def save_photo(self, username: str, file: File) -> str:
        ext = self._base_ext
        file_ext = file.file_path.split('.')
        if file_ext:
            ext = file_ext[-1]
        photo_id = f'{username}_{int(time())}.{ext}'
        await file.download_to_drive(custom_path=f'{self._path}/{photo_id}')
        return photo_id
