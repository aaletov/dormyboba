from unittest.mock import Mock, patch, AsyncMock
import pytest
import dormyboba_api.v1api_pb2 as apiv1

@pytest.fixture
def message_default():
    return Mock(
        spec=["peer_id", "from_id", "answer"],
        peer_id=123456,
        from_id=123456,
        answer=AsyncMock(),
    )

@pytest.fixture
def state_dispenser_default():
    return Mock(
        spec=["set", "get", "delete"],
        set=AsyncMock(),
        get=AsyncMock(),
        delete=AsyncMock(),
    )

@pytest.fixture
def ctx_storage_default():
    return Mock(
        spec=["set", "get"],
        set=Mock(),
        get=Mock(),
    )

@pytest.fixture
def stub_getUserById_role_default():
    stub = Mock()
    stub.GetUserById = AsyncMock()
    stub.GetUserById.return_value = apiv1.GetUserByIdResponse(
        user=apiv1.DormybobaUser(
            role=apiv1.DormybobaRole(
                role_name="admin",
            ),
        ),
    )
    return stub

@pytest.fixture
def stub_getUserById_role_council_member():
    stub = Mock()
    stub.GetUserById = AsyncMock()
    stub.GetUserById.return_value = apiv1.GetUserByIdResponse(
        user=apiv1.DormybobaUser(
            role=apiv1.DormybobaRole(
                role_name="council_member",
            ),
        ),
    )
    return stub

@pytest.fixture
def stub_getUserById_id_default():
    stub = Mock()
    stub.GetUserById = AsyncMock()
    stub.GetUserById.return_value = apiv1.GetUserByIdResponse(
        user=apiv1.DormybobaUser(
            user_id=123456,
        ),
    )
    return stub
