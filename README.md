# ClusterClient

The ClusterClient module offers asynchronous methods for managing groups across a cluster of hosts, utilizing the Saga design pattern to ensure reliable operations. It supports creating, verifying, and deleting groups on multiple hosts, incorporating advanced failure handling through retries and rollbacks. By employing the Saga pattern, the module guarantees consistency and fault tolerance across distributed transactions, managing failures gracefully and ensuring that operations are either completed successfully or appropriately rolled back.

## Features

- **Group Creation:** Create a group on multiple hosts with retry logic.
- **Group Verification:** Verify the existence of a group on a specific host.
- **Group Deletion:** Delete a group from all hosts with rollback capabilities.
- **Retry Mechanism:** Automatically retries operations in case of request errors using the `tenacity` library.
- **Saga Coordinator:** Manages distributed transactions according to the Saga design pattern guidelines.

## Requirements

- Python 3.7+
- `httpx` for asynchronous HTTP requests
- `tenacity` for retrying failed operations
- `logging` for logging messages

## Installation

You can install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

## Usage

### Initialization

Create an instance of `ClusterClient` with a list of host URLs:

```python
from cluster_client import ClusterClient

client = ClusterClient(hosts=["http://host1", "http://host2"])
```

### Methods

#### create_group

Creates a group using a saga coordinator to manage the process.

```python
await client.create_group(group_id)
```

- `group_id`: The ID of the group to be created.
- **Returns:** `True` if the process completes successfully; `False` otherwise.

#### delete_group

Deletes a group from all cluster nodes.

```python
await client.delete_group(group_id)
```

- `group_id`: The ID of the group to delete.
- **Returns:** A list of hosts where the deletion failed.

## Utilizing the Saga Design Pattern

The `SagaCoordinator` class implements the Saga design pattern for managing distributed transactions, ensuring consistency across multiple hosts during group operations. The Saga pattern involves breaking down a complex operation into a series of smaller, isolated transactions that are either completed successfully or compensated if they fail.

### How It Works

1. **Initiate Transactions:**
   - The `SagaCoordinator` class starts by attempting to create a group on all specified hosts.
   - Successful creation on each host is tracked in the `success_hosts` list.

2. **Verify Transactions:**
   - After all creation attempts, the coordinator verifies if the group was successfully created on each host.
   - If any verification fails, a rollback is triggered.

3. **Rollback:**
   - If any operation fails during creation or verification, the `rollback_creation` method is invoked.
   - This method attempts to delete the group from all hosts where it was successfully created and checks if the rollback was successful.
   - Any hosts where the rollback fails are reported.

### Example Usage

```python
import asyncio

from cluster_client import ClusterClient

async def main():
    client = ClusterClient(hosts=["http://host1", "http://host2"])
    success = await client.create_group("my-group-id")

    if success:
        print("Group created successfully.")
    else:
        print("Group creation failed.")

# Run the main function
asyncio.run(main())
```

## Error Handling

- **RequestErrorException**: Raised for request errors during group operations.
- **GroupOperationException**: Raised during the group creation or verification process, triggering rollback if necessary.

## Logging

Logging is configured to provide information about the success and failure of operations. Ensure that the logging configuration is set up in your application to capture these logs.

## Configuration

The `HOSTS` list can be configured in the `config` module to specify the cluster of hosts.