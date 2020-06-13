import pickle
import logging

from os import getcwd
from os.path import join
from pathlib import Path
from typing import Any

from storage.storage import StorageManager


log = logging.getLogger(__name__)


class LocalStorageManager(StorageManager):

    def __init__(self, path=None, hide_files=True):
        self._hide_files = hide_files
        self._path = path if path else join(getcwd())
        self._files = None
        self._data = None

        self._scan_path()

    def _scan_path(self):
        files = dict()

        for file in Path(self._path).glob('*.data'):

            # Why not?
            if file.is_dir():
                continue

            # Check if file can be opened
            try:
                with open(str(file), 'rb') as f:
                    pickle.load(f)

                # This blocks continues if everything is fine
                username = file.with_suffix('').name
                if username.startswith('.'):
                    # Then it was hidden
                    username = username[1:]

                files[username] = str(file)  # save for later

            except IOError:
                log.warning(f"Corrupted user checkpoint found: {file}")

        self._files = files

    def _save_data(self, username: str, value: Any):
        base_path = Path(self._path)
        save_path = base_path / f"{username}.data"

        if not base_path.exists():
            base_path.mkdir(parents=True)

        if self._hide_files:
            save_path = save_path.with_name('.' + save_path.name)

        try:
            with open(str(save_path), 'wb') as file:
                pickle.dump(value, file)
                return True

        except Exception as e:
            log.error(f"Can't save data. Operation discarded: {e}")
            return False

    def _load_data(self, username: str):
        """
        Finds `yaml` user config and loads it into memory for quick access.
        :return: None
        """

        if username not in self._files.keys():
            return

        data_path = self._files[username]
        with open(data_path, 'rb') as f:
            try:
                return pickle.load(f)
            except Exception as e:
                log.error(f"Error occurred while reading file `{data_path}`: {e}")
                raise e

    def _delete_data(self, username: str):
        import os

        if not self._files.get(username):
            error = f"Can't find checkpoint file for user: '{username}'."
            raise FileNotFoundError(error)

        os.remove(self._files[username])

    def get(self, username: str) -> Any:
        return self._load_data(username)

    def set(self, username: str, value: Any):
        return self._save_data(username, value)

    def delete(self, username: str):
        return self._delete_data(username)

