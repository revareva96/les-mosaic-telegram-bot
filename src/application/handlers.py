from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from bootstrap.constants import Callbacks, States, TextInfo, OrderStatus, PRODUCT_TYPE_TEXT_MAPPER, ProductType


def switch_status_handler(status: str, product_type: str):
    button_text, text = TextInfo.CONTINUE, TextInfo.START_WITH_ORDER
    text = text.format(product_type=PRODUCT_TYPE_TEXT_MAPPER[product_type])
    if status == OrderStatus.CREATED:
        if product_type == ProductType.SKETCH_PANEL:
            callback_data = Callbacks.CONTINUE_PHOTO + '_' + product_type
        else:
            callback_data = Callbacks.CONTINUE_DESC + '_' + product_type
    elif status == OrderStatus.ADDED_PHOTO:
        callback_data = Callbacks.CONTINUE_DESC + '_' + product_type
    elif status == OrderStatus.ADDED_DESC:
        callback_data = Callbacks.CONTINUE_DELIVERY + '_' + product_type
    elif status == OrderStatus.ADDED_DELIVERY:
        callback_data = Callbacks.CONTINUE_ADDRESS
    else:
        callback_data = Callbacks.FINISH + '_' + product_type
    keyboard = [
        InlineKeyboardButton(text=TextInfo.CONTINUE, callback_data=callback_data),
        InlineKeyboardButton(text=TextInfo.CANCEL_AND_CREATE, callback_data=Callbacks.CANCEL_AND_CREATE)
    ]
    return text, keyboard


async def start_handler(orders: list[dict]):
    if orders:
        order_status, product_type = orders[0]['status'], orders[0]['product_type']
        text, keyboard = switch_status_handler(status=order_status, product_type=product_type)
    else:
        text = TextInfo.START
        keyboard = [
            InlineKeyboardButton(text=TextInfo.NEW_ORDER, callback_data=Callbacks.NEW_ORDER),
            InlineKeyboardButton(text=TextInfo.EXISTING_ORDERS, callback_data=Callbacks.ORDERS)
        ]

    return text, InlineKeyboardMarkup([keyboard])


# async def panel_type_handler(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
#     keyboard = [
#         [
#             InlineKeyboardButton(text=TextInfo.READY_PANEL_DESC, callback_data=Callbacks.READY_PANEL),
#             InlineKeyboardButton(text=TextInfo.HANDMADE_PANEL_DESC, callback_data=Callbacks.HANDMADE_PANEL)
#         ]
#     ]
#     markup = InlineKeyboardMarkup(keyboard)
#     await context.bot.send_message(
#         chat_id=chat_id,
#         text=TextInfo.PANEL_TYPE,
#         reply_markup=markup
#     )
#     return States.PANEL_TYPE


# async def continue_desc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     text = TextInfo.PANEL_DESCRIPTION
#     await context.bot.send_message(
#         chat_id=update.effective_chat.id,
#         text=text
#     )
#     return States.DESCRIPTION


# async def continue_photo_handler(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
#     await context.bot.send_message(
#         chat_id=chat_id,
#         text=TextInfo.SKETCH_DESCRIPTION
#     )
#     return States.PHOTO_DESCRIPTION


# async def handmade_panel_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     keyboard = [
#         [
#             InlineKeyboardButton(text=TextInfo.PANEL_DESC, callback_data=Callbacks.PANEL),
#             InlineKeyboardButton(text=TextInfo.SCRATCH_DESC, callback_data=Callbacks.SKETCH)
#         ]
#     ]
#     markup = InlineKeyboardMarkup(keyboard)
#     await context.bot.send_message(
#         chat_id=update.effective_chat.id,
#         text=TextInfo.PANEL_SWITCH,
#         reply_markup=markup
#     )
#     return States.HANDMADE_PANEL_TYPE


# async def order_description_handler(
#         chat_id: int,
#         context: ContextTypes.DEFAULT_TYPE
# ):
#     keyboard = [
#         [InlineKeyboardButton(text=TextInfo.PICKUP_DELIVERY, callback_data=Callbacks.PICKUP_DELIVERY)],
#         [
#             InlineKeyboardButton(text=TextInfo.YANDEX_DELIVERY, callback_data=Callbacks.YANDEX_DELIVERY),
#             InlineKeyboardButton(text=TextInfo.OTHER_DELIVERY, callback_data=Callbacks.OTHER_DELIVERY)
#         ]
#     ]
#     await context.bot.send_message(
#         chat_id=chat_id,
#         text=TextInfo.ORDER_SAVED_DESCRIPTION,
#         reply_markup=InlineKeyboardMarkup(keyboard)
#     )
#     return States.ADDRESS_TYPE


async def address_type_handler(
        chat_id: int,
        context: ContextTypes.DEFAULT_TYPE,
):
    await context.bot.send_message(
        chat_id=chat_id,
        text=TextInfo.ADDRESS_TYPE_SAVED
    )
    return States.ADDRESS_DESC
