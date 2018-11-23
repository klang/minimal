#!/usr/bin/env python
# -*- coding: utf-8 -*-
from application import create_app
from util import examine_environment

app = create_app('settings')
examine_environment(app=app, env_name=app.config['ADE_ENVIRONMENT_NAME'])
app.run(port=5555)
