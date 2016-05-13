import json
import os
import shutil

import numpy as np

from lsa.keeper import base


class JsonIndexBackend(base.BaseIndexBackend):
    def __init__(self, **keep_index_info):
        self.index_folder = keep_index_info.get('path_to_index_folder')
        self.manage_index_folder()

    def manage_index_folder(self):
        # TODO: сделать проверку прав на запись и чтение в path_to_index_folder
        if not os.path.exists(self.index_folder):
            os.makedirs(self.index_folder)

    def dump(self, obj, file_name):
        self.manage_index_folder()
        file_path = os.path.join(self.index_folder, file_name)
        if isinstance(obj, np.matrix):
            obj = obj.tolist()
        with open(file_path, 'w') as file:
            json.dump(obj, file)

    def load(self, file_name, return_matrix=False):
        file_path = os.path.join(self.index_folder, file_name)
        with open(file_path, 'r') as file:
            obj = json.load(file)
        if return_matrix:
            return np.matrix(obj)
        return obj

    def delete_index(self):
        if os.path.exists(self.index_folder):
            shutil.rmtree(self.index_folder)
