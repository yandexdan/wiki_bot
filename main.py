# Импортируем необходимые классы.
import logging, wikipedia, re
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup
from config import BOT_TOKEN, LANGUAGE

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

reply_keyboard = [['/start', '/help', '/about', '/lang']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


async def help(update, context):
    await update.message.reply_text(
        "Просто введи слово в чат, и я дам информацию по нему.\n"
        'lang - смена языка поиска')


async def start(update, context):
    await update.message.reply_text(
        "Привет, Я бот справочник!\n"
        "Могу найти информацию по слову.", reply_markup=markup) 


async def about(update, context):
    await update.message.reply_text('Меня завут Курдин Даниил, а это мой проект - чат_бот поисковик.\n'
                                    'Он получает слово у пользывателя и ищет информацию о нём в wikipedia.\n'
                                    'Мой Git-hub: https://github.com/yandexdan/wiki_bot')


async def lang(update, context):
    await update.message.reply_text('Эта команда устанавливает язык поиска. Какой язык установить?\n'
                                    'Введите после этого сообщения: en/ru/de и др.)')
    return 1


async def response(update, context):
    global LANGUAGE
    # Ответ на вопрос.
    langu = update.message.text
    if langu in wikipedia.languages():
        LANGUAGE = langu
        logger.info(LANGUAGE)
        await update.message.reply_text(f"Выбран: {LANGUAGE}")
        return ConversationHandler.END
    else:
        await update.message.reply_text(f"Выбран некорректный язык, отмена команды")
        return ConversationHandler.END


async def stop(update, context):
    await update.message.reply_text("отмена")
    return ConversationHandler.END

conv_handler = ConversationHandler(
        # Точка входа в диалог.
        entry_points=[CommandHandler('lang', lang)],

        # Состояние внутри диалога.
        states={
            # Функция читает ответ на первый вопрос и завершает диалог.
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, response)]
        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)]
    )


async def search(update, context):
    try:
        wikipedia.set_lang(LANGUAGE)
        ny = wikipedia.page(update.message.text)
        # Получаем первую тысячу символов
        wikitext = ny.content[:1000]
        # Разделяем по точкам
        wikimas = wikitext.split('.')
        # Отбрасываем всЕ после последней точки
        wikimas = wikimas[:-1]
        # Создаем пустую переменную для текста
        wikitext2 = ''
        # Проходимся по строкам, где нет знаков «равно» (то есть все, кроме заголовков)
        for x in wikimas:
            if not('==' in x):
                    # Если в строке осталось больше трех символов, добавляем ее к нашей переменной и возвращаем утерянные при разделении строк точки на место
                if (len((x.strip())) > 3):
                   wikitext2 = wikitext2 + x + '.'
            else:
                break
        # Теперь при помощи регулярных выражений убираем разметку
        wikitext2 = re.sub('\([^()]*\)', '', wikitext2)
        wikitext2 = re.sub('\([^()]*\)', '', wikitext2)
        wikitext2 = re.sub('\{[^\{\}]*\}', '', wikitext2)
        # Возвращаем текстовую строку
        await update.message.reply_text(wikitext2)
    # Обрабатываем исключение, которое мог вернуть модуль wikipedia при запросе
    except Exception as e:
        await update.message.reply_text('В энциклопедии нет информации об этом.\n '
                                        'Попробуйте уточнить запрос, пример: ``Замок (строение)``')


async def close_keyboard(update, context):
    await update.message.reply_text(
        "Ok",
        reply_markup=markup
    )


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("close", close_keyboard))
    application.add_handler(CommandHandler("about", about))

    application.add_handler(conv_handler)

    text_handler = MessageHandler(filters.TEXT, search)
    application.add_handler(text_handler)

    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()

