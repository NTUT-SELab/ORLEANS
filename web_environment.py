import gym
import numpy as np

# -------------- Interface ----------------
from action_strategy.i_action_strategy import DefaultActionStrategy
from code_coverage.i_code_coverage_collector import DefaultCoverageCollector
from server_instance.i_server_instance_manager import DefaultServerInstanceManager
from webdriver.i_webdriver import DefaultWebDriver


class WebEnvironment(gym.Env):
    # WebDQN 訓練環境
    metadata = {'render.modes': ['human', 'system', 'none']}

    def __init__(self, env_index=0,
                 webdriver=DefaultWebDriver(),
                 action_strategy=DefaultActionStrategy(),
                 server_instance=DefaultServerInstanceManager(),
                 code_coverage_collector=DefaultCoverageCollector(3000)):
        # accept concrete classes for each interface
        self._webdriver = webdriver
        self._action_strategy = action_strategy
        self._server_instance = server_instance
        self._code_coverage_collector = code_coverage_collector

        self._total_step = 0
        self._current_step = 0
        # self._episode_reward = 0
        self._env_index = env_index
        self._is_valid_action = False

        # For openAI
        #   get the action_space and observation_space from ActionStrategy
        self.action_space = self._action_strategy.action_space
        self.observation_space = self._action_strategy.observation_shape

        # observation state
        self._next_state = None
        self._next_state_valid_actions = None

    def reset(self):
        # print("Reset")
        self._current_step = 0
        self._restart_episode()
        self._init_application()
        self._action_strategy.reset()
        return self._next_observation()

    def _restart_episode(self):
        self._server_instance.close_server_instance()
        self._server_instance.create_server_instance()
        self._code_coverage_collector.reset_coverage()
        self._action_strategy.reset()
        self._webdriver.restart_to_root_page()
        self._get_observations()

    def _get_observations(self):
        state, low_level_actions = self._webdriver.get_current_observation_and_actions()
        self._action_strategy.do_post_action_processing(state, low_level_actions)
        self._next_state = state

    def _init_application(self):
        initial_application_list = self._action_strategy.get_initial_actions_before_episode()
        if len(initial_application_list) != 0:
            for low_level_action_value_set in initial_application_list:
                self._webdriver.execute_actions(low_level_action_value_set)
                self._get_observations()

    def _next_observation(self):
        # The observation is a array,
        #   default is (DOM ASCII Array + CodeCoverageVector + actions info from ActionStrategy)
        observation = np.concatenate([self._next_state.get_observation(),
                                      np.asarray(self._code_coverage_collector.get_coverage_vector()),
                                      self._action_strategy.get_action_state()])
        # then convert to neural-net input shape
        observation.resize(self.observation_space.shape)
        return observation

    def step(self, action):
        target_element, value, element_value_list = self._convert_to_domain_ops(action)

        if self._is_valid_action is not False:
            self._execute_actions(target_element, value, element_value_list)
            self._get_observations()

        reward = self._action_strategy.get_reward(self._next_state,
                                                  action,
                                                  self._is_valid_action,
                                                  self._code_coverage_collector.get_coverage_vector())
        self._total_step += 1
        self._current_step += 1

        # print(self._env_index, ":Step: " + str(self._total_step) + ":",
        #       "action:" + str(action) + "  " + str(round(reward, 2)),
        #       "episode reward: " + str(round(self._episode_reward, 2)),
        #       "coverage:", self.get_coverage())

        return self._next_observation(), reward, self._action_strategy.get_isDone(), self._action_strategy.get_info()

    def _convert_to_domain_ops(self, action):
        target_element, value, is_valid_action, element_value_list = \
            self._action_strategy.convert_to_low_level_action(self._next_state, action)
        self._is_valid_action = is_valid_action

        return target_element, value, element_value_list

    def _execute_actions(self, target_element, value, element_value_list):
        if len(element_value_list) != 0:
            self._is_valid_action = self._webdriver.execute_actions(element_value_list)
            self._get_observations()
        elif (target_element is not None) and self._is_valid_action:
            self._is_valid_action = self._webdriver.execute_action(target_element, value)
            self._get_observations()

    def render(self, mode='human'):
        coverage_vector = self._code_coverage_collector.get_coverage_vector().count(300)
        coverage_vector_percentage = coverage_vector / len(self._code_coverage_collector.get_coverage_vector())
        print("current_actions:", len(self._next_state_valid_actions))
        print("coverage_vector count:", coverage_vector)
        print("coverage_vector_percentage:", coverage_vector_percentage)

    def close(self):
        print("Closing the Environment....")
        print("Env index :", self._env_index, ", Crawljax crawling time:", self._webdriver.get_execution_total_time())
        self._webdriver.close_webdriver()
        self._server_instance.close_server_instance()
