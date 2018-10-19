from flask import Flask, render_template, flash
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from flask_wtf import FlaskForm
from wtforms import TextField, StringField, BooleanField, SubmitField, validators, SelectField, HiddenField, FieldList, FormField
from wtforms.validators import NumberRange
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


class Device(FlaskForm):
    site_name = StringField('site_name', description="site name")
    dev_cfg = StringField('dev_cfg', description="viable device configuration")
    building = StringField('building', description="3 letter building name")
    df = StringField('df', description="3 letter distribution frame - I01 for IDF01, M01 for MDF01")
    serial = StringField('serial', description="Chassis serial number")
    stack_partner = StringField('stack_partner', description="use the assigned host as the primary device in a stack, this host should join")
    auto_connect = BooleanField('auto_connect', description="When true, connections to preexisting site devices will be automatically generated")
    wan_line = StringField('wan_line', description="for dmvpn/mpls roles, a SNOW wan name to retrieve wan details")
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
    site = StringField('site')
    submit_button = SubmitField('Find Site')


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


def get_site(site):
    data = []
    url = "https://virtserver.swaggerhub.com/steffenschumacher/netmanager/1.0.0/sites/{}".format(site)
    try:
        r = get_url(url)
        data = json.loads(r.text)
    except requests.exceptions.HTTPError as e:
        flash('{} - {} - has disappeared '.format(e.response.status_code, url), 'error')
    return data


def get_vlans(site):
    data = []
    url = "https://virtserver.swaggerhub.com/steffenschumacher/netmanager/1.0.0/sites/{}/vlans".format(site)
    try:
        r = get_url(url)
        data = json.loads(r.text)
    except requests.exceptions.HTTPError as e:
        flash('{} - {} - has disappeared '.format(e.response.status_code, url), 'error')
    return data


def create_app(configfile=None):
    app = Flask(__name__)
    AppConfig(app, configfile)  # Flask-Appconfig is not necessary, but
                                # highly recommend =)
                                # https://github.com/mbr/flask-appconfig
    Bootstrap(app)
    # in a real app, these should be configured through Flask-Appconfig
    app.config['SECRET_KEY'] = 'devkey'



    @app.route('/scratch', methods=('GET', 'POST'))
    def scratch():
        #if requests.method == 'POST':
        form = AddSiteForm()
        form.validate_on_submit()
        f2 = putSiteForm()
        if form.is_submitted():
            data = get_site(form.site_name.data)
            print(data)
            return render_template('scratch.html', form=form, form2=f2, sites=[data])
        return render_template('scratch.html', form=form, form2=f2)

    @app.route('/device', methods=('GET', 'POST'))
    def device():
        form = Device()
        form.validate_on_submit()
        if form.is_submitted():
            return render_template('device.html', form=form)
        return render_template('device.html', form=form)

    @app.route('/site', methods=('GET', 'POST'))
    def site():
        form = searchSiteForm()
        form.validate_on_submit()
        if form.is_submitted():
            print(request.form)
            submitted_device_configuration = None
            if 'submit_button' not in request.form and 'add_device_config' in request.form:
                print("add device configuration")
                submitted_device_configuration = request.form.to_dict(flat=True)
                submitted_device_configuration.pop('csrf_token', None)
                print("SUBMITTED CONFIG", submitted_device_configuration)
            data = get_site(form.site.data)
            print("\nSITE ", data)
            data['device_configurations'].append({'name': 'string', 'model': 'string', 'mbps': 0, 'roles': ['string1', 'string2', 'string3'], 'licenses': ['string1', 'string2', 'string3'], 'categories': [0,1,2,3]})
            data['device_configurations'].append({'name': 'string', 'model': 'string', 'mbps': 0, 'roles': ['string1', 'string2', 'string3'], 'licenses': ['string1', 'string2', 'string3'], 'categories': [0,1,2,3]})
            data['device_configurations'].append({'name': 'string', 'model': 'string', 'mbps': 0, 'roles': ['string1', 'string2', 'string3'], 'licenses': ['string1', 'string2', 'string3'], 'categories': [0,1,2,3]})
            if submitted_device_configuration:
                data['device_configurations'].append(submitted_device_configuration)
            print("\nEXTRA DEVICE CONFIGURATIONS ", [d for d in data['device_configurations']])
            vlans = get_vlans(form.site.data)
            vlans.append({'vlan': 1, 'kind': 'string', 'description': 'string'})
            vlans.append({'vlan': 2, 'kind': 'string', 'description': 'string'})
            vlans.append({'vlan': 3, 'kind': 'string', 'description': 'string'})
            print("\nEXTRA VLANS ", vlans)

            return render_template('site-search.html', form=form, vlans=vlans, data=data)
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

    @app.route('/advanced-sites', methods=('GET', 'POST'))
    def advanced_sites():
        url = "https://virtserver.swaggerhub.com/steffenschumacher/netmanager/1.0.0/sites"
        try:
            r = get_url(url)
            data = json.loads(r.text)
        except requests.exceptions.HTTPError as e:
            flash('{} - {} - has disappeared '.format(e.response.status_code, url), 'error')
            data = []
        print(data)
        if len(data) == 1:
            print("WARNING: adding a bit of fake data for site")
            data.append({'name': 'sample 1', 'networks': 'string', 'email_ips': 'string', 'sccm_ips': 'string', 'tp_subnets': 'string', 'vtp_domain': 'string', 'vtp_enc_key': 'string'})
            data.append({'name': 'sample 2', 'networks': 'string', 'email_ips': 'string', 'sccm_ips': 'string', 'tp_subnets': 'string', 'vtp_domain': 'string', 'vtp_enc_key': 'string'})
        vlans = {}
        for site in data:
            url = "https://virtserver.swaggerhub.com/steffenschumacher/netmanager/1.0.0/sites/{}/vlans".format(site['name'])
            try:
                r = get_url(url)
                subdata = json.loads(r.text)
                if len(subdata) == 1:
                    print("WARNING: adding a bit of fake data for vlans at site")
                    subdata.append({'vlan': 1, 'kind': 'string', 'description': 'string'})
                    subdata.append({'vlan': 2, 'kind': 'string', 'description': 'string'})
                    subdata.append({'vlan': 3, 'kind': 'string', 'description': 'string'})
            except requests.exceptions.HTTPError as e:
                subdata = []
            vlans[site['name']] = subdata

        return render_template('advanced-sites.html', sites=data, vlans=vlans)

    @app.route('/devices', methods=('GET', 'POST'))
    def devices():
        url = "https://virtserver.swaggerhub.com/steffenschumacher/netmanager/1.0.0/devices"
        try:
            r = get_url(url)
            data = json.loads(r.text)
        except requests.exceptions.HTTPError as e:
            flash('{} - {} - has disappeared '.format(e.response.status_code, url), 'error')
            data = []
        print(data)

        data.append({"name": "string", "ip": "string", "roles": "string", "dev_cfg": "string", "site": "string"})
        data.append({"name": "string", "ip": "string", "roles": "string", "dev_cfg": "string", "site": "string"})
        data.append({"name": "string", "ip": "string", "roles": "string", "dev_cfg": "string", "site": "string"})
        return render_template('devices.html', devices=data)

    return app


if __name__ == '__main__':
    create_app().run(debug=True)

