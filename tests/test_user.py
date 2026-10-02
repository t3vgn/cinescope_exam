from models.base_models import UserData
from models.base_models import RegisterUserResponse
import logging
import pytest
from pydantic import ValidationError
from constants.roles import Roles

logger = logging.getLogger(__name__)
class UserDataModel:

    def test_create_user(self, super_admin, creation_user_data):
        response = super_admin.api.user_api.create_user(creation_user_data)
        created_user = RegisterUserResponse(**response.json())

        assert created_user.email == creation_user_data.email
        assert created_user.fullName == creation_user_data.fullName
        assert created_user.roles == creation_user_data.roles
        assert created_user.verified is True

    def test_get_user_by_locator(self, super_admin, creation_user_data):
        created = RegisterUserResponse.model_validate(super_admin.api.user_api.create_user(creation_user_data).json())
        by_id = RegisterUserResponse.model_validate(super_admin.api.user_api.get_user(created.id).json())
        by_email = RegisterUserResponse.model_validate(super_admin.api.user_api.get_user(creation_user_data.email).json())


        assert by_id == by_email, "Содержание ответов должно быть идентичным"
        assert by_id.id, "ID должен быть не пустым"
        assert by_email.email == creation_user_data.email
        assert by_id.fullName == creation_user_data.fullName
        assert by_id.roles == creation_user_data.roles
        assert by_id.verified is True

    def test_get_user_by_id_common_user(self, common_user):
        common_user.api.user_api.get_user(common_user.email, expected_status=403)


    def test_create_user_model(self, creation_user_data):
        user:UserData = creation_user_data

        logger.info(f"✅ Модель создана: {user}")
        logger.info(f"📦 Поля: {user.model_dump()}")
        logger.info(f"📦 JSON: {user.model_dump_json(indent=2)}")

        assert user.email == creation_user_data.email
        assert user.fullName == creation_user_data.fullName
        assert user.roles == creation_user_data.roles
        assert user.verified is True
        assert user.banned is False

    def test_user_model_rejects_invalid_email(self):
        with pytest.raises(ValidationError) as exc_info:
            UserData(
                email="не-почта",
                fullName="Иван",
                password="12345678",
                passwordRepeat="12345678",
                roles=[Roles.USER],
            )

        errors = exc_info.value.errors()
        assert any(err["loc"] == ("email",) for err in errors), \
            f"Ожидали ошибку на email, получили: {errors}"