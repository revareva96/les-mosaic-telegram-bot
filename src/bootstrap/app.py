from telegram.ext import Application
from sqlalchemy.ext.asyncio import (create_async_engine, AsyncEngine)

from application.queries import OrderQueries
from application.usecases import OrderCallbackService
from bootstrap.builder import build_conv_handler
from bootstrap.logger import setup_logger
from bootstrap.settings import (AppSettings, FSStorageSettings)
from bootstrap.constants import (Commands, TextInfo)
from infrastructure.dal.repos import OrderRepo
from infrastructure.integations.file_storage.fs_client import FSStorage
from presentation.callback import OrderCallback
from presentation.command import OrderCommands


async def post_init(app: Application):
    await app.bot.set_my_commands(  # type: ignore
        [(Commands.START, TextInfo.START_ORDER), (Commands.CANCEL, TextInfo.CANCEL_ORDER)])


def setup_app() -> Application:
    app_settings = AppSettings()
    app = Application.builder().token(app_settings.token).post_init(post_init).build()
    setup_logger(app_settings)

    engine = create_engine(app_settings)
    order_repo, order_view = setup_order_repo(engine=engine), setup_order_view(engine=engine)
    order_service = setup_order_service(repo=order_repo)
    order_commands = setup_order_command(view=order_view, order_service=order_service)
    fs_storage_adapter = setup_storage_adapter()
    order_callback = OrderCallback(order_service=order_service, storage_adapter=fs_storage_adapter)

    conv_handler = build_conv_handler(order_commands=order_commands, order_callback=order_callback)
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
