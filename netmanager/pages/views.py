# -*- coding: utf-8 -*-
from flask import Blueprint, render_template
from flask import current_app, jsonify, request, flash, redirect, url_for
from . import Pagination, crossdomain

import sys

import pprint
import datetime
from collections import namedtuple

from pytz import timezone

from .snow import SnowForm
from .device import AddDeviceConfigurationForm, DeviceForm, AddDeviceForm
from .helpers.rest import get_url, get_rest_command, select_keys, get_sites, get_site, get_vlans, get_devices, get_info
from .site import SearchSiteForm, AddSiteForm
from .router import RouterConfigForm

import json
import requests
import wtforms_json
from flask import request

requests.packages.urllib3.disable_warnings()

PER_PAGE = 15

DateInterval = namedtuple('DateInterval', 'value description range')

DATE_INTERVALS = [
    DateInterval(value='today',      description='Today',            range={"gt": "now-1d/d",  "lte": "now/d"}),
    DateInterval(value='thisweek',   description='Previous 7 days',  range={"gt": "now-7d/d",  "lte": "now"}),
    DateInterval(value='thismonth',  description='Previous 30 days', range={"gt": "now-30d/d", "lte": "now"}),
    DateInterval(value='tomorrow',   description='Tomorrow',         range={"gte": "now",      "lte": "now+1d/d"}),
    DateInterval(value='nextweek',   description='Next 7 days',      range={"gte": "now",      "lte": "now+7d/d"}),
    DateInterval(value='everything', description='Everything',       range=None),
]

pages_app = Blueprint('pages_app', __name__)

@pages_app.route('/hello')
def index():
    return render_template('pages/index.html')

@pages_app.route('/about')
def about():
    return render_template('pages/about.html')


@pages_app.route('/cost')
def cost():
    return render_template('pages/cost.html')


@pages_app.route('/find', methods=['POST'])
def boxsearch():
    data = request.form
    pprint.pprint(data)
    return render_template('pages/element.html')


@pages_app.route('/snow', methods=('GET', 'POST'))
def snow():
    form = SnowForm()
    form.validate_on_submit()
    if form.is_submitted():
        site_name = request.form.get('site_name')
        payload = select_keys(request.form, ['category', 'delete_if_exists', 'kbps'])
        r = requests.post(current_app.config['API_ENDPOINT'] + '_snow/{}'.format(site_name), data=payload, verify=False)
        print(current_app.config['API_ENDPOINT'] + '_snow/{}'.format(site_name))
        if r.status_code == 200:
            flash("{} - {}".format(r.status_code, '{} created'.format(site_name)), 'info')
        else:
            flash("{} - {}".format(r.status_code, r.text), 'error')
        return render_template('pages/snow.html', form=form)
    return render_template('pages/snow.html', form=form)


@pages_app.route('/add-site', methods=('GET', 'POST'))
def add_site():
    form = AddSiteForm()
    form.validate_on_submit()
    if form.is_submitted():
        site_name = request.form.get('site_name')
        payload = select_keys(request.form, ['users', 'ipphones'])
        #headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}
        r = requests.post(current_app.config['API_ENDPOINT'] + 'sites/{}'.format(site_name), data=payload, verify=False)
        print(current_app.config['API_ENDPOINT'] + 'sites/{}'.format(site_name))
        print(payload)
        print(r.status_code)
        if r.status_code == 200:
            flash("{} - {}".format(r.status_code, '{} created'.format(site_name)), 'info')
            return render_template('pages/site.html', data=json.loads(r.text))
        else:
            flash("{} - {}".format(r.status_code, json.loads(r.text)['message']), 'error')
        print('wahappa')
        return render_template('pages/site-add.html', form=form)
    return render_template('pages/site-add.html', form=form)



# this route is not needed, addition of a device will work anyway
@pages_app.route('/device', methods=('GET', 'POST'))
def device():
    form = DeviceForm()
    form.validate_on_submit()
    if form.is_submitted():
        return render_template('pages/device.html', form=form)
    return render_template('pages/device.html', form=form)


@pages_app.route('/', methods=('GET', 'POST'))
@pages_app.route('/site', methods=('GET', 'POST'))
def site():
    form = SearchSiteForm(request.values)
    form.validate_on_submit()

    print(request.method)
    print(request.form)

    if form.is_submitted():
        if 'submit_add_device' in request.form:
            print("Got a submit event on the AddDevice form")
            submitted = request.form.to_dict(flat=True)
            submitted.pop('csrf_token', None)
            print("SUBMITTED DEVICE", submitted)
            add_device = DeviceForm(site_name=submitted['site_name'], dev_cfg=submitted['dev_cfg'])
            add_device.site_name.render_kw = {'readonly': True}
            add_device.dev_cfg.render_kw = {'readonly': True}
            add_device.dev_cfg.description = '' # just to remove the description
            return render_template('pages/device.html', form=add_device)

        if 'submit_device' in request.form:
            print("Got a submit event on the Device form")
            submitted = request.form.to_dict(flat=True)
            submitted.pop('csrf_token', None)
            # submitted['site'] = submitted.pop('site_name')
            # submitted['site_name'] = submitted['site']
            # submitted['auto_connect'] = submitted.get('auto_connect', 'false').replace('y', 'true')
            if submitted.get('auto_connect'):
                submitted['auto_connect'] = submitted.get('auto_connect').replace('y', 'true')
            # submitted.pop('stack_partner', None)
            submitted.pop('submit_device', None)
            # TODO: actually insert 'submitted' into a database somewhere
            # i.e. call the rest endpoint
            print("CALL post_url with {}".format(submitted))
            # CALL post_url with {'dev_cfg': 'string3', 'building': 'HB2', 'df': 'M01', 'serial': '15135424',
            #                     'stack_partner': '123', 'wan_line': 'adsga', 'site': 'DKAARHED42',
            #                     'auto_connect': 'false'}
            r = requests.post(current_app.config['API_ENDPOINT'] + 'devices', data=submitted, verify=False)
            print('post_url responds with: ')
            print(r.text)
            if r.status_code == 500:
                flash("{} - {}".format(r.status_code, r.text), 'info')
            # if r.status_code != 200:
            #    add_device = AddDeviceForm(request.values)
            #    return render_template('device.html', form=add_device)
            submitted['site'] = submitted.pop('site_name')
            if r.status_code == 200:
                flash('{} was added added to {} - {}'.format(submitted['dev_cfg'], submitted['site'], submitted['df']), 'info')

        if ('submit_search_site' in request.form and bool(form.site_name.data)) or 'submit_device' in request.form:
            # DATA FOR THE "SHOW SITE INFORMATION" Page
            #
            data = get_site(form.site_name.data)
            vlans = None
            devices = None
            add_device = None

            if bool(data):
                vlans = get_vlans(form.site_name.data)
                devices = get_devices(form.site_name.data)
                add_device = AddDeviceForm(request.values)
                if bool(data.get('device_configurations')):
                    print(data['device_configurations'])
                    choices = [(device['name'], device['name']) for device in data['device_configurations']]
                    add_device.dev_cfg.choices = choices

            return render_template('pages/site-search.html', form=form, vlans=vlans, devices=devices, data=data, add_device=add_device)
        return render_template('pages/site-search.html', form=form)
    return render_template('pages/site-search.html', form=form)


@pages_app.route('/sites', methods=('GET', 'POST'))
def sites():
    data = get_sites()
    print(data)
    return render_template('pages/sites.html', sites=data)


@pages_app.route('/configure', methods=('GET', 'POST'))
def configure():
    form = RouterConfigForm()
    form.validate_on_submit()  # to get error messages to the browser
    print("configuring%s+%s" % (form.router.data, form.switch.data) + " with SNOW ID: %s " % (form.snow.data) + " %s APs" % (form.aps.data))

    if form.is_submitted():
        url = current_app.config['API_ENDPOINT'] + "sites"
        r = requests.get(url)
        print(r.text)
        # a form that is able to show the information will need to be made
        return render_template('pages/configuring.html', form=form)

    return render_template('pages/configure.html', form=form)


def _from_utc(utcTime, fmt="%Y-%m-%dT%H:%M:%S.%fZ"):
    """
    Convert UTC time string to time.struct_time
    """
    utcdatetime = datetime.datetime.strptime(utcTime, fmt)
    localdatetime = timezone(current_app.config['ADE_TIMEZONE']).fromutc(utcdatetime)
    return localdatetime



