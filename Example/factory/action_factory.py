from Example.action.crawljax_action import CrawlJaxAction


class ActionFactory:
    def create_action(self, action_java_object):
        return CrawlJaxAction(action_java_object)
