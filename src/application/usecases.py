from enum import StrEnum
from time import time

from application.handlers import address_type_handler
from bootstrap.constants import Callbacks, TextInfo, ProductType, States, DELIVERY_TYPE_CALLBACKS_MAPPER
from infrastructure.dal.abstractions import IOrderRepo
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler


class OrderStatus(StrEnum):
    CREATED = 'CREATED'
    ADDED_DESC = 'ADDED_DESC'
    ADDED_PHOTO = 'ADDED_PHOTO'
    ADDED_DELIVERY = 'ADDED_DELIVERY'
    ACCEPTED = 'ACCEPTED'
    CANCELED = 'CANCELED'


class OrderCallbackService:

    def __init__(self, repo: IOrderRepo):
        self._repo = repo

    # async def start_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     query = update.callback_query
    #     await query.answer()
    #     chat_id = update.effective_chat.id
    #
    #     query_data = query.data
    #     if query_data == Callbacks.ORDERS:
    #         await context.bot.send_message(
    #             chat_id=chat_id,
    #             text=TextInfo.ORDERS
    #         )
    #     elif query_data == Callbacks.NEW_ORDER:
    #         return await panel_type_handler(chat_id=chat_id, context=context)
    #     elif query_data == Callbacks.CANCEL_AND_CREATE:
    #         await self._repo.update_order(
    #             username=update.effective_chat.username,
    #             info={
    #                 'status': OrderStatus.CANCELED
    #             }
    #         )
    #         return await panel_type_handler(chat_id=chat_id, context=context)
    #     elif query_data.startswith(Callbacks.CONTINUE_DESC):
    #         return await continue_desc_handler(update=update, context=context)
    #     elif query_data.startswith(Callbacks.CONTINUE_PHOTO):
    #         return await continue_photo_handler(chat_id=chat_id, context=context)
    #     elif query_data.startswith(Callbacks.CONTINUE_DELIVERY):
    #         return await order_description_handler(chat_id=update.effective_chat.id, context=context)
    #     elif query_data == Callbacks.CONTINUE_ADDRESS:
    #         return await address_type_handler(chat_id=chat_id, context=context)

    async def start_order(self, data: str, username: str) -> tuple[str, InlineKeyboardMarkup, States]:
        state, markup = None, None
        if data == Callbacks.ORDERS:
            text = TextInfo.ORDER_SAVED_TEXT_ERROR
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

    # async def product_description_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     query = update.callback_query
    #     await query.answer()
    #     callback_data, username, chat_id = query.data, update.effective_chat.username, update.effective_chat.id
    #     info = {}
    #     if callback_data == Callbacks.PANEL:
    #         info['product_type'] = ProductType.HANDMADE_PANEL
    #         text = TextInfo.PANEL_DESCRIPTION
    #     elif callback_data == Callbacks.SKETCH:
    #         info['product_type'] = ProductType.SKETCH_PANEL
    #         text = TextInfo.SKETCH_DESCRIPTION
    #     else:
    #         info['product_type'] = ProductType.READY_PANEL
    #         text = TextInfo.PANEL_DESCRIPTION
    #     order = await self._repo.get_uncompleted_order(username=username)
    #     if not order:
    #         info['username'] = username
    #         await self._repo.create_order(info)
    #     else:
    #         await self._repo.update_order(username=username, info=info)
    #     state = States.DESCRIPTION
    #     if text == TextInfo.SKETCH_DESCRIPTION:
    #         state = States.PHOTO_DESCRIPTION
    #
    #     await context.bot.send_message(
    #         chat_id=chat_id,
    #         text=text,
    #     )
    #
    #     return state

    async def add_product_description(self, data: str, username: str):
        info = {}
        if data == Callbacks.PANEL:
            info['product_type'] = ProductType.HANDMADE_PANEL
            text = TextInfo.PANEL_DESCRIPTION
        elif data == Callbacks.SKETCH:
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

    # async def panel_type_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     query = update.callback_query
    #     await query.answer()
    #
    #     if query.data == Callbacks.READY_PANEL:
    #         return await self.product_description_callback(
    #             update=update,
    #             context=context
    #         )
    #     elif query.data == Callbacks.HANDMADE_PANEL:
    #         return await handmade_panel_type_handler(update=update, context=context)

    async def add_panel_type(self, data: str, username: str):
        markup = None
        if data == Callbacks.READY_PANEL:
            text, state = await self.add_product_description(data=data, username=username)
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

    # async def description_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     info = {
    #         'description': update.message.text,
    #         'status': OrderStatus.ADDED_DESC
    #     }
    #     await self._repo.update_order(username=update.effective_user.username, info=info)
    #     return await order_description_handler(chat_id=update.effective_chat.id, context=context)

    async def add_order_description(self, username: str, description: str):
        info = {
            'description': description,
            'status': OrderStatus.ADDED_DESC
        }
        await self._repo.update_order(username=username, info=info)

        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=TextInfo.PICKUP_DELIVERY, callback_data=Callbacks.PICKUP_DELIVERY)],
            [
                InlineKeyboardButton(text=TextInfo.YANDEX_DELIVERY, callback_data=Callbacks.YANDEX_DELIVERY),
                InlineKeyboardButton(text=TextInfo.OTHER_DELIVERY, callback_data=Callbacks.OTHER_DELIVERY)
            ]
        ])
        text, state = TextInfo.ORDER_SAVED_DESCRIPTION, States.ADDRESS_TYPE
        return text, state, markup

    async def photo_description_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        username = update.effective_chat.username
        docs = update.message.photo or [update.message.document]
        if len(docs) == 0 or not docs[0] or (
                update.message.document and not update.message.document.mime_type.startswith('image/')):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=TextInfo.ORDER_SAVED_PHOTO_ERROR
            )
            return States.PHOTO_DESCRIPTION

        # todo - move logic with storage adapter
        # names = []
        # for photo_id in docs:
        obj = await context.bot.get_file(docs[-1])
        ext = 'jpeg'
        file_ext = obj.file_path.split('.')
        if file_ext:
            ext = file_ext[-1]
        photo_id = f'{username}_{int(time())}.{ext}'
        await obj.download_to_drive(custom_path=f'./photos/{photo_id}')
        # names.append(photo_name)

        info = {
            'status': OrderStatus.ADDED_PHOTO,
            'photo_id': photo_id
        }
        await self._repo.update_order(username=username, info=info)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=TextInfo.PANEL_DESCRIPTION,
        )
        return States.DESCRIPTION

    async def address_type_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        await self._repo.update_order(
            username=update.effective_chat.username,
            info={
                'status': OrderStatus.ADDED_DELIVERY,
                'delivery_type': DELIVERY_TYPE_CALLBACKS_MAPPER[query.data]
            }
        )
        return await address_type_handler(
            chat_id=update.effective_chat.id,
            context=context
        )

    async def address_desc_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._repo.update_order(
            username=update.effective_chat.username,
            info={
                'status': OrderStatus.ACCEPTED,
                'address': update.message.text
            }
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=TextInfo.ADDRESS_DESC_SAVED
        )
        return ConversationHandler.END

    async def cancel(self, username: str):
        await self._repo.update_order(
            username=username,
            info={
                'status': OrderStatus.CANCELED
            }
        )
        return ConversationHandler.END
