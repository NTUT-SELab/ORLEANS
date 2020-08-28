import requests


def is_server_active(server_port=3000, url=None, expected_status_code=200):
    server_url = "http://127.0.0.1:{port}/".format(port=str(server_port)) if url is None else url

    http_status_code = get_response_status_code(server_url)

    if http_status_code == expected_status_code:
        active = True
    else:
        active = False

    return active

def get_response_status_code(url=""):
    try:
        return requests.get(url).status_code
    except requests.exceptions.RequestException:
        return -1