class DataSelector(object):
    def __init__(self, name=None, data_list=None):
        if data_list is None:
            data_list = []

        if name is None:
            name = "NoNameDataSet"
        self._name = name
        self._data_index = 0
        self._data_list = data_list

    def get_value_and_increment_index(self):
        value = self._data_list[self._data_index]
        self._update_data_index()
        return value

    def _update_data_index(self):
        self._data_index += 1
        self._data_index %= len(self._data_list)

    def get_index(self):
        return self._data_index

    def reset(self):
        self._data_index = 0

    def get_list_size(self):
        return len(self._data_list)

    def set_index(self, setting):
        self._data_index = setting
