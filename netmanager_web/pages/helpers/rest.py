from flask import flash, current_app
import json
import requests

from retrying import retry


def retry_if_HTTP404(exception):
    return isinstance(exception, requests.exceptions.HTTPError) and exception.response.status_code == 404

def retry_if_HTTP500(exception):
    return isinstance(exception, requests.exceptions.HTTPError) and exception.response.status_code == 500


@retry(stop_max_attempt_number=5, wait_exponential_multiplier=100, retry_on_exception=retry_if_HTTP500)
def get_url(url):
    try:
        r = requests.get(url, verify=False)
        r.raise_for_status()
        return r
    except requests.exceptions.HTTPError as e:
        print(e)
        raise e


def get_rest_command(url, command):
    data = []
    url = "{url}/{command}".format(url=url.strip("/"), command=command)
    try:
        r = get_url(url)
        data = json.loads(r.text)
    except requests.exceptions.HTTPError as e:
        try:
            message=json.loads(e.response.text)['message']
            flash("{} - {}".format(e.response.status_code, message), 'warning')
        except json.decoder.JSONDecodeError as ee:
            flash('{} - {} - has disappeared'.format(e.response.status_code, url), 'error')
            flash('{}'.format( e.response.text ), 'warning')
            print(ee)
        return data
    return data

# helper functions for interacting ith the API endpoint
get_info = lambda command: get_rest_command(current_app.config['API_ENDPOINT'], command)
get_sites = lambda : get_info("sites")
search_site = lambda site : get_info("sites/{}".format(site))
get_site = lambda site : get_info("sites/{}?list_viable_devices=true".format(site))
get_vlans = lambda site : get_info("sites/{}/vlans".format(site))
get_devices = lambda site : get_info("sites/{}/devices".format(site))
#post_devices = lambda site : get_info("devices".format(site))

select_keys = lambda dictionary, x: {key : dictionary.get(key) for key in dictionary.keys() if key in x}
