import abc


class State(abc.ABC):
    @abc.abstractmethod
    def get_url(self):
        return ""

    @abc.abstractmethod
    def get_dom(self):
        return ""

    @abc.abstractmethod
    def get_observation(self):
        return []


class DefaultState(State):
    def get_url(self):
        raise NotImplementedError

    def get_dom(self):
        raise NotImplementedError

    def get_observation(self):
        raise NotImplementedError
