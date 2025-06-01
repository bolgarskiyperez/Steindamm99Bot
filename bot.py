import logging
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Загружаем переменные окружения из .env
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токен и chat_id из окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
FEEDBACK_CHAT_ID = int(os.getenv("FEEDBACK_CHAT_ID"))
# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_interior_images():
    """Возвращает список путей к фотографиям интерьера, которые существуют."""
    existing_images = []
    for image_name in INTERIOR_IMAGES:
        image_path = os.path.join(INTERIOR_IMAGES_DIR, image_name)
        if os.path.exists(image_path):
            existing_images.append(image_path)
        else:
            logger.warning(f"Фотография интерьера {image_path} не найдена")
    return existing_images

def get_menu_images():
    """Возвращает список путей к изображениям меню, которые существуют."""
    existing_images = []
    for image_name in MENU_IMAGES:
        image_path = os.path.join(MENU_IMAGES_DIR, image_name)
        if os.path.exists(image_path):
            existing_images.append(image_path)
        else:
            logger.warning(f"Изображение {image_path} не найдено")
    return existing_images


# Пути к изображениям меню (поместите ваши изображения в папку 'menu_images')
MENU_IMAGES_DIR = "menu_images"
MENU_IMAGES = [
    "menu1.jpg",
    "menu2.jpg", 
    "menu3.jpg",
    "menu4.jpg",
    "menu5.jpg",
    "menu6.jpg"
]

# Пути к фотографиям интерьера (поместите в папку 'interior_photos')
INTERIOR_IMAGES_DIR = "interior_photos"
INTERIOR_IMAGES = [
    "interior1.jpg",
    "interior2.jpg",
    "interior3.jpg",
]

# Контактная информация
CONTACT_INFO = {
    "address": "г.Калининград, ул. Житомирская, 22",
    "phone": "+7 (4012) 38-99-75",
    "hours": "12:00-23:00",
    "coordinates": "https://yandex.ru/maps/-/CDeHbS10"
}

# Ссылка на сервис бронирования (замените на реальную)
BOOKING_URL = "https://clck.ru/36vuug"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет приветственное сообщение с кнопками меню."""
    
    welcome_message = (
        "👋 Добро пожаловать в *Штайндамм 99* — камерный ресторан балтийской кухни, расположенный в историческом центре Калининграда.\n\n"
        "Мы ценим локальные продукты, уважаем сезонность и вдохновляемся культурным наследием этого уникального места.\n\n"
        "📍 Используй меню ниже или кнопки, чтобы узнать больше о концепции, истории, кухне и нашем подходе."
    )
    
    keyboard = [
        [InlineKeyboardButton("📋 Меню", callback_data='menu')],
        [InlineKeyboardButton("🏛️ История района", callback_data='history'),
         InlineKeyboardButton("📸 Интерьер", callback_data='interior')],
        [InlineKeyboardButton("💡 Концепция", callback_data='concept'),
         InlineKeyboardButton("📞 Контакты", callback_data='contacts')],
        [InlineKeyboardButton("💬 Обратная связь", callback_data='feedback')],
        [InlineKeyboardButton("📅 Забронировать столик", url=BOOKING_URL)]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_message, 
        reply_markup=reply_markup, 
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает нажатия на кнопки."""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'menu':
        menu_images = get_menu_images()
        
        if menu_images:
            try:
                if len(menu_images) == 1:
                    with open(menu_images[0], 'rb') as photo:
                        back_button = [[InlineKeyboardButton("← Назад в главное меню", callback_data='back_to_main')]]
                        back_markup = InlineKeyboardMarkup(back_button)
                        
                        # Редактируем сообщение с фото и кнопкой "назад"
                        await query.edit_message_media(
                            media=InputMediaPhoto(media=photo, caption="📋 *МЕНЮ РЕСТОРАНА «ШТАЙНДАММ, 99»*", parse_mode='Markdown'),
                            reply_markup=back_markup
                        )
                else:
                    # Для нескольких фото: отправляем альбом, потом отдельное сообщение с кнопкой "назад"
                    media_group = []
                    for i, image_path in enumerate(menu_images):
                        with open(image_path, 'rb') as photo_file:
                            data = photo_file.read()
                            if i == 0:
                                media_group.append(InputMediaPhoto(
                                    media=data,
                                    caption="📋 *МЕНЮ РЕСТОРАНА «ШТАЙНДАММ, 99»*",
                                    parse_mode='Markdown'
                                ))
                            else:
                                media_group.append(InputMediaPhoto(media=data))
                    
                    # Отправляем альбом фотографий
                    await context.bot.send_media_group(
                        chat_id=query.message.chat_id,
                        media=media_group
                    )
                    
                    # Отправляем кнопку "назад" отдельным сообщением
                    back_button = [[InlineKeyboardButton("← Назад в главное меню", callback_data='back_to_main')]]
                    back_markup = InlineKeyboardMarkup(back_button)
                    
                    await context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text="Выберите действие:",
                        reply_markup=back_markup
                    )
                    
                    # Не удаляем исходное сообщение, оставляем как есть
                
            except Exception as e:
                logger.error(f"Ошибка при отправке изображений меню: {e}")
        else:
            logger.warning("Изображения меню не найдены")
    
    elif query.data == 'history':
        history_text = (
            "🏛️ *История места*\n\n"
        "Ресторан *Штайндамм 99* — это не просто гастрономический проект, а продолжение многовековой традиции.\n\n"
        "Название *Штайндамм* (в переводе с немецкого — 'каменная дамба') — историческое название улицы, "
        "которая проходила здесь во времена Кёнигсберга. Это была одна из главных торговых артерий города, "
        "место притяжения для купцов, горожан и путешественников. Здесь кипела жизнь — рынки, трактиры, лавки, гостиницы, телеграф.\n\n"
        "Здание, в котором мы находимся, — один из немногих уцелевших фрагментов старого города. "
        "Оно пережило войны, бомбардировки и смену эпох. На протяжении всей своей истории это место "
        "всегда оставалось связанным с гастрономией — здесь были трактиры, кафе, рестораны.\n\n"
        "Мы выбрали название *Штайндамм 99*, чтобы сохранить память об этом историческом месте и дать ему новую жизнь. "
        "Сегодня мы продолжаем эту традицию, сочетая уважение к истории с современной интерпретацией балтийской кухни."
        )
        
        back_button = [[InlineKeyboardButton("← Назад в главное меню", callback_data='back_to_main')]]
        back_markup = InlineKeyboardMarkup(back_button)
        
        await query.edit_message_text(
            text=history_text,
            reply_markup=back_markup,
            parse_mode='Markdown'
        )
    
    elif query.data == 'interior':
        interior_images = get_interior_images()
        
        if interior_images:
            try:
                if len(interior_images) == 1:
                    with open(interior_images[0], 'rb') as photo:
                        back_button = [[InlineKeyboardButton("← Назад в главное меню", callback_data='back_to_main')]]
                        back_markup = InlineKeyboardMarkup(back_button)
                        
                        # Редактируем сообщение с фото и кнопкой "назад"
                        await context.bot.send_photo(
                            chat_id=query.message.chat_id,
                            photo=photo,
                            caption="📸 *ИНТЕРЬЕР РЕСТОРАНА «ШТАЙНДАММ, 99»*\n\nУютная атмосфера старого Кёнигсберга",
                            parse_mode='Markdown',
                            reply_markup=back_markup
                        )
                else:
                    media_group = []
                    for i, image_path in enumerate(interior_images):
                        with open(image_path, 'rb') as photo_file:
                            data = photo_file.read()
                            if i == 0:
                                media_group.append(InputMediaPhoto(
                                    media=data,
                                    caption="📸 *ИНТЕРЬЕР РЕСТОРАНА «ШТАЙНДАММ, 99»*\n\nУютная атмосфера старого Кёнигсберга",
                                    parse_mode='Markdown'
                                ))
                            else:
                                media_group.append(InputMediaPhoto(media=data))
                    
                    await context.bot.send_media_group(
                        chat_id=query.message.chat_id,
                        media=media_group
                    )
                    
                    back_button = [[InlineKeyboardButton("← Назад в главное меню", callback_data='back_to_main')]]
                    back_markup = InlineKeyboardMarkup(back_button)
                    
                    await context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text="Выберите действие:",
                        reply_markup=back_markup
                    )
                    
                    # Не удаляем исходное сообщение
                
            except Exception as e:
                logger.error(f"Ошибка при отправке фотографий интерьера: {e}")
        else:
            logger.warning("Фотографии интерьера не найдены")
    
    elif query.data == 'contacts':
        contacts_text = (
            f"📞 *КОНТАКТНАЯ ИНФОРМАЦИЯ*\n\n"
            f"📍 *Адрес:*\n{CONTACT_INFO['address']}\n\n"
            f"☎️ *Телефон:*\n{CONTACT_INFO['phone']}\n\n"
            f"🕐 *Часы работы:*\n{CONTACT_INFO['hours']}\n\n"
            f"💡 _Рекомендуем бронировать столик заранее!_"
        )
        
        keyboard = [
            [InlineKeyboardButton("📍 Построить маршрут",  url=f"{CONTACT_INFO['coordinates']}")],
            [InlineKeyboardButton("📅 Забронировать столик", url=BOOKING_URL)],
            [InlineKeyboardButton("← Назад в главное меню", callback_data='back_to_main')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=contacts_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif query.data == 'feedback':
        feedback_text = (
            "💬 *ОБРАТНАЯ СВЯЗЬ*\n\n"
            "Мы очень ценим мнение наших гостей!\n\n"
            "📝 *Как оставить отзыв:*\n"
            "• Напишите нам прямо в этот чат\n"
            "• Опишите ваши впечатления\n"
            "• Поделитесь предложениями\n\n"
            "🌟 *Что нас интересует:*\n"
            "• Качество блюд и сервиса\n"
            "• Атмосфера заведения\n"
            "• Идеи новых блюд\n"
            "• Любые пожелания\n\n"
            "_Просто напишите сообщение ниже, и мы обязательно его прочитаем!_"
        )
        
        back_button = [[InlineKeyboardButton("← Назад в главное меню", callback_data='back_to_main')]]
        back_markup = InlineKeyboardMarkup(back_button)
        
        await query.edit_message_text(
            text=feedback_text,
            reply_markup=back_markup,
            parse_mode='Markdown'
        )
    
    elif query.data == 'back_to_main':
        # Возвращаемся к главному меню
        welcome_message = (
             "👋 Добро пожаловать в *Штайндамм 99* — камерный ресторан балтийской кухни, расположенный в историческом центре Калининграда.\n\n"
        "Мы ценим локальные продукты, уважаем сезонность и вдохновляемся культурным наследием этого уникального места.\n\n"
        "📍 Используй меню ниже или кнопки, чтобы узнать больше о концепции, истории, кухне и нашем подходе."
        )
        
        keyboard = [
            [InlineKeyboardButton("📋 Меню", callback_data='menu')],
            [InlineKeyboardButton("🏛️ История района", callback_data='history'),
             InlineKeyboardButton("📸 Интерьер", callback_data='interior')],
            [InlineKeyboardButton("💡 Концепция", callback_data='concept'),
             InlineKeyboardButton("📞 Контакты", callback_data='contacts')],
            [InlineKeyboardButton("💬 Обратная связь", callback_data='feedback')],
            [InlineKeyboardButton("📅 Забронировать столик", url=BOOKING_URL)]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=welcome_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif query.data == 'concept':
        concept_text = (
            "🎯 *Концепция ресторана Штайндамм 99*\n\n"
        "Ресторан *Штайндамм 99* — это камерное гастрономическое пространство с уютной атмосферой, "
        "ограниченным количеством посадочных мест и вниманием к каждой детали. Мы создали место, где еда, история и уважение к продукту соединяются воедино.\n\n"
        "В основе концепции — *балтийская кухня*, построенная на сезонности и использовании локальных продуктов. "
        "Наши поставщики — фермерские хозяйства, сыроварни (в том числе собственная сыроварня «Кранц»), рыбаки и травники региона.\n\n"
        "Мы придерживаемся принципов устойчивого потребления: в баре используются натуральные сезонные ингредиенты для настоек и коктейлей, "
        "а винная карта отдает предпочтение российским производителям.\n\n"
        "♻️ Вдохновленные философией *Zero Waste*, мы стремимся бережно использовать ресурсы, сокращать отходы, перерабатывать и компостировать органику.\n\n"
        "Здесь каждый гость становится частью живой, развивающейся гастрономической истории Калининграда."
        )
        
        back_button = [[InlineKeyboardButton("← Назад в главное меню", callback_data='back_to_main')]]
        back_markup = InlineKeyboardMarkup(back_button)
        
        await query.edit_message_text(
            text=concept_text,
            reply_markup=back_markup,
            parse_mode='Markdown'
        )

async def feedback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Пересылает сообщение обратной связи в админский чат."""
    if update.message:
        user = update.message.from_user
        text = update.message.text
        
        feedback_message = (
            f"Сообщение от @{user.username or user.first_name} (id: {user.id}):\n\n{text}"
        )
        
        await context.bot.send_message(
            chat_id=FEEDBACK_CHAT_ID,
            text=feedback_message
        )
        
        back_button = [[InlineKeyboardButton("← Назад в главное меню", callback_data='back_to_main')]]
        back_markup = InlineKeyboardMarkup(back_button)
        
        reply_text = (
            "Спасибо за ваш отзыв! 🙏\n\n"
            "Мы очень ценим обратную связь наших гостей — она помогает нам становиться лучше.\n"
            "Если у вас есть ещё вопросы или предложения, пожалуйста, не стесняйтесь писать.\n\n"
            "Нажмите кнопку ниже, чтобы вернуться в главное меню."
        )
        
        await update.message.reply_text(reply_text, reply_markup=back_markup)
        
def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), feedback_handler))
    
    application.run_polling()

if __name__ == '__main__':
    main()
