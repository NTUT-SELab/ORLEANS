import math
import numpy as np
from gym.spaces.box import Box
from gym.spaces.discrete import Discrete
# interface
from action_strategy.i_action_strategy import ActionStrategy
from webdriver.action.i_low_level_action import DefaultAction
from Example.action_strategy.data_selector.data_selector import DataSelector

FOCUS_SIZE = 100
GROUP_SIZE = 30
EPISODE_STEPS = 60

"""
Case `All valid input` :
    (0) all input field fill in valid value， focus ++
    (1) focused input field fill in the `invalid value`, others input field fill in valid value, focus ++
    (2) focused input field fill in the `invalid value`, others input field don't change its value, focus ++
    (3) button 0, focus ++
    (4) button 1, focus ++
    (5) button 2, focus ++
    (6) button 3, focus ++
    (7) group++, focus ++
"""


class AllValidInput(ActionStrategy):
    def __init__(self, env_index=0):
        super().__init__()
        self._env_index = env_index
        self._action_set = 0
        self._current_step = 0
        self._episode_reward = 0
        self._total_step = 0
        self._group_index = 0
        self._group_quantity = 4
        self._reward = 0
        # for reward, previous step code coverage
        self._prev_coverage_count = 0

        self._input_index = 0
        self._button_index = 0
        self._low_level_actions = []
        self._input_element_list = []
        self._button_element_list = []
        self._is_changed_focus = False

        self._valid_value_list = {'email': DataSelector(name="valid_email",
                                                        data_list=["teacher@ntut.edu.tw", "student@ntut.edu.tw"]),
                                  'password_confirmed': DataSelector(name="valid_password_confirmed",
                                                                     data_list=["selab1421", "selab1623"]),
                                  'password-confirm': DataSelector(name="valid_password_confirmed",
                                                                   data_list=["selab1421", "selab1623"]),
                                  'password': DataSelector(name="valid_password", data_list=["selab1421", "selab1623"]),
                                  'other': DataSelector(name="other_valid", data_list=["other valid"])}
        self._invalid_value_list = {'email': DataSelector(name="invalid_email",
                                                          data_list=["ADi*ggMU%u", "*##&*%&*$$", "teacher@@ntut.tw",
                                                                     "teacher@ntut..tw"]),
                                    'password_confirmed': DataSelector(name="invalid_password_confirmed",
                                                                       data_list=["0", ""]),
                                    'password-confirm': DataSelector(name="valid_password_confirmed",
                                                                     data_list=["0", ""]),
                                    'password': DataSelector(name="invalid_password", data_list=["-", "1"]),
                                    'other': DataSelector(name="other_invalid", data_list=["other invalid"])}

        self.action_space = 8
        """
        observation shape = DOM + Coverage Vector + Focus Index + Group Index + Valid Index + Invalid Index

        DOM:
            which has been convert to Unicode
        Coverage Vector:
            a list of branch coverage which represented application coverage
        Focus Index:
            index of the focus on which element
        Group Index:
            click button will separate multiple group, and this index represent the current group 
        valid index:
            may have multiple dataset, so this index is point out which dataset
        invalid index：
            may have multiple dataset, so this index is point out which dataset
        """
        # only for `timeoff-managment` application
        shape = (1, 130100 + 1036 + 100 + 30 + 7 + 9, 1)

        self.action_space = Discrete(self.action_space)
        self.observation_shape = Box(low=0,
                                     high=300,
                                     shape=shape,
                                     dtype=np.float16)

    def get_action_state(self):
        """
        observation vector = (Focus index + Group index + valid index list + invalid index list)
                            (one_hot + one_hot + [] + [])
        Focus Index:
            index of the focus on which element, transferred in one hot, size = 6
        Group Index:
            click button will separate multiple group, and this index represent the current group,
            transferred in one hot, size = group_count
        valid index:
            may have multiple dataset, so this index is point out which dataset
        invalid index：
            may have multiple dataset, so this index is point out which dataset
        :return:
        """
        # Max button, link = 85, 85/3=29
        input_index_one_hot = _convert_to_one_hot(self._input_index, FOCUS_SIZE)
        group_index_one_hot = _convert_to_one_hot(self._group_index, GROUP_SIZE)

        valid_index_list_one_hot = _create_one_hot_vector(self._valid_value_list)
        invalid_index_list_one_hot = _create_one_hot_vector(self._invalid_value_list)

        # print("valid_index_list_one_hot", valid_index_list_one_hot)
        # print("invalid_index_list_one_hot", invalid_index_list_one_hot)

        return np.append(np.append(input_index_one_hot, group_index_one_hot),
                         np.append(valid_index_list_one_hot, invalid_index_list_one_hot))

    def get_initial_actions_before_episode(self):
        """
        get a low_level_action list contain multiple List of tuple
              type is like this: List< List< (low_level_action, value) > >

        :return:
                List<List<(low_level_action, value)>>
        """
        return []

    def convert_to_low_level_action(self, i_state, action):
        """
        do correspond action which agent gave
        :param i_state:
                current state
        :param action:
                which was agent gave
        :return:
                value:
                    string, the value should fill in the element
                target_element:
                    java object, which is correspond element
                is_change_focus:
                    boolean, if action is change focus then return True
                is_valid_action:
                    boolean, which is valid action
                element_value_list:
                    list, contain multiple pair (element, value)
        """
        self._current_step += 1
        self._total_step += 1
        value = None
        robot_action = action
        target_element = None
        self._is_changed_focus = False
        # print(self._env_index, ": Now action is ", action)

        self._update_action_set()

        # update group index (group ++)
        if robot_action == 7:
            is_valid_action = True
            self._update_group_index()
            self._is_changed_focus = True
            if self._action_set == 0:
                self._input_index += 1
            self._check_input_index()
            # print("group_index:", self._group_index)
            return target_element, value, is_valid_action, []
        # print("group_index:", self._group_index)
        return self._get_correspond_action(robot_action)

    def _update_action_set(self):
        """
        check is all input fill in, because all element which Crawljax crawled has been add <value> attribute,
        so can check current value on input element, that can solve the current value problem
        """
        self._action_set = 0
        for _, input_element in self._input_element_list:
            current_input_value = input_element.get_source().getValue()
            if current_input_value == "":
                self._action_set = 0
                break
        # print("action_set:", self._action_set)

    def _get_correspond_action(self, action):
        value = None
        target_element = None
        self._is_valid_action = False
        element_value_list = []

        # fill in all valid input, `all valid index` ++
        if action == 0:
            if len(self._input_element_list) == 0:
                return None, None, False, None
            self._is_valid_action = True
            element_value_list = self._create_valid_input_pair()
            self._input_index += 1
            self._check_input_index()

        # fill in all valid input, `all valid index` ++, set Invalid value with focus item
        elif action == 1:
            if len(self._input_element_list) == 0:
                return None, None, False, None
            self._is_valid_action = True
            target_element = self._get_focus_input()
            # print("==target==", target_element.toString())

            # If page has no input, set as invalid action
            if target_element is None:
                self._is_valid_action = False
            else:
                _, target_element_value = self._get_the_invalid_value_which_represent_the_focused_input(target_element)
                element_value_list = self._create_valid_input_pair()
                element_value_list[self._input_index] = (
                    self._low_level_actions[self._input_element_list[self._input_index][0]], target_element_value)
            self._input_index += 1
            self._check_input_index()

        #  set Invalid value with focus item
        elif action == 2:
            if len(self._input_element_list) == 0:
                return None, None, False, None
            self._is_valid_action = True
            target_element = self._get_focus_input()

            # If page has no input, set as invalid action
            if target_element is None:
                self._is_valid_action = False
            else:
                _, target_element_value = self._get_the_invalid_value_which_represent_the_focused_input(target_element)
                element_value_list.append(
                    (self._low_level_actions[self._input_element_list[self._input_index][0]], target_element_value))
            self._input_index += 1
            self._check_input_index()

        # click button, if action_set = 0, change focus
        elif 2 < action < 7 and self._is_valid_button_index(action_index=action):
            self._is_valid_action = True
            target_element = self._get_focus_button()
            if self._action_set == 0:
                self._input_index += 1
                self._check_input_index()

        return target_element, value, self._is_valid_action, element_value_list

    def _check_input_index(self):
        if self._input_index >= len(self._input_element_list):
            self._input_index = 0

    def _get_focus_input(self):
        target_input = None
        if len(self._input_element_list) == 0:
            return target_input
        self._check_input_index()

        _, target_input = self._input_element_list[self._input_index]

        return target_input

    def do_post_action_processing(self, i_state, low_level_actions):
        """
        create a valid element list for timeoff-management

        :param i_state:
                current state
        :param low_level_actions:
                webdriver found
        """
        self._action_set = 0
        self._input_element_list = []
        self._low_level_actions = low_level_actions
        self._button_element_list = []
        for index, low_level_action in enumerate(low_level_actions):
            if _is_input_element(low_level_action):
                # self._action_set = 0
                self._input_element_list.append((index, low_level_action))
            else:
                self._button_element_list.append((index, low_level_action))

    def get_reward(self, i_state, action, is_execute_success, coverage_vector):
        if self._is_changed_focus:
            reward = -7 * 0.05
        else:
            covered_count = coverage_vector.count(300)
            if covered_count > self._prev_coverage_count:
                reward = (covered_count - self._prev_coverage_count) * 10
            else:
                reward = -5 * 0.05
            self._prev_coverage_count = covered_count
        # print("reward:", reward)
        self._reward = reward
        self._episode_reward += reward
        print(self._env_index, ":Total Step: " + str(self._total_step) + ":",
              "action:" + str(action) + "  " + str(round(reward, 2)),
              "episode reward: " + str(round(self._episode_reward, 2)),
              "coverage:", _get_coverage(coverage_vector))

        return reward

    def get_isDone(self):
        if self._current_step >= EPISODE_STEPS:
            self._current_step = 0
            return True
        return False

    def get_info(self):
        return {"Reward": self._reward}

    def reset(self):
        """
        reset the focus index and element mask
        """
        self._episode_reward = 0
        self._action_set = 0
        self._group_index = 0
        self._input_index = 0
        self._button_index = 0
        self._reset_all_data_selector()
        self._input_element_list = []
        self._button_element_list = []

    def _reset_all_data_selector(self):
        for (_, dataSelector) in self._valid_value_list.items():
            dataSelector.reset()
        for (_, dataSelector) in self._invalid_value_list.items():
            dataSelector.reset()

    def _get_the_valid_value_which_represent_the_focused_input(self, target_element=None):
        if target_element is None:
            raise RuntimeError("Something wrong when get the valid value for focus input...")
        unique_string = target_element.get_source().getSource().getUniqueString().lower()

        for keyword, selector in self._valid_value_list.items():
            if keyword in unique_string:
                return keyword, selector.get_value_and_increment_index()
        return 'other', self._valid_value_list['other'].get_value_and_increment_index()

    def _get_the_invalid_value_which_represent_the_focused_input(self, target_element=None):
        if target_element is None:
            raise RuntimeError("Something wrong when get the invalid value for focus input...")
        unique_string = target_element.get_source().getSource().getUniqueString().lower()

        if "checkbox" in unique_string:
            print("=====checkbox=====")
            return 'other', "False"
        for keyword, selector in self._invalid_value_list.items():
            if keyword in unique_string:
                return keyword, selector.get_value_and_increment_index()
        return 'other', self._invalid_value_list['other'].get_value_and_increment_index()

    def _get_focus_button(self):
        return self._button_element_list[self._button_index][1]

    def _is_valid_button_index(self, action_index=0):
        self._button_index = self._group_quantity * self._group_index + action_index
        self._button_index -= 3
        # print("button_index", self._button_index)

        if self._button_index >= len(self._button_element_list):
            return False
        return True

    def _update_group_index(self):
        group_count = math.ceil(len(self._button_element_list) / self._group_quantity)
        if group_count is 0:
            group_count = 1
        self._group_index = (self._group_index + 1) % group_count
        # print(self._env_index, ": change group, new group index is ", self._group_index)

    def _check_password_index_same(self):
        password_index = 0
        for keyword, selector in self._valid_value_list.items():
            if keyword == "password":
                password_index = selector.get_index()
        for keyword, selector in self._valid_value_list.items():
            if keyword == "password_confirmed" or keyword == "password-confirm":
                if selector.get_index() != password_index:
                    selector.set_index(password_index)

    def _create_valid_input_pair(self):
        valid_input_pair = []
        value_pair = {}
        for index, element in self._input_element_list:
            valid_value = _get_the_correspond_value(element, value_pair,
                                                    self._get_the_valid_value_which_represent_the_focused_input)
            valid_input_pair.append((self._low_level_actions[index], valid_value))
        self._check_password_index_same()
        return valid_input_pair

    def _create_invalid_input_pair(self):
        invalid_input_pair = []
        value_pair = {}
        for index, element in self._input_element_list:
            invalid_value = _get_the_correspond_value(element, value_pair,
                                                      self._get_the_invalid_value_which_represent_the_focused_input)
            if self._input_index is not index:
                invalid_input_pair.append((self._low_level_actions[index], invalid_value))
        return invalid_input_pair


def _get_coverage(coverage_vector):
    code_coverage = coverage_vector
    if len(code_coverage) == 0:
        return 0
    return round(code_coverage.count(300) * 100 / len(code_coverage), 2)


def _get_the_correspond_value(element=DefaultAction(), value_pair=None, get_value_function=None):
    if element is None or value_pair is None or get_value_function is None:
        raise RuntimeError()
    keyword, value = get_value_function(element)
    return value


def _create_one_hot_vector(target):
    one_hot_list = np.array([])
    target_index_list = [selector.get_index() for _, selector in target.items()]
    target_index_list_size = [selector.get_list_size() for _, selector in target.items()]
    for i in range(len(target_index_list)):
        one_hot_list = np.append(one_hot_list,
                                 _convert_to_one_hot(target_index_list[i], target_index_list_size[i]))
    return one_hot_list


def _convert_to_one_hot(number, size):
    one_hot = np.zeros(size)
    if size == 0:
        return None
    if number > (size - 1):
        number = number % size
    one_hot[number] = 300
    return one_hot


def _is_input_element(low_level_action=DefaultAction()):
    return True if (low_level_action is not None) and (
                low_level_action.get_action_type().lower() == "INPUT".lower()) else False


def _is_click_element(low_level_action=DefaultAction()):
    return True if (low_level_action is not None) and (
                low_level_action.get_action_type().lower() != "INPUT".lower()) else False
