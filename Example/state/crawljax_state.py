from webdriver.state.i_state import State


class CrawlJaxState(State):
    def __init__(self, state_java_object, observation):
        self.source = state_java_object
        self.observation = observation

    def get_url(self):
        return self.source.getUrl()

    def get_dom(self):
        return self.source.getDom()

    def get_observation(self):
        return self.observation
