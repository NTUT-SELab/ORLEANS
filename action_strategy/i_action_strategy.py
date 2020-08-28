import abc
import numpy as np
from gym.spaces.box import Box
from gym.spaces.discrete import Discrete


class ActionStrategy(abc.ABC):
    @abc.abstractmethod
    def __init__(self):
        self.action_space = Discrete(1)
        self.observation_shape = Box(low=0,
                                     high=300,
                                     shape=(1, 1),
                                     dtype=np.float16)

    @abc.abstractmethod
    def reset(self):

        """
        reset the cache in strategy
        """
        pass

    @abc.abstractmethod
    def get_action_state(self):
        """
        get the information of action strategy which want to append on observation

        :return: [] (list of type float)
        """
        pass

    @abc.abstractmethod
    def get_initial_actions_before_episode(self):
        """
        get the initial actions before episode, and the webdriver will execute this actions

        :return: List<Pair<LowLevelAction, value>>
        """
        pass

    @abc.abstractmethod
    def convert_to_low_level_action(self, i_state, action):
        """
        this will convert the action which agent selected
             and give environment correspond action
        :param i_state:
            which is current state
        :param action:
            which is agent selected
        :return:
            1. is_valid_action : boolean
            2. actions_values_list: List<Pair<LowLevelAction, value>>
        """
        pass

    @abc.abstractmethod
    def do_post_action_processing(self, i_state, low_level_actions):
        """
        this will let ActionStrategy update their state and low_level_actions

        :param i_state:
            which is current state
        :param low_level_actions:
            which is all low_level_action represent in current state
        """
        pass

    @abc.abstractmethod
    def get_reward(self, i_state, action, is_execute_success, coverage_vector):
        """
        will calculate the reward according arguments

        :param i_state:
            current state
        :param action:
            which agent selected
        :param is_execute_success:
            the boolean which agent selected action is a effective aciton
        :param coverage_vector:
            which is a integer array
        :return:
            reward : float
        """
        pass

    @abc.abstractmethod
    def get_isDone(self):
        """
        this will tell agent this episode is done or not

        :return: isDone : boolean
        """
        pass

    @abc.abstractmethod
    def get_info(self):
        """
        this will get the info which is present in gym.Env.step()

        :return: info : dictionary
        """
        pass


class DefaultActionStrategy(ActionStrategy):
    def __init__(self):
        super().__init__()

    def reset(self):
        raise NotImplementedError

    def get_action_state(self):
        raise NotImplementedError

    def get_initial_actions_before_episode(self):
        raise NotImplementedError

    def convert_to_low_level_action(self, i_state, action):
        raise NotImplementedError

    def do_post_action_processing(self, i_state, low_level_actions):
        raise NotImplementedError

    def get_reward(self, i_state, action, is_execute_success, coverage_vector):
        raise NotImplementedError

    def get_isDone(self):
        raise NotImplementedError

    def get_info(self):
        raise NotImplementedError
