from flask import Flask, render_template, flash, redirect
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from flask_wtf import FlaskForm
from wtforms import TextField, StringField, BooleanField, SubmitField, validators, SelectField, HiddenField, FieldList, FormField
from wtforms.validators import NumberRange, DataRequired
from wtforms_components import IntegerField

import requests
import json
from retrying import retry

import wtforms_json
from flask import request
wtforms_json.init()


# https://wtforms-components.readthedocs.io/en/latest/#selectfield

class RouterConfigForm(FlaskForm):
    router = SelectField('Router', description="router", choices=[('C4321', 'Cisco 4321')])
    switch = SelectField('Switch', description="switch", choices=[('3650X-12', '3650X-12P')])
    aps = SelectField('APs', choices=[(0,0), (1,1), (2,2), (3,3)], validators=[NumberRange(min=0, max=3)], coerce=int)
    riverbed = BooleanField('Riverbed', description='optional')
    snow = IntegerField('Snow', description="SNOW site id")
    region = SelectField('Region', choices=[('eu-west-1', 'Ireland'), ('eu-west-2', 'London'), ('eu-west-3', 'Paris'), ('eu-central-1', 'Frankfurt')])
    serial = TextField('Serial', description='Serial number for each device to be configured')
    submit_button = SubmitField('Submit Form')


# there must be a way to auto generate this stuff
class AddSiteForm(FlaskForm):
    site_name = StringField('site_name', description="Name of new site - must exist in SNOW, to extract the site category etc" )
    users = IntegerField('users', description="Number of expected users")
    ipphones = IntegerField('ipphones', description="Number physical IP Phones")
    submit_button = SubmitField('Submit Form')


class AddDeviceConfigurationForm(FlaskForm):
    name = StringField('name')
    model = StringField('model')
    mbps = IntegerField('mbps')
    roles = StringField('roles')
    licenses = StringField('licenses')
    categories = StringField('categories')

class putSiteForm(FlaskForm):
    name = StringField('name')
    networks = StringField('networks')
    email_ips = StringField('email_ips')
    sccm_ips = StringField('sccm_ips')
    tp_subnets = StringField('tp_subnets')
    vtp_domain = StringField('vtp_domain')
    vtp_enc_key = StringField('vtp_enc_key')
    #device_configurations = FieldList(FormField(DeviceConfigurationForm), min_entries=1)
#    device_configurations = HiddenField('device_configurations')
    #submit_button = SubmitField('Submit Form')

class searchSiteForm(FlaskForm):
    site_name = StringField('site_name')
    submit_search_site = SubmitField('Find Site')


def retry_if_HTTP404(exception):
    return isinstance(exception, requests.exceptions.HTTPError) and exception.response.status_code == 404


@retry(stop_max_attempt_number=5, wait_exponential_multiplier=100, retry_on_exception=retry_if_HTTP404)
def get_url(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
        return r
    except requests.exceptions.HTTPError as e:
        raise e


def get_rest_command(url, command):
    data = []
    url = "{url}/{command}".format(url = url.strip("/"), command = command)
    try:
        r = get_url(url)
        data = json.loads(r.text)
    except requests.exceptions.HTTPError as e:
        flash('{} - {} - has disappeared '.format(e.response.status_code, url), 'error')
    return data

get_info = lambda command: get_rest_command("https://virtserver.swaggerhub.com/steffenschumacher/netmanager/1.0.0/", command)
get_site = lambda site : get_info("sites/{}?list_viable_devices=true".format(site))
get_vlans = lambda site : get_info("sites/{}/vlans".format(site))
get_devices = lambda site : get_info("sites/{}/devices".format(site))

#post_devices = lambda site : get_info("devices".format(site))

class Device(FlaskForm):
    site_name = StringField('site_name', description="site name")
    dev_cfg = StringField('dev_cfg', description="viable device configuration")
    building = StringField('building', description="3 letter building name")
    df = StringField('df', description="3 letter distribution frame - I01 for IDF01, M01 for MDF01")
    serial = StringField('serial', description="Chassis serial number")
    stack_partner = StringField('stack_partner', description="use the assigned host as the primary device in a stack, this host should join")
    auto_connect = BooleanField('auto_connect', description="When true, connections to preexisting site devices will be automatically generated")
    wan_line = StringField('wan_line', description="for dmvpn/mpls roles, a SNOW wan name to retrieve wan details")
    submit_device = SubmitField('Add Device')


class AddDevice(FlaskForm):
    site_name = HiddenField('site_name')
    dev_cfg = SelectField('dev_cfg', validators=[DataRequired()], id='dev_cfg', description="DeviceConfigurations")
    submit_add_device = SubmitField('Add Device')

def create_app(configfile=None):
    app = Flask(__name__)
    AppConfig(app, configfile)  # Flask-Appconfig is not necessary, but
                                # highly recommend =)
                                # https://github.com/mbr/flask-appconfig
    Bootstrap(app)
    # in a real app, these should be configured through Flask-Appconfig
    app.config['SECRET_KEY'] = 'devkey'


    @app.route('/device', methods=('GET', 'POST'))
    def device():
        form = Device()
        form.validate_on_submit()
        if form.is_submitted():
            return render_template('device.html', form=form)
        return render_template('device.html', form=form)


    @app.route('/site', methods=('GET', 'POST'))
    def site():
        form = searchSiteForm(request.values)
        form.validate_on_submit()

        print(request.method)
        print(request.form)

        if form.is_submitted():
            if 'submit_add_device' in request.form:
                print("Got a submit event on the AddDevice form")
                submitted = request.form.to_dict(flat=True)
                submitted.pop('csrf_token', None)
                print("SUBMITTED DEVICE", submitted)
                add_device = Device(site_name = submitted['site_name'], dev_cfg = submitted['dev_cfg'])
                add_device.site_name.render_kw = {'readonly': True}
                add_device.dev_cfg.render_kw = {'readonly': True}
                add_device.dev_cfg.description = '' # just to remove the description
                return render_template('device.html', form=add_device)

            if 'submit_device' in request.form:
                print("Got a submit event on the Device form")
                submitted = request.form.to_dict(flat=True)
                submitted.pop('csrf_token', None)
                submitted['site'] = submitted.pop('site_name')
                submitted['auto_connect'] = submitted.get('auto_connect', 'false').replace('y', 'true')
                submitted.pop('submit_device', None)
                # TODO: actually insert 'submitted' into a database somewhere
                # i.e. call the rest endpoint
                print("CALL post_url with {}".format(submitted))
                #CALL post_url with {'dev_cfg': 'string3', 'building': 'HB2', 'df': 'M01', 'serial': '15135424', 'stack_partner': '123', 'wan_line': 'adsga', 'site': 'DKAARHED42', 'auto_connect': 'false'}
                r = requests.post('https://virtserver.swaggerhub.com/steffenschumacher/netmanager/1.0.0/devices', data=submitted)
                print('post_url responds with: ')
                print(r.text)
                flash(r.text, 'info')
                flash('{} was added added to {} - {}-{}'.format(submitted['dev_cfg'], submitted['site'], submitted['building'], submitted['df']), 'success')

            # DATA FOR THE "SHOW SITE INFORMATION" Page
            #
            data = get_site(form.site_name.data)
            vlans = get_vlans(form.site_name.data)
            devices = get_devices(form.site_name.data)

            # TODO: remove added fake data
            data['device_configurations'].append({'name': 'string1', 'model': 'string', 'mbps': 0, 'roles': ['string1', 'string2', 'string3'], 'licenses': ['string1', 'string2', 'string3'], 'categories': [0,1,2,3]})
            data['device_configurations'].append({'name': 'string2', 'model': 'string', 'mbps': 0, 'roles': ['string1', 'string2', 'string3'], 'licenses': ['string1', 'string2', 'string3'], 'categories': [0,1,2,3]})
            data['device_configurations'].append({'name': 'string3', 'model': 'string', 'mbps': 0, 'roles': ['string1', 'string2', 'string3'], 'licenses': ['string1', 'string2', 'string3'], 'categories': [0,1,2,3]})
            vlans.append({'vlan': 1, 'kind': 'stringA', 'description': 'string'})
            vlans.append({'vlan': 2, 'kind': 'stringB', 'description': 'string'})
            vlans.append({'vlan': 3, 'kind': 'stringC', 'description': 'string'})
            devices.append({'name': 'string4', 'ip': 'string', 'roles': 'string', 'dev_cfg': 'string', 'site': 'string', 'serial': 'string'})
            devices.append({'name': 'string5', 'ip': 'string', 'roles': 'string', 'dev_cfg': 'string', 'site': 'string', 'serial': 'string'})
            devices.append({'name': 'string6', 'ip': 'string', 'roles': 'string', 'dev_cfg': 'string', 'site': 'string', 'serial': 'string'})
            # ----------- fake data ends here

            add_device = AddDevice(request.values)
            choices = [(device['name'], device['name']) for device in data['device_configurations']]
            add_device.dev_cfg.choices = choices

            return render_template('site-search.html', form=form, vlans=vlans, devices=devices, data=data, add_device=add_device)
        return render_template('site-search.html', form=form)


    @app.route('/', methods=('GET', 'POST'))
    def index():
        form = RouterConfigForm()
        form.validate_on_submit()  # to get error messages to the browser
        print("configuring%s+%s" % (form.router.data, form.switch.data) + " with SNOW ID: %s " % (form.snow.data) + " %s APs" % (form.aps.data))

        if form.is_submitted():
            url = "https://virtserver.swaggerhub.com/steffenschumacher/netmanager/1.0.0/sites"
            r = requests.get(url)
            print(r.text)
            # a form that is able to show the information will need to be made
            return render_template('configuring.html', form=form)

        return render_template('index.html', form=form)

    @app.route('/sites', methods=('GET', 'POST'))
    def sites():
        url = "https://virtserver.swaggerhub.com/steffenschumacher/netmanager/1.0.0/sites"
        try:
            r = get_url(url)
            data = json.loads(r.text)
        except requests.exceptions.HTTPError as e:
            flash('{} - {} - has disappeared '.format(e.response.status_code, url), 'error')
            data = []
        print(data)
        return render_template('sites.html', sites=data)



    return app


if __name__ == '__main__':
    create_app().run(debug=True)

