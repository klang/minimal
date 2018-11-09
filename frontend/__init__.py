from flask import Flask, render_template, flash
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from flask_wtf import FlaskForm
from wtforms import TextField, StringField, BooleanField, SubmitField, validators, SelectField, HiddenField
from wtforms.validators import NumberRange, DataRequired
from wtforms_components import IntegerField
import json
import requests
import wtforms_json
from flask import request

from .snow import SnowForm
from .device import AddDeviceConfigurationForm, DeviceForm, AddDeviceForm
from .helpers.rest import get_url, get_rest_command
from .site import SearchSiteForm, AddSiteForm
from .router import RouterConfigForm

wtforms_json.init()
requests.packages.urllib3.disable_warnings()

# https://wtforms-components.readthedocs.io/en/latest/#selectfield


def create_app(configfile=None):
    app = Flask(__name__)
    print("config file = {}".format(configfile))
    AppConfig(app, configfile)  # Flask-Appconfig is not necessary, but
                                # highly recommend =)
                                # https://github.com/mbr/flask-appconfig
    Bootstrap(app)

    if not app.config.get('API_ENDPOINT'):
        app.config['API_ENDPOINT'] = 'https://virtserver.swaggerhub.com/steffenschumacher/netmanager/1.0.0/'
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = 'devkey'

    print("api_endpoint={}".format(app.config['API_ENDPOINT']))
    print('secret_key={}'.format(app.config['SECRET_KEY']))

    # helper functions for interacting ith the API endpoint
    get_info = lambda command: get_rest_command(app.config['API_ENDPOINT'], command)
    get_sites = lambda : get_info("sites")
    search_site = lambda site : get_info("sites/{}".format(site))
    get_site = lambda site : get_info("sites/{}?list_viable_devices=true".format(site))
    get_vlans = lambda site : get_info("sites/{}/vlans".format(site))
    get_devices = lambda site : get_info("sites/{}/devices".format(site))
    #post_devices = lambda site : get_info("devices".format(site))

    select_keys = lambda dictionary, x: {key : dictionary.get(key) for key in dictionary.keys() if key in x}

    @app.route('/snow', methods=('GET', 'POST'))
    def snow():
        form = SnowForm()
        form.validate_on_submit()
        if form.is_submitted():
            site_name = request.form.get('site_name')
            payload = select_keys(request.form, ['category', 'delete_if_exists', 'kbps'])
            r = requests.post(app.config['API_ENDPOINT'] + '_snow/{}'.format(site_name), data=payload, verify=False)
            if r.status_code == 200:
                flash("{} - {}".format(r.status_code, '{} created'.format(site_name)), 'info')
            else:
                flash("{} - {}".format(r.status_code, r.text), 'error')
            return render_template('snow.html', form=form)
        return render_template('snow.html', form=form)


    @app.route('/add-site', methods=('GET', 'POST'))
    def add_site():
        form = AddSiteForm()
        form.validate_on_submit()
        if form.is_submitted():
            site_name = request.form.get('site_name')
            payload = select_keys(request.form, ['users', 'ipphones'])
            print(payload)
            #headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}
            r = requests.post(app.config['API_ENDPOINT'] + 'sites/{}'.format(site_name), data=payload, verify=False)

            if r.status_code == 200:
                flash("{} - {}".format(r.status_code, '{} created'.format(site_name)), 'info')
                return render_template('site.html', data=json.loads(r.text))
            else:
                flash("{} - {}".format(r.status_code, r.text), 'error')
            return render_template('site-add.html', form=form)
        return render_template('site-add.html', form=form)



    @app.route('/device', methods=('GET', 'POST'))
    def device():
        form = DeviceForm()
        form.validate_on_submit()
        if form.is_submitted():
            return render_template('device.html', form=form)
        return render_template('device.html', form=form)


    @app.route('/site', methods=('GET', 'POST'))
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
                return render_template('device.html', form=add_device)

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
                r = requests.post(app.config['API_ENDPOINT'] + 'devices', data=submitted, verify=False)
                print('post_url responds with: ')
                print(r.text)
                if r.status_code == 500:
                    flash("{} - {}".format(r.status_code,r.text), 'info')
                # if r.status_code != 200:
                #    add_device = AddDeviceForm(request.values)
                #    return render_template('device.html', form=add_device)
                submitted['site'] = submitted.pop('site_name')
                if r.status_code == 200:
                    flash('{} was added added to {} - {}'.format(submitted['dev_cfg'], submitted['site'], submitted['df']), 'success')

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

                return render_template('site-search.html', form=form, vlans=vlans, devices=devices, data=data, add_device=add_device)
            return render_template('site-search.html', form=form)
        return render_template('site-search.html', form=form)

    @app.route('/', methods=('GET', 'POST'))
    def index():
        form = RouterConfigForm()
        form.validate_on_submit()  # to get error messages to the browser
        print("configuring%s+%s" % (form.router.data, form.switch.data) + " with SNOW ID: %s " % (form.snow.data) + " %s APs" % (form.aps.data))

        if form.is_submitted():
            url = app.config['API_ENDPOINT'] + "sites"
            r = requests.get(url)
            print(r.text)
            # a form that is able to show the information will need to be made
            return render_template('configuring.html', form=form)

        return render_template('index.html', form=form)

    @app.route('/sites', methods=('GET', 'POST'))
    def sites():
        data = get_sites()
        print(data)
        return render_template('sites.html', sites=data)

    return app


if __name__ == '__main__':
    create_app().run(debug=True)

