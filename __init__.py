import requests
import backoff

import logging
#
# Turn off gratuitous logging.
#
logging.getLogger('chardet.charsetprober').setLevel(logging.INFO)

# https://2.python-requests.org/en/latest/user/advanced/#proxies
#
def proxy_dictionary(proxy):
    if proxy:
        return {
            "http": proxy,
            "https": proxy,
        }
    else:
        return None

# A fault-tolerant version of requests.post().
#
# headers - dictionary
# cookies - dictionary
#
@backoff.on_exception(
    backoff.expo,
    (requests.exceptions.HTTPError,
     requests.exceptions.ConnectionError,
     requests.exceptions.Timeout,
     requests.exceptions.ConnectTimeout,
     requests.exceptions.ReadTimeout,
     requests.exceptions.ChunkedEncodingError),
    max_tries=8)
def post(url, headers, data, cookies=None, proxy=None):
    return requests.post(
        url,
        headers=headers,
        data=data,
        cookies=cookies,
        proxies=proxy_dictionary(proxy)
        )

# A fault-tolerant version of requests.get().
#
@backoff.on_exception(
    backoff.expo,
    (requests.exceptions.HTTPError,
     requests.exceptions.ConnectionError,
     requests.exceptions.Timeout,
     requests.exceptions.ConnectTimeout,
     requests.exceptions.ReadTimeout,
     requests.exceptions.ChunkedEncodingError),
    max_tries=8)
def get(url, headers=None, proxy=None, deserialise=False):
    response = requests.get(
        url,
        headers=headers,
        proxies=proxy_dictionary(proxy)
        )
    
    if response.status_code == 503:
        logging.warning("Got 503 response.")
        raise requests.exceptions.HTTPError
    
    if deserialise:
        return response.json()
    else:
        return response