# -*- coding: utf-8 -*-
import os
import subprocess


class DictQuery(dict):
    def get(self, path, default = None):
        keys = path.split("/")
        val = None

        for key in keys:
            if val:
                if isinstance(val, list):
                    val = [ v.get(key, default) if v else None for v in val]
                else:
                    val = val.get(key, default)
            else:
                val = dict.get(self, key, default)

            if not val:
                break;

        return val


def examine_environment(app, env_name):
    application_name = 'netmanager'

    #app.config['API_ENDPOINT'] = DictQuery(response).get('DomainStatus/Endpoint')

    app.config['ADE_PROJECT_NAME'] = application_name
    app.config['ADE_ENVIRONMENT_NAME'] = env_name
