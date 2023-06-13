from setuptools import setup

setup(
    name='app-utils',
    version='0.1.0',
    packages=['elastic_migrations', 'web_sockets'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'web-sockets = web_sockets.scripts:cli',
            'elastic-migrations = elastic_migrations.scripts:cli'
        ]
    }
)
