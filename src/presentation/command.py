from telegram import Update
from telegram.ext import (ContextTypes, ConversationHandler)

from application.handlers import start_handler
from application.queries import OrderQueries
from application.usecases import (OrderCallbackService, CancelOrderCommand)
from bootstrap.constants import (States, TextInfo)


class OrderCommands:

    def __init__(self, order_view: OrderQueries, order_service: OrderCallbackService):
        self._view = order_view
        self._service = order_service

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        username = update.effective_chat.username
        orders = await self._view.get_active_order(username=username)
        text, markup = await start_handler(orders=orders)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=markup
        )
        return States.START

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._service.cancel(command=CancelOrderCommand(username=update.effective_chat.username))
        await update.message.reply_text(
            text=TextInfo.CANCEL
        )

        return ConversationHandler.END
