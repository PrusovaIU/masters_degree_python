from auth_service.app.schemas import token_data
from auth_service.app.consts.token_type import TokenType
from datetime import timedelta, datetime, timezone
import pytest


SUB = "test_sub"
EXP_DELTA = timedelta(seconds=10)
EXP = int(
    (datetime.now(timezone.utc) - token_data.TokenData._UNIX_EPOCH)
    .total_seconds()
)
ROLE = "test_role"
PAYLOAD = {"test": "test"}


EXP_PARAMS = [
    pytest.param(EXP, id="int"),
    pytest.param(EXP_DELTA, id="timedelta")
]

class TestTokenData:
    @pytest.mark.parametrize("exp", EXP_PARAMS)
    def test_new_access_token(self, exp: timedelta | int):
        """
        Тест создания AccessTokenData методом TokenData.new.
        """
        td = token_data.TokenData.new(
            SUB,
            exp,
            TokenType.access,
            role=ROLE,
            payload=PAYLOAD
        )
        assert isinstance(td, token_data.AccessTokenData)
        assert td.sub == SUB
        assert isinstance(td.exp, datetime)
        assert isinstance(td.iat, datetime)
        assert td.role == ROLE
        assert td.payload == PAYLOAD
        assert td.token_type == TokenType.access

    @pytest.mark.parametrize("exp", EXP_PARAMS)
    def test_new_refresh_token(self, exp: timedelta | int):
        """
        Тест создания RefreshTokenData методом TokenData.new.
        """
        td = token_data.TokenData.new(
            SUB,
            exp,
            TokenType.refresh
        )
        assert isinstance(td, token_data.RefreshTokenData)
        assert td.sub == SUB
        assert isinstance(td.exp, datetime)
        assert isinstance(td.iat, datetime)
        assert td.token_type == TokenType.refresh
