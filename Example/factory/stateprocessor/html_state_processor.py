import numpy as np


HTML_LENGTH = 130000


class HtmlStateProcessor:

    def __init__(self):
        super().__init__()

    def get_unicodes(self, ascii_string):
        n = 1
        ascii_list = [ascii_string[ascii_code:ascii_code + n] for ascii_code in range(0, len(ascii_string), n)]
        unicodes = list(ord(ascii_code) for ascii_code in ascii_list)

        return self.pad_state_ob_with_space(np.array(unicodes))

    def pad_state_ob_with_space(self, state_ob):
        # print("state_ob:", len(state_ob))
        if len(state_ob) > 130000:
            state_ob = state_ob[:130000]
        return np.pad(state_ob, (50, 130050 - len(state_ob)), 'constant', constant_values=32)
