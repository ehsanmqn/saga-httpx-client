import os
import logging

logging.basicConfig(level=logging.INFO)


def get_hosts():
    hosts_str = os.getenv('HOSTS', '')
    hosts = [host.strip() for host in hosts_str.split(',') if host.strip()]

    if not hosts:
        logging.warning('HOSTS environment variable is not set or is empty. Using default values.')
        hosts = [
            'http://localhost:8000',
            'http://localhost:8001',
            'http://localhost:8002',
        ]

    for host in hosts:
        if not host.startswith('http://') and not host.startswith('https://'):
            logging.warning(f'URL {host} does not start with http:// or https://')

    return hosts


HOSTS = get_hosts()
