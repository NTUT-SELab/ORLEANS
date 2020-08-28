from subprocess import Popen
from Example.factory.state_factory import StateFactory
from Example.factory.action_factory import ActionFactory
from webdriver.i_webdriver import WebDriver
from py4j.java_gateway import (
    JavaGateway, GatewayParameters, CallbackServerParameters)
import time
import os

EVENT_WAITING_TIME = 1000
PAGE_WAITING_TIME = 1000
MAX_CRAWLJAX_STEPS = 5000


class CrawlJax(WebDriver):
    def __init__(self, java_port=50000, python_port=50001, crawler_id=None, url=None, is_wrap_element=False,
                 is_headless=False):
        self._step_counter = 0
        self._total_step_counter = 0
        self._gateway = None
        self._web_snapshot = None
        self._id = crawler_id
        self._url = url
        self._wrapElement = is_wrap_element
        self._isHeadLess = is_headless
        self._is_open_application = False
        self._execution_total_time = 0.0
        self._state_factory = StateFactory()
        self._action_factory = ActionFactory()

        self._subProcess = Popen(['java',
                                  '-jar', os.getcwd() + '/Example/lib/irobot-crawler_no_record_version.jar',
                                  '-java_port', str(java_port),
                                  '-python_port', str(python_port)])
        time.sleep(5)
        self._build_gateway(python_port, java_port)

    def _build_gateway(self, python_port, java_port):
        """ Build connection with crawler

        :param python_port:
        :param java_port:
        :return:
        """
        gateway_parameters = GatewayParameters(port=java_port)
        callback_server_parameters = CallbackServerParameters(port=python_port)
        self._gateway = JavaGateway(
            gateway_parameters=gateway_parameters,
            callback_server_parameters=callback_server_parameters)
        self._gateway.setHeadLess(self._isHeadLess)
        self._gateway.setRecordBoolean(True)
        self._gateway.setWaitingTime(EVENT_WAITING_TIME, PAGE_WAITING_TIME)

    def open_application(self):
        """
        open the target url browser
        """
        self._step_counter += 1
        self._gateway.setUrl(self._url, self._wrapElement)
        self._web_snapshot = self._gateway.getWebSnapShot()
        self._is_open_application = True

    def restart_to_root_page(self):
        if self._step_counter > MAX_CRAWLJAX_STEPS:
            self._total_step_counter += self._step_counter
            self._step_counter = 0
            self._restart_crawler()
        else:
            self._restart_application()

    def close_webdriver(self):
        """
        1. close browser
        2. close java py4j server
        3. shut down py4j server
        4. terminate subprocess of crawler
        """
        self._gateway.terminateCrawler()
        self._gateway.close(False, True)
        self._gateway.shutdown(True)
        self._subProcess.terminate()

    def get_current_observation_and_actions(self):

        state = self._state_factory.create_state(state_java_object=self._web_snapshot.getState())
        low_level_actions = [self._action_factory.create_action(java_object) for java_object in
                             self._web_snapshot.getActions()]

        return state, low_level_actions

    def execute_action(self, low_level_action, value=None):
        """ Agent select element and let crawler click
        selected element.

        :param low_level_action:
        :param value:
        :return: boolean:
                    return the boolean crawler execute action success or not
        """
        self._step_counter += 1
        execute_success = self._gateway.executeAction(low_level_action.get_source(), value)
        self._web_snapshot = self._gateway.getWebSnapShot()
        return execute_success

    def execute_actions(self, low_level_actions_value_map=None):
        """ Agent select multiple action let crawler click
        selected element.

        :param low_level_actions_value_map:
        :return: boolean:
                    return the boolean crawler execute action success or not
        """
        if len(low_level_actions_value_map) is 0:
            return False
        element_value_pair = self._gateway.jvm.java.util.HashMap()
        for (low_level_action, value) in low_level_actions_value_map:
            element_value_pair.put(low_level_action.get_source(), value)

        self._step_counter += 1
        execute_success = self._gateway.executeActions(element_value_pair)
        self._web_snapshot = self._gateway.getWebSnapShot()
        return execute_success

    def get_execution_steps(self):
        return self._total_step_counter + self._step_counter

    def get_execution_total_time(self):
        """
        return the total execute time of crawler

        :return: crawling time
        """
        return self._gateway.getCrawlerSpendingTime()

    def _restart_application(self):
        self._step_counter += 1
        if self._is_open_application:
            self._gateway.restart()
            self._web_snapshot = self._gateway.getWebSnapShot()
        else:
            self.open_application()

    def _restart_crawler(self):
        """
        close the browser and open a new browser
        """
        self._step_counter = 1
        self._gateway.terminateCrawler()
        self._gateway.setUrl(self._url, True)
        self._web_snapshot = self._gateway.getWebSnapShot()

    def _is_elements_is_interactable(self, elements):
        self._step_counter += 1
        return self._gateway.isElementsInteractable(elements)
