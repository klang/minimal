from flask import Flask, render_template, flash
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from flask_wtf import Form
from wtforms import TextField, StringField, BooleanField, SubmitField, validators, SelectField
from wtforms.validators import NumberRange
from wtforms_components import IntegerField

import requests
import json
from retrying import retry

# straight from the wtforms docs:
class TelephoneForm(Form):
    country_code = IntegerField('Country Code', [validators.required()])
    area_code = IntegerField('Area Code/Exchange', [validators.required()])
    number = StringField('Number')


# https://wtforms-components.readthedocs.io/en/latest/#selectfield

class RouterConfigForm(Form):
    router = SelectField('Router', description="router", choices=[('C4321', 'Cisco 4321')])
    switch = SelectField('Switch', description="switch", choices=[('3650X-12', '3650X-12P')])
    aps = SelectField('APs', choices=[(0,0), (1,1), (2,2), (3,3)], validators=[NumberRange(min=0, max=3)], coerce=int)
    riverbed = BooleanField('Riverbed', description='optional')
    snow = IntegerField('Snow', description="SNOW site id")
    region = SelectField('Region', choices=[('eu-west-1', 'Ireland'), ('eu-west-2', 'London'), ('eu-west-3', 'Paris'), ('eu-central-1', 'Frankfurt')])
    serial = TextField('Serial', description='Serial number for each device to be configured')
    submit_button = SubmitField('Submit Form')


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


def create_app(configfile=None):
    app = Flask(__name__)
    AppConfig(app, configfile)  # Flask-Appconfig is not necessary, but
                                # highly recommend =)
                                # https://github.com/mbr/flask-appconfig
    Bootstrap(app)
    # in a real app, these should be configured through Flask-Appconfig
    app.config['SECRET_KEY'] = 'devkey'

    @app.route('/', methods=('GET', 'POST'))
    def index():
        form = RouterConfigForm()
        form.validate_on_submit()  # to get error messages to the browser
        print("configuring%s+%s" % (form.router.data, form.switch.data) + " with SNOW ID: %s " % (form.snow.data) + " %s APs" % (form.aps.data))

        if form.is_submitted():
            url="https://virtserver.swaggerhub.com/steffenschumacher/netmanager/1.0.0/sites"
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
            data= json.loads(r.text)
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
        return render_template('devices.html', devices=data)

    return app


if __name__ == '__main__':
    create_app().run(debug=True)
