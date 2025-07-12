from telegram.ext import (
    ConversationHandler, MessageHandler, filters, CommandHandler, CallbackQueryHandler
)

from bootstrap.constants import (Callbacks, Commands, States)
from presentation.callback import OrderCallback
from presentation.command import OrderCommands


def build_conv_handler(order_commands: OrderCommands, order_callback: OrderCallback):
    return ConversationHandler(
        entry_points=[CommandHandler(Commands.START, order_commands.start)],

        states={
            States.START: [CallbackQueryHandler(
                callback=order_callback.start_callback,
                pattern=f"^{Callbacks.NEW_ORDER}$|^{Callbacks.CANCEL_AND_CREATE}$|"
                        f"^{Callbacks.ORDERS}$"
                        f"|^{Callbacks.CONTINUE_DESC}.*|^{Callbacks.CONTINUE_PHOTO}.*"
                        f"|^{Callbacks.CONTINUE_DELIVERY}.*|^{Callbacks.CONTINUE_ADDRESS}.*"
            )],
            States.PANEL_TYPE: [CallbackQueryHandler(
                callback=order_callback.panel_type_callback,
                pattern=f"^{Callbacks.READY_PANEL}$|^{Callbacks.HANDMADE_PANEL}$"
            )],
            States.HANDMADE_PANEL_TYPE: [CallbackQueryHandler(
                callback=order_callback.product_description_callback,
                pattern=f"^{Callbacks.PANEL}$|^{Callbacks.SKETCH}$"
            )],
            States.DESCRIPTION: [
                MessageHandler(
                    filters=(filters.TEXT & ~filters.COMMAND),
                    callback=order_callback.description_callback
                )
            ],
            States.PHOTO_DESCRIPTION: [
                MessageHandler(
                    filters=filters.PHOTO | filters.ATTACHMENT,
                    callback=order_callback.photo_callback
                )
            ],
            States.ADDRESS_TYPE: [
                CallbackQueryHandler(
                    callback=order_callback.address_type_callback,
                    pattern=f"^{Callbacks.PICKUP_DELIVERY}$|^{Callbacks.YANDEX_DELIVERY}$|^{Callbacks.OTHER_DELIVERY}$|"
                )
            ],
            States.ADDRESS_DESC: [
                MessageHandler(
                    filters=(filters.TEXT & ~filters.COMMAND),
                    callback=order_callback.address_desc_callback
                )
            ]

        },

        fallbacks=[CommandHandler(Commands.CANCEL, order_commands.cancel)],
    )
