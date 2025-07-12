# import pytest
# from application.exceptions import NotEnoughUpdateInfoException, NotCorrectedProductType
# from application.usecases import CreateBaseOrderCommand, UpdateOrderCommand
# from bootstrap.constants import ProductType
# from pytest import raises
#
# from bootstrap.constants import Callbacks, PANEL_DESCRIPTION_TEXT, SKETCH_DESCRIPTION_TEXT
#
#
# @pytest.fixture
# def create_command(username):
#     def wrapper(callback_data: Callbacks = Callbacks.PANEL):
#         return CreateBaseOrderCommand(username=username, callback_data=callback_data)
#
#     return wrapper
#
#
# class TestUseCases:
#
#     @pytest.mark.parametrize('callback, expected_product, expected_text', (
#             (Callbacks.PANEL, ProductType.HANDMADE_PANEL, PANEL_DESCRIPTION_TEXT),
#             (Callbacks.SKETCH, ProductType.SKETCH_PANEL, SKETCH_DESCRIPTION_TEXT),
#             (Callbacks.READY_PANEL, ProductType.READY_PANEL, PANEL_DESCRIPTION_TEXT)
#     ))
#     async def test_create(
#             self, order_service, create_command, username, engine,
#             callback, expected_text, expected_product
#     ):
#         text = await order_service.create_base_order(command=create_command(callback_data=callback))
#         result = engine[username]
#         assert result['product_type'] == expected_product
#         assert text == expected_text
#
#     async def test_create_with_exception(self, order_service, create_command):
#         with pytest.raises(NotCorrectedProductType):
#             await order_service.create_base_order(command=create_command(callback_data='test'))  # type: ignore
#
#     async def test_update(self, order_service, create_command, username, engine):
#         await order_service.create_base_order(command=create_command())
#         desc = 'test'
#         await order_service.update_order(UpdateOrderCommand(username=username, description=desc))
#         result = engine[username]
#         assert result['description'] == desc
#
#     async def test_update_error(self, order_service, create_command, username):
#         with raises(NotEnoughUpdateInfoException):
#             await order_service.create_base_order(command=create_command())
#             await order_service.update_order(UpdateOrderCommand(username=username))
