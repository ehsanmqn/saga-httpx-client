import pytest
import httpx
import tenacity
from unittest import mock
from saga_client.client import ClusterClient
from httpx import Response, RequestError, TimeoutException
from saga_client.config import HOSTS


@pytest.fixture
def mock_async_client():
    return mock.AsyncMock(spec=httpx.AsyncClient)


@pytest.mark.asyncio
async def test_create_group_on_host_success(mock_async_client):
    client = ClusterClient()

    mock_response = mock.Mock(spec=Response)
    mock_response.status_code = 201

    with mock.patch.object(mock_async_client, 'post', return_value=mock_response):
        result = await client.create_group_on_host(mock_async_client, HOSTS[0], 'test_group')
        assert result is True


@pytest.mark.asyncio
async def test_create_group_on_host_400_status_code(mock_async_client):
    client = ClusterClient()

    mock_response = mock.Mock(spec=Response)
    mock_response.status_code = 400

    with mock.patch.object(mock_async_client, 'post', return_value=mock_response):
        result = await client.create_group_on_host(mock_async_client, HOSTS[0], 'test_group')
        assert result is False


@pytest.mark.asyncio
async def test_create_group_on_host_500_status_code(mock_async_client):
    client = ClusterClient()

    mock_response = mock.Mock(spec=Response)
    mock_response.status_code = 500

    with mock.patch.object(mock_async_client, 'post', return_value=mock_response):
        result = await client.create_group_on_host(mock_async_client, HOSTS[0], 'test_group')
        assert result is False


@pytest.mark.asyncio
async def test_create_group_on_host_timeout(mock_async_client):
    client = ClusterClient()

    with mock.patch.object(mock_async_client, 'post', side_effect=TimeoutException('Request timed out')):
        with pytest.raises(tenacity.RetryError):
            await client.create_group_on_host(mock_async_client, HOSTS[0], 'test_group')


@pytest.mark.asyncio
async def test_create_group_on_host_request_error(mock_async_client):
    client = ClusterClient()

    with mock.patch.object(mock_async_client, 'post', side_effect=RequestError('Request failed')):
        with pytest.raises(tenacity.RetryError):
            await client.create_group_on_host(mock_async_client, HOSTS[0], 'test_group')


@pytest.mark.asyncio
async def test_delete_group_on_host_success(mock_async_client):
    client = ClusterClient()

    mock_response = mock.Mock(spec=Response)
    mock_response.status_code = 200

    with mock.patch.object(mock_async_client, 'request', return_value=mock_response):
        result = await client._delete_group_on_host(mock_async_client, HOSTS[0], 'test_group')
        assert result is True


@pytest.mark.asyncio
async def test_delete_group_on_host_400_status_code(mock_async_client):
    client = ClusterClient()

    mock_response = mock.Mock(spec=Response)
    mock_response.status_code = 400

    with mock.patch.object(mock_async_client, 'request', return_value=mock_response):
        result = await client._delete_group_on_host(mock_async_client, HOSTS[0], 'test_group')
        assert result is False


@pytest.mark.asyncio
async def test_delete_group_on_host_500_status_code(mock_async_client):
    client = ClusterClient()

    mock_response = mock.Mock(spec=Response)
    mock_response.status_code = 500

    with mock.patch.object(mock_async_client, 'request', return_value=mock_response):
        result = await client._delete_group_on_host(mock_async_client, HOSTS[0], 'test_group')
        assert result is False


@pytest.mark.asyncio
async def test_delete_group_on_host_timeout(mock_async_client):
    client = ClusterClient()

    with mock.patch.object(mock_async_client, 'request', side_effect=TimeoutException('Request timed out')):
        with pytest.raises(tenacity.RetryError):
            await client._delete_group_on_host(mock_async_client, HOSTS[0], 'test_group')


@pytest.mark.asyncio
async def test_delete_group_on_host_request_error(mock_async_client):
    client = ClusterClient()

    with mock.patch.object(mock_async_client, 'request', side_effect=RequestError('Request failed')):
        with pytest.raises(tenacity.RetryError):
            await client._delete_group_on_host(mock_async_client, HOSTS[0], 'test_group')


@pytest.mark.asyncio
async def test_verify_group_on_host_success(mock_async_client):
    client = ClusterClient()

    mock_response = mock.Mock(spec=Response)
    mock_response.status_code = 200

    with mock.patch.object(mock_async_client, 'get', return_value=mock_response):
        result = await client.verify_group_on_host(mock_async_client, HOSTS[0], 'test_group')
        assert result is True


@pytest.mark.asyncio
async def test_verify_group_on_host_not_found(mock_async_client):
    client = ClusterClient()

    mock_response = mock.Mock(spec=Response)
    mock_response.status_code = 404

    with mock.patch.object(mock_async_client, 'get', return_value=mock_response):
        result = await client.verify_group_on_host(mock_async_client, HOSTS[0], 'test_group')
        assert result is False


@pytest.mark.asyncio
async def test_verify_group_on_host_request_error(mock_async_client):
    client = ClusterClient()

    with mock.patch.object(mock_async_client, 'get', side_effect=RequestError('Request failed')):
        with pytest.raises(tenacity.RetryError):
            await client.verify_group_on_host(mock_async_client, HOSTS[0], 'test_group')


@pytest.mark.asyncio
async def test_rollback_creation_success(mock_async_client):
    client = ClusterClient(hosts=HOSTS)

    with mock.patch.object(client, '_delete_group_on_host', return_value=True), \
            mock.patch.object(client, 'verify_group_on_host', return_value=False):
        undeleted_hosts = await client.rollback_creation(mock_async_client, 'test_group', HOSTS)
        assert undeleted_hosts == []


@pytest.mark.asyncio
async def test_rollback_creation_failure(mock_async_client):
    client = ClusterClient(hosts=HOSTS)

    with mock.patch.object(client, '_delete_group_on_host', return_value=True), \
            mock.patch.object(client, 'verify_group_on_host', return_value=True):
        undeleted_hosts = await client.rollback_creation(mock_async_client, 'test_group', HOSTS)
        assert undeleted_hosts == HOSTS


@pytest.mark.asyncio
async def test_create_group_success(mock_async_client):
    client = ClusterClient(hosts=HOSTS)

    with mock.patch.object(client, 'create_group_on_host', return_value=True), \
            mock.patch.object(client, 'verify_group_on_host', return_value=True):
        result = await client.create_group('test_group')
        assert result is True


@pytest.mark.asyncio
async def test_create_group_rollback(mock_async_client):
    client = ClusterClient(hosts=HOSTS)

    with mock.patch.object(client, 'create_group_on_host', side_effect=[True, True, False]), \
            mock.patch.object(client, 'verify_group_on_host', return_value=True), \
            mock.patch.object(client, 'rollback_creation', return_value=HOSTS[:2]):
        result = await client.create_group('test_group')
        assert result is False


@pytest.mark.asyncio
async def test_delete_group_success(mock_async_client):
    client = ClusterClient(hosts=HOSTS)

    with mock.patch.object(client, '_delete_group_on_host', return_value=True):
        result = await client.delete_group('test_group')
        assert result == []


@pytest.mark.asyncio
async def test_delete_group_failure(mock_async_client):
    client = ClusterClient(hosts=HOSTS)

    with mock.patch.object(client, '_delete_group_on_host', side_effect=[True, False, True]):
        result = await client.delete_group('test_group')
        assert result == [HOSTS[1]]


@pytest.mark.asyncio
async def test_create_group_on_host_empty_group_id(mock_async_client):
    client = ClusterClient()

    mock_response = mock.Mock(spec=Response)
    mock_response.status_code = 400

    with mock.patch.object(mock_async_client, 'post', return_value=mock_response):
        result = await client.create_group_on_host(mock_async_client, HOSTS[0], '')
        assert result is False


@pytest.mark.asyncio
async def test_create_group_on_host_unexpected_exception(mock_async_client):
    client = ClusterClient()

    class UnexpectedException(Exception):
        pass

    with mock.patch.object(mock_async_client, 'post', side_effect=UnexpectedException('Unexpected error')):
        with pytest.raises(UnexpectedException):
            await client.create_group_on_host(mock_async_client, HOSTS[0], 'test_group')


@pytest.mark.asyncio
async def test_delete_group_on_host_unexpected_exception(mock_async_client):
    client = ClusterClient()

    class UnexpectedException(Exception):
        pass

    with mock.patch.object(mock_async_client, 'request', side_effect=UnexpectedException('Unexpected error')):
        with pytest.raises(UnexpectedException):
            await client._delete_group_on_host(mock_async_client, HOSTS[0], 'test_group')


@pytest.mark.asyncio
async def test_verify_group_on_host_unexpected_exception(mock_async_client):
    client = ClusterClient()

    class UnexpectedException(Exception):
        pass

    with mock.patch.object(mock_async_client, 'get', side_effect=UnexpectedException('Unexpected error')):
        with pytest.raises(UnexpectedException):
            await client.verify_group_on_host(mock_async_client, HOSTS[0], 'test_group')
