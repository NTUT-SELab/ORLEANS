from webdriver.action.i_low_level_action import LowLevelAction


class CrawlJaxAction(LowLevelAction):
    def __init__(self, action_java_object):
        self.source = action_java_object

    def get_action_type(self):
        if self.source.getType().upper() == "INPUT":
            return "INPUT"
        else:
            return "CLICK"

    def get_component_xpath(self):
        return self.source.getXpath()

    def get_component_location(self):
        return "Not implement...."

    def get_component_html_code(self):
        return self.source.getSource().getGeneralString()

    def get_source(self):
        return self.source
