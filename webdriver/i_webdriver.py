import abc


class WebDriver(abc.ABC):
    @abc.abstractmethod
    def open_application(self):
        """
        let webdriver open the browser and go to application page
        """
        pass

    @abc.abstractmethod
    def restart_to_root_page(self):
        """
        restart the applications and go to initial state
        """
        pass

    @abc.abstractmethod
    def close_webdriver(self):
        """
        terminate the crawler
        """
        pass

    @abc.abstractmethod
    def execute_action(self, low_level_action, value=None):
        """
        let crawler to execute action and fill in the value which you gave

        :param low_level_action:
                    the action which you want to execute
        :param value:
                    the value which you want to fill in (ex: fill in the input field)
        """
        pass

    @abc.abstractmethod
    def execute_actions(self, low_level_actions_values_list=None):
        """
        let crawler to execute action and fill in the value which you gave

        :param low_level_actions_values_list:
                   multiple low_level_action value pair which you want to execute multiple action at one time
                   ex: fill in all input
        """
        pass

    @abc.abstractmethod
    def get_current_observation_and_actions(self):
        """
        get the state and actions which crawler crawled

        :return: state(State), low_level_actions(List<LowLevelAction>)
        """
        pass

    @abc.abstractmethod
    def get_execution_steps(self):
        """
        return the total execute steps of crawler

        :return: steps (int)
        """
        pass

    @abc.abstractmethod
    def get_execution_total_time(self):
        """
        return the total execute time of crawler

        :return: time(time)
        """
        pass


class DefaultWebDriver(WebDriver):
    def open_application(self):
        raise NotImplementedError

    def restart_to_root_page(self):
        raise NotImplementedError

    def close_webdriver(self):
        raise NotImplementedError

    def execute_action(self, low_level_action, value=None):
        raise NotImplementedError

    def execute_actions(self, low_level_actions_values_list=None):
        raise NotImplementedError

    def get_current_observation_and_actions(self):
        raise NotImplementedError

    def get_execution_steps(self):
        raise NotImplementedError

    def get_execution_total_time(self):
        raise NotImplementedError
