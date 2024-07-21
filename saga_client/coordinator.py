import httpx
import logging

from .exceptions import GroupOperationException

logger = logging.getLogger(__name__)


class SagaCoordinator:
    def __init__(self, cluster_client):
        self.cluster_client = cluster_client

    async def execute(self, group_id: str) -> bool:
        """
        Execute the group creation process across multiple hosts.

        This method attempts to create a group with the specified group ID on all hosts in the cluster. It first tries to create
        the group on each host. If creation succeeds on a host, the host is added to the list of successful hosts. After all creation
        attempts, it verifies the existence of the group on each successful host. If any verification fails, or if any creation attempt
        fails, the method triggers a rollback process on all successfully created hosts.

        :param group_id: The identifier of the group to be created.
        :return: `True` if the group creation and verification are successful on all hosts;
                 `False` if any operation fails and rollback is required.
        """

        success_hosts = []

        async with httpx.AsyncClient() as client:
            try:
                for host in self.cluster_client.hosts:
                    if await self.cluster_client.create_group_on_host(client, host, group_id):
                        success_hosts.append(host)
                    else:
                        raise GroupOperationException(f'Failed to create group on {host}, initiating rollback.')

                for host in success_hosts:
                    if not await self.cluster_client.verify_group_on_host(client, host, group_id):
                        raise GroupOperationException(f'Failed to verify group on {host}, initiating rollback.')

                return True

            except GroupOperationException as e:
                logger.error(f'Error during group creation. Detail: {e}')

                if success_hosts:
                    undeleted_hosts = await self.cluster_client.rollback_creation(client, group_id, success_hosts)
                    if undeleted_hosts:
                        logger.error(f'Rollback failed on the following hosts: {undeleted_hosts}')

                return False
