import asyncio
import logging
from saga_client.client import ClusterClient
from saga_client.config import HOSTS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    client = ClusterClient(hosts=HOSTS)
    group_id = 'example_group'

    # Create a group
    logger.info("Starting group creation...")
    create_success = await client.create_group(group_id)
    if create_success:
        logger.info(f"Group {group_id} successfully created on all hosts.")
    else:
        logger.error(f"Failed to create group {group_id} on all hosts.")

    # Delete a group
    logger.info("Starting group deletion...")
    undeleted_hosts = await client.delete_group(group_id)
    if not undeleted_hosts:
        logger.info(f"Group {group_id} successfully deleted from all hosts.")
    else:
        logger.error(f"Failed to delete group {group_id} from the following hosts: {undeleted_hosts}")


if __name__ == '__main__':
    asyncio.run(main())
