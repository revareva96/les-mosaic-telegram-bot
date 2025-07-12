from application.usecases import OrderCallbackService

from telegram import Update
from telegram.ext import ContextTypes

from bootstrap.constants import Callbacks


class OrderCallback:

    def __init__(self, order_service: OrderCallbackService):
        self._service = order_service

    async def start_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        query_date = query.data
        username = update.effective_chat.username

        text, markup, state = await self._service.start_order(data=query_date, username=username)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=markup
        )
        return state

    async def product_description_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        callback_data, username, chat_id = query.data, update.effective_chat.username, update.effective_chat.id

        text, state = await self._service.add_product_description(data=callback_data, username=username)
        await context.bot.send_message(
            chat_id=chat_id,
            text=text,
        )
        return state

    async def panel_type_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        query_data, username = query.data, update.effective_chat.username

        text, state, markup = await self._service.add_panel_type(data=query_data, username=username)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=markup
        )
        return state

    async def description_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        username, description = update.effective_chat.username, update.message.text
        text, state, markup = await self._service.add_order_description(username=username, description=description)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=markup
        )
        return state
