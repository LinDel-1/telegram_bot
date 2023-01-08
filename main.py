from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters, ApplicationBuilder

from database_connection import DataBase
from config_file import TOKEN
from image_func_application import get_cat_image_with_date

# Создаём глобальную переменную, в которой открывается подключение к БД и реализованы методы для работы с ней
database = DataBase()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Функция-обработчик команды /start.
    Отправляет пользователю дату и время на фоне котёнка
    """

    photo = get_cat_image_with_date()
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=photo
    )

    database.create_row(update.effective_user, update.message.text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Функция-обработчик команды /help
    Выводит возможные команды, которые понимает бот
    """

    text = '''
    Привет! Я бот, который подскажет время и поднимет тебе настроение!
    
*Доступные команды:*
    /start - Подскажу время.
    /help - Справка.
        '''
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode='MARKDOWN'
    )


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Функция-обработчик неопознанных команд
    """
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Я не знаю комманду: {update.message.text}. Напиши /help для справки'
    )


async def echo_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Функция-обработчик текстовых сообщений пользователя
    """
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Я повторюшка! Ты сказал: {update.message.text}.'
    )


async def echo_other(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Функция-обработчик НЕ текстовых (аудио, видео, вложения) сообщений пользователя
    """
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Эээ... Буквы сейчас бесплатные, если что.'
    )


def main() -> None:
    # ApplicationBuilder это инициализация инстанса класса Application.
    # Application - класс, который отправляет все виды обновлений к зарегестрированным handlers, является точкой входа
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start_command)
    help_handler = CommandHandler('help', help_command)
    echo_other_handler = MessageHandler(filters.ATTACHMENT | filters.AUDIO, echo_other)
    echo_text_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo_text)
    unknown_command_handler = MessageHandler(filters.COMMAND, unknown_command)

    application.add_handler(echo_other_handler)
    application.add_handler(echo_text_handler)
    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(unknown_command_handler)

    # Метод, который инициализирует и запускает бота
    application.run_polling()


if __name__ == "__main__":
    main()
