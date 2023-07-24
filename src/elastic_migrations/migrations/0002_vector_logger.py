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
        'index.lifecycle.rollover_alias': WEB_LOGS
    }

    policy = {
        'phases': {
            'hot': {
                'actions': {
                    'rollover': {
                        'max_age': '1d'
                    }
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

    client.ilm.put_lifecycle(name=WEB_LOGS, policy=policy)
    client.indices.create(index=f'{WEB_LOGS}-000001', mappings=mapping, aliases=aliases, settings=settings)


def reverse():
    indices = list(client.indices.get(index=f'{WEB_LOGS}-*').keys())
    for i in indices:
        client.indices.delete(index=i)
    client.ilm.delete_lifecycle(name=WEB_LOGS)


migration = Migration(
    depends_on='0001_initial',
    forwards=forwards,
    reverse=reverse
)
