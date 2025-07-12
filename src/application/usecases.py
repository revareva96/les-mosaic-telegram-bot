from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler
from pydantic import BaseModel

from bootstrap.constants import (Callbacks, TextInfo, ProductType, States, DELIVERY_TYPE_CALLBACKS_MAPPER, OrderStatus)
from infrastructure.dal.abstractions import IOrderRepo


class StartOrderCommand(BaseModel):
    username: str
    callback_data: str


class CreateBaseOrderCommand(BaseModel):
    username: str
    product_type: str


class AddPanelTypeCommand(BaseModel):
    username: str
    panel_type: str


class AddDescCommand(BaseModel):
    username: str
    product_desc: str


class AddPhotoCommand(BaseModel):
    username: str
    photo_id: str


class AddAddressTypeCommand(BaseModel):
    username: str
    address_type: str


class AddAddressDescCommand(BaseModel):
    username: str
    desc: str


class CancelOrderCommand(BaseModel):
    username: str


class OrderCallbackService:

    def __init__(self, repo: IOrderRepo):
        self._repo = repo

    async def start_order(self, command: StartOrderCommand) -> tuple[str, InlineKeyboardMarkup, States]:
        state, markup = None, None
        username, data = command.username, command.callback_data
        if data == Callbacks.ORDERS:
            text = TextInfo.ORDERS
        elif data in (Callbacks.NEW_ORDER, Callbacks.CANCEL_AND_CREATE):
            if data == Callbacks.CANCEL_AND_CREATE:
                await self._repo.update_order(
                    username=username,
                    info={
                        'status': OrderStatus.CANCELED
                    }
                )
            text = TextInfo.PANEL_TYPE
            keyboard = [
                [
                    InlineKeyboardButton(text=TextInfo.READY_PANEL_DESC, callback_data=Callbacks.READY_PANEL),
                    InlineKeyboardButton(text=TextInfo.HANDMADE_PANEL_DESC, callback_data=Callbacks.HANDMADE_PANEL)
                ]
            ]
            markup = InlineKeyboardMarkup(keyboard)
            state = States.PANEL_TYPE
        elif data.startswith(Callbacks.CONTINUE_DESC):
            text = TextInfo.PANEL_DESCRIPTION
            state = States.DESCRIPTION
        elif data.startswith(Callbacks.CONTINUE_PHOTO):
            text = TextInfo.SKETCH_DESCRIPTION
            state = States.PHOTO_DESCRIPTION
        elif data.startswith(Callbacks.CONTINUE_DELIVERY):
            keyboard = [
                [InlineKeyboardButton(text=TextInfo.PICKUP_DELIVERY, callback_data=Callbacks.PICKUP_DELIVERY)],
                [
                    InlineKeyboardButton(text=TextInfo.YANDEX_DELIVERY, callback_data=Callbacks.YANDEX_DELIVERY),
                    InlineKeyboardButton(text=TextInfo.OTHER_DELIVERY, callback_data=Callbacks.OTHER_DELIVERY)
                ]
            ]
            markup = InlineKeyboardMarkup(keyboard)
            text = TextInfo.ORDER_SAVED_DESCRIPTION
            state = States.ADDRESS_TYPE
        else:  # elif data == Callbacks.CONTINUE_ADDRESS
            text = TextInfo.ADDRESS_TYPE_SAVED
            state = States.ADDRESS_DESC
        return text, markup, state

    async def add_product_description(self, command: CreateBaseOrderCommand):
        info = {}
        username, product_type = command.username, command.product_type
        if product_type == Callbacks.PANEL:
            info['product_type'] = ProductType.HANDMADE_PANEL
            text = TextInfo.PANEL_DESCRIPTION
        elif product_type == Callbacks.SKETCH:
            info['product_type'] = ProductType.SKETCH_PANEL
            text = TextInfo.SKETCH_DESCRIPTION
        else:
            info['product_type'] = ProductType.READY_PANEL
            text = TextInfo.PANEL_DESCRIPTION

        order = await self._repo.get_uncompleted_order(username=username)
        if not order:
            info['username'] = username
            await self._repo.create_order(info)
        else:
            await self._repo.update_order(username=username, info=info)
        state = States.DESCRIPTION
        if text == TextInfo.SKETCH_DESCRIPTION:
            state = States.PHOTO_DESCRIPTION
        return text, state

    async def add_panel_type(self, command: AddPanelTypeCommand):
        markup = None
        username, panel_type = command.username, command.panel_type
        if panel_type == Callbacks.READY_PANEL:
            text, state = await self.add_product_description(CreateBaseOrderCommand(
                username=username,
                product_type=panel_type
            ))
        else:  # elif data == Callbacks.HANDMADE_PANEL
            keyboard = [
                [
                    InlineKeyboardButton(text=TextInfo.PANEL_DESC, callback_data=Callbacks.PANEL),
                    InlineKeyboardButton(text=TextInfo.SCRATCH_DESC, callback_data=Callbacks.SKETCH)
                ]
            ]
            markup = InlineKeyboardMarkup(keyboard)
            text, state = TextInfo.PANEL_SWITCH, States.HANDMADE_PANEL_TYPE
        return text, state, markup

    async def add_order_description(self, command: AddDescCommand):
        info = {
            'description': command.product_desc,
            'status': OrderStatus.ADDED_DESC
        }
        await self._repo.update_order(username=command.username, info=info)

        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=TextInfo.PICKUP_DELIVERY, callback_data=Callbacks.PICKUP_DELIVERY)],
            [
                InlineKeyboardButton(text=TextInfo.YANDEX_DELIVERY, callback_data=Callbacks.YANDEX_DELIVERY),
                InlineKeyboardButton(text=TextInfo.OTHER_DELIVERY, callback_data=Callbacks.OTHER_DELIVERY)
            ]
        ])
        text, state = TextInfo.ORDER_SAVED_DESCRIPTION, States.ADDRESS_TYPE
        return text, state, markup

    async def add_photo(self, command: AddPhotoCommand):
        info = {
            'status': OrderStatus.ADDED_PHOTO,
            'photo_id': command.photo_id
        }
        await self._repo.update_order(username=command.username, info=info)
        return TextInfo.PANEL_DESCRIPTION, States.DESCRIPTION

    async def add_address_type(self, command: AddAddressTypeCommand):
        info = {
            'status': OrderStatus.ADDED_DELIVERY,
            'delivery_type': DELIVERY_TYPE_CALLBACKS_MAPPER[command.address_type]
        }
        await self._repo.update_order(
            username=command.username,
            info=info
        )
        return TextInfo.ADDRESS_TYPE_SAVED, States.ADDRESS_DESC

    async def add_desc(self, command: AddAddressDescCommand):
        await self._repo.update_order(
            username=command.username,
            info={
                'status': OrderStatus.ACCEPTED,
                'address': command.desc
            }
        )
        return TextInfo.ADDRESS_DESC_SAVED, ConversationHandler.END

    async def cancel(self, command: CancelOrderCommand):
        await self._repo.update_order(
            username=command.username,
            info={
                'status': OrderStatus.CANCELED
            }
        )
        return ConversationHandler.END
