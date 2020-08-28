import abc


class LowLevelAction(abc.ABC):
    @abc.abstractmethod
    def get_action_type(self):
        pass

    @abc.abstractmethod
    def get_component_xpath(self):
        pass

    @abc.abstractmethod
    def get_component_location(self):
        pass

    @abc.abstractmethod
    def get_component_html_code(self):
        pass


class DefaultAction(LowLevelAction):
    def get_action_type(self):
        raise NotImplementedError

    def get_component_xpath(self):
        raise NotImplementedError

    def get_component_location(self):
        raise NotImplementedError

    def get_component_html_code(self):
        raise NotImplementedError
