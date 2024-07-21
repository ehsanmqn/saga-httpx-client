import httpx
import logging
from typing import List
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .config import HOSTS
from .coordinator import SagaCoordinator
from .exceptions import RequestErrorException

logger = logging.getLogger(__name__)


class ClusterClient:
    def __init__(self, hosts: List[str] = HOSTS):
        self.hosts = hosts

    @retry(
        retry=retry_if_exception_type(RequestErrorException),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    async def create_group_on_host(self, client: httpx.AsyncClient, host: str, group_id: str) -> bool:
        url = f'{host}/v1/group/'
        try:
            response = await client.post(url, json={'groupId': group_id}, timeout=10)
            if response.status_code == 201:
                logger.info(f'Group {group_id} created on {host}')
                return True
            logger.error(f'Failed to create group on {host}: {response.status_code}')
            return False
        except httpx.RequestError as exc:
            logger.error(f'Request error occurred while creating group on {host}: {exc}')
            raise RequestErrorException(host, str(exc))

    @retry(
        retry=retry_if_exception_type(RequestErrorException),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    async def _delete_group_on_host(self, client: httpx.AsyncClient, host: str, group_id: str) -> bool:
        url = f'{host}/v1/group/'
        try:
            response = await client.request(method='DELETE', url=url, json={'groupId': group_id}, timeout=10)
            if response.status_code == 200:
                logger.info(f'Group {group_id} deleted from {host}')
                return True
            logger.error(f'Failed to delete group on {host}: {response.status_code}')
            return False
        except httpx.RequestError as exc:
            logger.error(f'Request error occurred while deleting group on {host}: {exc}')
            raise RequestErrorException(host, str(exc))

    @retry(
        retry=retry_if_exception_type(RequestErrorException),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    async def verify_group_on_host(self, client: httpx.AsyncClient, host: str, group_id: str) -> bool:
        url = f'{host}/v1/group/{group_id}/'
        try:
            response = await client.get(url, timeout=10)
            if response.status_code == 200:
                logger.info(f'Group {group_id} verified on {host}')
                return True
            elif response.status_code == 404:
                logger.warning(f'Group {group_id} not found on {host}')
                return False
            else:
                logger.error(f'Failed to verify group on {host}: {response.status_code}')
                return False
        except httpx.RequestError as exc:
            logger.error(f'Request error occurred while verifying group on {host}: {exc}')
            raise RequestErrorException(host, str(exc))

    async def rollback_creation(self, client: httpx.AsyncClient, group_id: str, success_hosts: List[str]) -> List[str]:
        logger.info('Rolling back creation on successful hosts...')
        undeleted_hosts = []
        for host in success_hosts:
            try:
                if not await self._delete_group_on_host(client, host, group_id):
                    logger.error(f'Failed to rollback creation on {host}')
                    undeleted_hosts.append(host)
                else:
                    if await self.verify_group_on_host(client, host, group_id):
                        logger.error(f'Group {group_id} still exists on {host} after rollback attempt')
                        undeleted_hosts.append(host)
            except RequestErrorException as e:
                logger.error(f'Error during rollback on {host}: {e}')
                undeleted_hosts.append(host)
        if len(undeleted_hosts) == 0:
            logger.info('Roll back performed successfully.')
        return undeleted_hosts

    async def create_group(self, group_id: str) -> bool:
        coordinator = SagaCoordinator(self)
        return await coordinator.execute(group_id)

    async def delete_group(self, group_id: str) -> List[str]:
        undeleted_hosts = self.hosts[:]
        async with httpx.AsyncClient() as client:
            for host in self.hosts:
                try:
                    if not await self._delete_group_on_host(client, host, group_id):
                        logger.warning(f'Deletion failed on host {host}')
                        continue
                    undeleted_hosts.remove(host)
                except Exception as e:
                    logger.error(f'Error during deletion on host {host}: {e}')
                    continue
        return undeleted_hosts