from enum import StrEnum, IntEnum


class OrderStatus(StrEnum):
    CREATED = 'CREATED'
    ADDED_DESC = 'ADDED_DESC'
    ADDED_PHOTO = 'ADDED_PHOTO'
    ADDED_DELIVERY = 'ADDED_DELIVERY'
    ACCEPTED = 'ACCEPTED'
    CANCELED = 'CANCELED'


class Commands(StrEnum):
    START = 'start'
    CANCEL = 'cancel'


class States(IntEnum):
    """
    Telegram bot lifecycle:
                    START
            /                   \
        PANEL_TYPE      HANDMADE_PANEL_TYPE

    """

    START = 0
    PANEL_TYPE = 1
    HANDMADE_PANEL_TYPE = 2
    DESCRIPTION = 3
    PHOTO_DESCRIPTION = 4
    ADDRESS_TYPE = 5
    ADDRESS_DESC = 6


class Callbacks(StrEnum):
    NEW_ORDER = 'NEW_ORDER'
    ORDERS = 'ORDERS'
    CANCEL_AND_CREATE = 'CANCEL_AND_CREATE'

    CONTINUE_DESC = 'CONTINUE_CREATED'
    CONTINUE_PHOTO = 'CONTINUE_PHOTO'
    CONTINUE_DELIVERY = 'CONTINUE_DELIVERY'
    CONTINUE_ADDRESS = 'CONTINUE_ADDRESS'
    FINISH = 'FINISH'

    READY_PANEL = 'READY_PANEL'
    HANDMADE_PANEL = 'HANDMADE_PANEL'

    PANEL = 'PANEL'
    SKETCH = 'SKETCH'

    PICKUP_DELIVERY = 'PICKUP_DELIVERY'
    YANDEX_DELIVERY = 'YANDEX_DELIVERY'
    OTHER_DELIVERY = 'OTHER_DELIVERY'


class ProductType(StrEnum):
    READY_PANEL = 'READY_PANEL'  # готовое панно
    HANDMADE_PANEL = 'HANDMADE_PANEL'  # набор по эскизу
    SKETCH_PANEL = 'SKETCH_PANEL'  # готовый набор


class DeliveryType(StrEnum):
    PICKUP = 'PICKUP'
    YANDEX_DELIVERY = 'YANDEX_DELIVERY'
    OTHER_DELIVERY = 'OTHER_DELIVERY'


DELIVERY_TYPE_CALLBACKS_MAPPER = {
    Callbacks.PICKUP_DELIVERY: DeliveryType.PICKUP,
    Callbacks.YANDEX_DELIVERY: DeliveryType.YANDEX_DELIVERY,
    Callbacks.OTHER_DELIVERY: DeliveryType.OTHER_DELIVERY
}

DELIVERY_TYPE_TEXT_MAPPER = {
    DeliveryType.PICKUP: 'Самовывоз (метро Нижегородская)',
    DeliveryType.YANDEX_DELIVERY: 'Яндекс доставка',
    DeliveryType.OTHER_DELIVERY: 'Другое'

}

PRODUCT_TYPE_TEXT_MAPPER = {
    ProductType.READY_PANEL: 'готовое панно',
    ProductType.HANDMADE_PANEL: 'готовый набор',
    ProductType.SKETCH_PANEL: 'набор по эскизу'

}


class TextInfo:
    START = """
Привет! :) 
Это помощник студии мозаики lesmosaic, рад знакомству 💚
Я помогу оформить заказ, а мои коллеги свяжутся с тобой для уточнения деталей.
    """
    CANCEL = "Будем ждать Вас снова! 💚"
    CANCEL_AND_CREATE = "Отменить и оформить новый"
    START_WITH_ORDER = """
Привет! :)
Вижу, что у тебя есть не завершенный заказ - {product_type} 🐣 Что выберешь? 
    """
    CONTINUE = "Продолжить оформление"

    ORDERS = "Данная функция находится в разработке. Будем рады видеть Вас позже. ⏳"
    NEW_ORDER = "Новый заказ"
    EXISTING_ORDERS = "Ваши заказы"

    READY_PANEL_DESC = "Готовое панно 🖼"
    HANDMADE_PANEL_DESC = "Набор для создания панно 👩‍🎨👨‍🎨"
    PANEL_DESC = "Готовый набор☑️"
    SCRATCH_DESC = "Собственный эскиз 🪄"

    PANEL_TYPE = """
Хочешь заказать готовое панно из мозаики или набор для создания панно❔
    """
    PANEL_SWITCH = "Отлично! Давай теперь выберем"
    PANEL_DESCRIPTION = """
Отлично! Напиши описание интересуемого товара 🌟
    """
    SKETCH_DESCRIPTION = """
Приложи одно фото в хорошем качестве 🌟
    """

    ORDER_SAVED_DESCRIPTION = """
Информацию получили ✅ Теперь давай выберем способ доставки :)
    """
    ORDER_SAVED_PHOTO_ERROR = "Ой, забыли приложить фото. Попробуйте еще раз :)"
    ORDER_SAVED_TEXT_ERROR = "Ой, забыли приложить описание. Попробуйте еще раз :)"

    PICKUP_DELIVERY = DELIVERY_TYPE_TEXT_MAPPER[DeliveryType.PICKUP]
    YANDEX_DELIVERY = DELIVERY_TYPE_TEXT_MAPPER[DeliveryType.YANDEX_DELIVERY]
    OTHER_DELIVERY = DELIVERY_TYPE_TEXT_MAPPER[DeliveryType.OTHER_DELIVERY]

    ADDRESS_TYPE_SAVED = """
Отлично ✅ а теперь напиши подробную информацию о доставке (место, время, пункт выдачи и др.)
    """
    ADDRESS_DESC_SAVED = """
    Успешно, спасибо за заказ! Скоро с тобой свяжутся наши менеджеры для подверждения заказа 💚   
"""
