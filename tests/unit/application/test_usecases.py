import pytest
from telegram import InlineKeyboardMarkup
from telegram.ext import ConversationHandler

from application.usecases import OrderCallbackService, StartOrderCommand, CreateBaseOrderCommand, AddPanelTypeCommand, \
    AddDescCommand, AddPhotoCommand, AddAddressTypeCommand, AddAddressDescCommand, CancelOrderCommand
from bootstrap.constants import Callbacks, TextInfo, States, OrderStatus, ProductType, DeliveryType


class TestUseCases:

    @pytest.fixture(autouse=True)
    def setup(self, fake_order_repo):
        self._service = OrderCallbackService(repo=fake_order_repo)

    @pytest.mark.parametrize('callback_data, expected_text, expected_markup, expected_state', (
            (Callbacks.ORDERS, TextInfo.ORDERS, None, None),
            (Callbacks.NEW_ORDER, TextInfo.PANEL_TYPE, InlineKeyboardMarkup, States.PANEL_TYPE),
            (Callbacks.CONTINUE_DESC, TextInfo.PANEL_DESCRIPTION, None, States.DESCRIPTION),
            (Callbacks.CONTINUE_PHOTO, TextInfo.SKETCH_DESCRIPTION, None, States.PHOTO_DESCRIPTION),
            (Callbacks.CONTINUE_DELIVERY, TextInfo.ORDER_SAVED_DESCRIPTION, InlineKeyboardMarkup, States.ADDRESS_TYPE),
            (Callbacks.CONTINUE_ADDRESS, TextInfo.ADDRESS_TYPE_SAVED, None, States.ADDRESS_DESC)
    ))
    async def test_start_order(self, username, callback_data, expected_text, expected_markup, expected_state):
        text, markup, state = await self._service.start_order(command=StartOrderCommand(
            username=username,
            callback_data=callback_data
        ))
        assert text == expected_text
        if not expected_markup:
            assert not markup
        else:
            assert isinstance(markup, expected_markup)
        assert state == expected_state

    @pytest.mark.parametrize('product_type, expected_text, expected_state, expected_product_type', (
            (Callbacks.PANEL, TextInfo.PANEL_DESCRIPTION, States.DESCRIPTION, ProductType.HANDMADE_PANEL),
            (Callbacks.SKETCH, TextInfo.SKETCH_DESCRIPTION, States.PHOTO_DESCRIPTION, ProductType.SKETCH_PANEL),
            ('', TextInfo.PANEL_DESCRIPTION, States.DESCRIPTION, ProductType.READY_PANEL),
    ))
    async def test_create_order(
            self, username, engine,
            product_type, expected_text, expected_state, expected_product_type
    ):
        text, state = await self._service.add_product_description(command=CreateBaseOrderCommand(
            username=username,
            product_type=product_type
        ))
        assert text == expected_text
        assert state == expected_state
        assert engine[0]['product_type'] == expected_product_type

    async def test_create_and_cancel_order(self, username, engine):
        await self._service.add_product_description(command=CreateBaseOrderCommand(
            username=username,
            product_type=Callbacks.PANEL
        ))

        text, markup, state = await self._service.start_order(command=StartOrderCommand(
            username=username,
            callback_data=Callbacks.CANCEL_AND_CREATE
        ))
        assert text == TextInfo.PANEL_TYPE
        assert markup.inline_keyboard[0][0].text == TextInfo.READY_PANEL_DESC
        assert markup.inline_keyboard[0][1].text == TextInfo.HANDMADE_PANEL_DESC
        assert state == States.PANEL_TYPE
        assert engine[0]['status'] == OrderStatus.CANCELED

    @pytest.mark.parametrize('panel_type, expected_text, expected_state', (
            (Callbacks.READY_PANEL, TextInfo.PANEL_DESCRIPTION, States.DESCRIPTION),
            (Callbacks.HANDMADE_PANEL, TextInfo.PANEL_SWITCH, States.HANDMADE_PANEL_TYPE)
    ))
    async def test_add_panel_type(self, username, panel_type, expected_text, expected_state):
        text, state, _ = await self._service.add_panel_type(command=AddPanelTypeCommand(
            username=username,
            panel_type=panel_type
        ))
        assert text == expected_text
        assert state == expected_state

    async def test_add_order_description(self, username, engine):
        await self._service.add_product_description(command=CreateBaseOrderCommand(
            username=username,
            product_type=Callbacks.PANEL
        ))

        text, state, markup = await self._service.add_order_description(command=AddDescCommand(
            username=username,
            product_desc='test'
        ))
        assert text == TextInfo.ORDER_SAVED_DESCRIPTION
        assert state == States.ADDRESS_TYPE
        assert markup.inline_keyboard[0][0].text == TextInfo.PICKUP_DELIVERY
        assert markup.inline_keyboard[1][0].text == TextInfo.YANDEX_DELIVERY
        assert markup.inline_keyboard[1][1].text == TextInfo.OTHER_DELIVERY
        assert engine[0]['status'] == OrderStatus.ADDED_DESC

    async def test_add_photo(self, username, engine):
        await self._service.add_product_description(command=CreateBaseOrderCommand(
            username=username,
            product_type=Callbacks.PANEL
        ))

        photo_id = '1'
        text, state = await self._service.add_photo(command=AddPhotoCommand(
            username=username,
            photo_id=photo_id
        ))
        assert text == TextInfo.PANEL_DESCRIPTION
        assert state == States.DESCRIPTION
        assert engine[0]['status'] == OrderStatus.ADDED_PHOTO
        assert engine[0]['photo_id'] == photo_id

    @pytest.mark.parametrize('address_type, expected_delivery_type', (
            (Callbacks.PICKUP_DELIVERY, DeliveryType.PICKUP),
            (Callbacks.YANDEX_DELIVERY, DeliveryType.YANDEX_DELIVERY),
            (Callbacks.OTHER_DELIVERY, DeliveryType.OTHER_DELIVERY)
    ))
    async def test_address_type(self, username, engine, address_type, expected_delivery_type):
        await self._service.add_product_description(command=CreateBaseOrderCommand(
            username=username,
            product_type=Callbacks.PANEL
        ))

        text, state = await self._service.add_address_type(command=AddAddressTypeCommand(
            username=username,
            address_type=address_type
        ))
        assert text == TextInfo.ADDRESS_TYPE_SAVED
        assert state == States.ADDRESS_DESC
        assert engine[0]['delivery_type'] == expected_delivery_type

    async def test_add_desc(self, username, engine):
        await self._service.add_product_description(command=CreateBaseOrderCommand(
            username=username,
            product_type=Callbacks.PANEL
        ))

        address_description = 'test'
        text, state = await self._service.add_desc(command=AddAddressDescCommand(
            username=username,
            desc=address_description
        ))
        assert text == TextInfo.ADDRESS_DESC_SAVED
        assert state == ConversationHandler.END
        assert engine[0]['status'] == OrderStatus.ACCEPTED
        assert engine[0]['address'] == address_description

    async def test_cancel(self, username, engine):
        await self._service.add_product_description(command=CreateBaseOrderCommand(
            username=username,
            product_type=Callbacks.PANEL
        ))

        state = await self._service.cancel(command=CancelOrderCommand(
            username=username
        ))
        assert state == ConversationHandler.END
        assert engine[0]['status'] == OrderStatus.CANCELED
