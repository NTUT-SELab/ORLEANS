import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


class RequestHandler:

    def __init__(self, server_port=3000):
        self._URL = 'http://127.0.0.1:{port}'.format(port=server_port)
        self.session = self._requests_retry_session()
        # self._setup_cookies()

    def get_branch_coverage_vector(self):
        try:
            # return global coverage object on /coverage/object as JSON
            # for more info, consult the istanbul-middleware utils docs
            response = self.session.get("{}{}".format(self._URL, "/coverage/object"))
            composed_dict = [v['b'].values() for v in response.json().values()]
            flatten_list = [item for sublist in [item for sublist in composed_dict for item in sublist] for item in sublist]
            return flatten_list
        except Exception as e:
            print("Failed at getting coverage", e.__class__.__name__)

    def get_state_coverage_vector(self):
        try:
            # return global coverage object on /coverage/object as JSON
            # for more info, consult the istanbul-middleware utils docs
            response = self.session.get("{}{}".format(self._URL, "/coverage/object"))
            composed_dict = [v['s'].values() for v in response.json().values()]
            flatten_list = [item for sublist in composed_dict for item in sublist]
            return flatten_list
        except Exception as e:
            print("Failed at getting coverage", e.__class__.__name__)

    def reset_coverage(self):
        try:
            # istanbul allows reset on GET as well
            # so here we simply use GET to reset the coverage
            response = self.session.get("{}{}".format(self._URL, "/coverage/reset"))
        except Exception as e:
            print("Failed at resetting coverage", e.__class__.__name__)
        else:
            if response.status_code != requests.codes.ok:
                raise Exception('Reset coverage error!')

    def _requests_retry_session(self, retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None):
        session = session or requests.Session()
        retry = Retry(total=retries, read=retries, connect=retries, backoff_factor=backoff_factor, status_forcelist= status_forcelist)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def _setup_cookies(self):
        # hard-code cookies
        # cookies = requests.cookies.RequestsCookieJar()
        # self.session.cookies["connect.sid"] = "s%3A_MefiYjLHfo3gEoikMhro-QRbXDiuaIQ.qLyFNjmz4y2pYqHWY1Q6gzTBh1qNiJR%2BGOmSzQyTF0Q"

        # hit the login utils to get cookies
        # requests.Session takes care of the rest
        url = self._URL + "/login"
        paras = {"username": "test@gmail.com", "password": "1234"}
        response = self.session.post(url=url, data=paras)
        # use content of response to force connection to return into the connection pool
        cookies = response.cookies.get_dict()
