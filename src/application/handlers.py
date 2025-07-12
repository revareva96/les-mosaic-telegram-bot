from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bootstrap.constants import Callbacks, TextInfo, OrderStatus, PRODUCT_TYPE_TEXT_MAPPER, ProductType


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
