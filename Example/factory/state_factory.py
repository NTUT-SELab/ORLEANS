from Example.state.crawljax_state import CrawlJaxState
from Example.factory.stateprocessor.html_state_processor import HtmlStateProcessor


class StateFactory:
    def create_state(self, state_java_object):
        dom = state_java_object.getDom()
        processor = HtmlStateProcessor()
        ascii_dom = processor.get_unicodes(ascii_string=dom)
        return CrawlJaxState(state_java_object, ascii_dom)
