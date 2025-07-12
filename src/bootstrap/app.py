from telegram.ext import (
    Application, ConversationHandler, MessageHandler, filters, CommandHandler, CallbackQueryHandler
)

from application.queries import OrderQueries
from application.usecases import OrderCallbackService
from bootstrap.settings import AppSettings, FSStorageSettings
from bootstrap.constants import Callbacks, Commands, States
from sqlalchemy.ext.asyncio import (create_async_engine, AsyncEngine)

from infrastructure.db.repos import OrderRepo
from infrastructure.integations.file_storage.fs_client import FSStorage
from presentation.callback import OrderCallback
from presentation.command import OrderCommands


async def post_init(app: Application):
    await app.bot.set_my_commands([(Commands.START, 'Заказать'), (Commands.CANCEL, 'Отменить заказ')])  # type: ignore


def setup_app() -> Application:
    app_settings = AppSettings()
    app = Application.builder().token(app_settings.token).post_init(post_init).build()
    engine = create_engine(app_settings)
    order_repo, order_view = setup_order_repo(engine=engine), setup_order_view(engine=engine)
    order_service = setup_order_service(repo=order_repo)
    order_commands = setup_order_command(view=order_view, order_service=order_service)
    fs_storage_adapter = setup_storage_adapter()
    order_callback = OrderCallback(order_service=order_service, storage_adapter=fs_storage_adapter)

    conv_handler = ConversationHandler(
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
    app.add_handler(conv_handler)
    return app


def setup_order_repo(engine: AsyncEngine):
    return OrderRepo(engine=engine)


def setup_order_view(engine: AsyncEngine):
    return OrderQueries(engine=engine)


def setup_order_service(repo: OrderRepo):
    return OrderCallbackService(repo=repo)


def setup_order_command(view: OrderQueries, order_service: OrderCallbackService):
    return OrderCommands(order_view=view, order_service=order_service)


def create_engine(config: AppSettings) -> AsyncEngine:
    return create_async_engine(config.db_url, pool_pre_ping=True)


def setup_storage_adapter():
    settings = FSStorageSettings()
    return FSStorage(path=settings.path, ext=settings.ext)
