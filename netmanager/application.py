# -*- coding: utf-8 -*-
from flask import Flask, request, url_for
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from flask_nav.renderers import Renderer
from flask_bootstrap import Bootstrap
from dominate import tags


nav = Nav()


@nav.renderer()
class BootstrapDashboardRenderer(Renderer):
    def visit_Navbar(self, node):
        sub = []
        for item in node.items:
            sub.append(self.visit(item))

        return tags.nav(
            tags.div(
                tags.ul(sub,
                        _class="nav flex-column"),
                _class='sidebar-sticky'),
            _class='col-md-2 d-none d-md-block bg-light sidebar')

    def visit_FeatherView(self, node):
        link_class = ['nav-link']
        text_content = [tags.span({'data-feather': node.feather}), node.text]

        if node.active:
            link_class.append('active')
            text_content.append(tags.span("(current)", _class="sr-only"))

        return tags.li(
            tags.a(
                text_content,
                href=node.get_url(),
                title=node.text,
                _class=" ".join(link_class)),
            _class="nav-item"
        )


class FeatherView(View):
    # https://feathericons.com/
    def __init__(self, text, feather, endpoint, **kwargs):
        View.__init__(self, text, endpoint, **kwargs)
        self.feather = feather

    @property
    def active(self):
        if not request.endpoint == self.endpoint:
            return False

        # add view_args to be able to build the correct URL for page/N URL's
        rule_build_args = self.url_for_kwargs.copy()
        if len(request.url_rule.arguments) > 0:
            rule_build_args.update(request.view_args)

        _, url = request.url_rule.build(rule_build_args,
                                        append_unknown=not self.ignore_query)

        if self.ignore_query:
            return url == request.path

        return url == request.full_path


nav.register_element('left', Navbar('',
                                    FeatherView('Sites', 'chevron-right', 'pages_app.sites'),
                                    FeatherView('Add site in SNOW', 'chevron-right', 'pages_app.snow'),
                                    FeatherView('Add Site in NetCMDB', 'chevron-right', 'pages_app.add_site'),
                                    FeatherView('Add Devices to site', 'chevron-right', 'pages_app.site'),
                                    #FeatherView('Cost', 'dollar-sign', 'pages_app.cost'),
                                    #FeatherView('About', 'info', 'pages_app.about'),
                                    ))


def url_for_other_page(page):
    all_args = dict()
    all_args.update(request.args.copy())
    all_args.update(request.view_args.copy())
    all_args['page'] = page
    return url_for(request.endpoint, **all_args)


def url_for_with_args(page, **kwargs):
    all_args = dict()
    all_args.update(request.args.copy())
    all_args.update(request.view_args.copy())
    all_args.update(**kwargs)
    return url_for(request.endpoint, **all_args)

# application factory, see: http://flask.pocoo.org/docs/patterns/appfactories/
def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)
    Bootstrap(app)
    # import blueprints
    from pages.views import pages_app
    # register blueprints
    app.register_blueprint(pages_app)

    nav.init_app(app)

    app.jinja_env.globals['url_for_other_page'] = url_for_other_page
    app.jinja_env.globals['url_for_with_args'] = url_for_with_args

    return app
