from elastic_migrations.base import Migration
from app_core.elastic import client

WEB_LOGS = 'web_logs'


def forwards():
    mapping = {
        'properties': {
            'agent': {
                'type': 'text'
            },
            'http_method': {
                'type': 'text'
            },
            'ip': {
                'type': 'ip'
            },
            'message': {
                'type': 'text'
            },
            'path': {
                'type': 'text'
            },
            'process': {
                'type': 'keyword'
            },
            'severity': {
                'type': 'keyword'
            },
            'status_code': {
                'type': 'short'
            },
            'timestamp': {
                'type': 'date'
            }
        }
    }

    aliases = {
        WEB_LOGS: {
            'is_write_index': True
        }
    }
    settings = {
        'index.lifecycle.name': WEB_LOGS,
        'index.lifecycle.rollover_alias': WEB_LOGS,
        'index.number_of_replicas': 0
    }

    policy = {
        'phases': {
            'hot': {
                'min_age': '0ms',
                'actions': {
                    'rollover': {
                        'max_age': '1d'
                    }
                }
            },
            'cold': {
                'min_age': '1d',
                'actions': {
                    'readonly': {}
                }
            },
            'delete': {
                'min_age': '14d',
                'actions': {
                    'delete': {}
                }
            }
        }
    }

    client.indices.put_template(mappings=mapping, settings=settings, index_patterns=f'{WEB_LOGS}-*',
                                name=WEB_LOGS)
    client.ilm.put_lifecycle(name=WEB_LOGS, policy=policy)
    client.indices.create(index=f'{WEB_LOGS}-000001', aliases=aliases)


def reverse():
    indices = list(client.indices.get(index=f'{WEB_LOGS}-*').keys())
    for i in indices:
        client.indices.delete(index=i)
    client.indices.delete_template(name=WEB_LOGS)
    client.ilm.delete_lifecycle(name=WEB_LOGS)


migration = Migration(
    depends_on='0001_initial',
    forwards=forwards,
    reverse=reverse
)
