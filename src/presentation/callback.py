from logging import getLogger

from telegram import Update
from telegram.ext import ContextTypes

from application.usecases import (
    OrderCallbackService, AddPhotoCommand, AddAddressTypeCommand, AddAddressDescCommand,
    StartOrderCommand, CreateBaseOrderCommand, AddPanelTypeCommand, AddDescCommand
)
from bootstrap.constants import (TextInfo, States)
from infrastructure.integations.file_storage.abstractions import IStorage


class OrderCallback:

    def __init__(self, order_service: OrderCallbackService, storage_adapter: IStorage):
        self._service = order_service
        self._storage_adapter = storage_adapter
        self._logger = getLogger(name='les_mosaic')

    async def start_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        username = update.effective_chat.username

        text, markup, state = await self._service.start_order(command=StartOrderCommand(
            username=username,
            callback_data=query.data
        ))
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=markup
        )
        self._logger.info(msg=f'Start order with text {text}; state - {state} for user - {username}.')
        return state

    async def product_description_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        username = update.effective_chat.username

        text, state = await self._service.add_product_description(CreateBaseOrderCommand(
            username=username,
            product_type=query.data
        ))
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
        )
        self._logger.info(msg=f'Update order product description with state - {state} for user - {username}.')
        return state

    async def panel_type_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        username = update.effective_chat.username

        text, state, markup = await self._service.add_panel_type(AddPanelTypeCommand(
            username=username,
            panel_type=query.data
        ))
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=markup
        )
        self._logger.info(msg=f'Add order panel_type with state - {state} for user - {username}.')
        return state

    async def description_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text, state, markup = await self._service.add_order_description(AddDescCommand(
            username=update.effective_chat.username,
            product_desc=update.message.text
        ))
        username = update.effective_chat.username

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=markup
        )
        self._logger.info(msg=f'Add order description with state - {state} for user - {username}.')
        return state

    async def photo_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        username = update.effective_chat.username
        docs = update.message.photo or [update.message.document]
        if len(docs) == 0 or not docs[0] or (
                update.message.document and not update.message.document.mime_type.startswith('image/')):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=TextInfo.ORDER_SAVED_PHOTO_ERROR
            )
            return States.PHOTO_DESCRIPTION

        obj = await context.bot.get_file(docs[-1])
        photo_id = await self._storage_adapter.save_photo(username=username, file=obj)
        text, state = await self._service.add_photo(AddPhotoCommand(username=username, photo_id=photo_id))
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text
        )
        self._logger.info(msg=f'Add order photo with state - {state} for user - {username}.')
        return state

    async def address_type_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        username = update.effective_chat.username

        text, state = await self._service.add_address_type(command=AddAddressTypeCommand(
            username=username,
            address_type=query.data
        ))
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text
        )
        self._logger.info(msg=f'Add address type with state - {state} for user - {username}.')
        return state

    async def address_desc_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        username = update.effective_chat.username
        text, state = await self._service.add_desc(command=AddAddressDescCommand(
            username=username,
            desc=update.message.text
        ))

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text
        )
        self._logger.info(msg=f'Success order for user - {username}.')
        return state
