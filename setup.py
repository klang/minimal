from setuptools import setup, find_packages
desc = "NetManager webservices"

setup(
    name='netmanager-web',
    version="0.0.1",
    author="Karsten Lang Pedersen",
    author_email="karsten@cloudpartners.com",
    description=desc,
    long_description=desc,
    long_description_content_type="text/markdown",
    url="https://vestas.visualstudio.com/DefaultCollection/IT-50926%20Network%20Automation/_git/netmanager-web",
    packages=find_packages(),
    # scripts=["netmanager-web-flask.py"],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    include_package_data=True,
    zip__safe=False,
    install_requires=[
        'Flask', 'flask-nav', 'flask_bootstrap', 'pytz', 'flask_wtf', 'wtforms_components', 'requests', 'retrying',
        'wtforms_json'
    ],
    setup_requires=[

    ],
    tests_require=[

    ],
)