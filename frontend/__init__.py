from flask import Flask, render_template, flash
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from flask_wtf import Form
from wtforms import TextField, StringField, BooleanField, SubmitField, validators, SelectField
from wtforms.validators import NumberRange
from wtforms_components import IntegerField


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
            import requests
            url="https://virtserver.swaggerhub.com/steffenschumacher/netmanager/1.0.0/sites"
            r = requests.get(url)
            print(r.text)
            # a form that is able to show the information will need to be made
            return render_template('configuring.html', form=form)

        return render_template('index.html', form=form)

    @app.route('/sites', methods=('GET', 'POST'))
    def sites():
        import requests
        import json
        url="https://virtserver.swaggerhub.com/steffenschumacher/netmanager/1.0.0/sites"
        r = requests.get(url)
        sites = json.loads(r.text)
        print(r.text)
        return render_template('sites.html', sites=sites)

    return app


if __name__ == '__main__':
    create_app().run(debug=True)
