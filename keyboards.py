from vk_api.keyboard import VkKeyboard, VkKeyboardColor

def get_welcome_keyboard():
    """Клавиатура шага 1: Приветствие (Inline с ссылкой)"""
    keyboard = VkKeyboard(inline=True)
    keyboard.add_button("📋 Выбрать из меню / Оформить заявку", color=VkKeyboardColor.POSITIVE)
    return keyboard.get_keyboard()

def get_main_keyboard():
    """Главное меню (Шаг 2)"""
    keyboard = VkKeyboard(one_time=False)
    
    keyboard.add_button("🪧 Вывески и фасады", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("🖨 Баннеры и печать", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    
    keyboard.add_button("🔥 Мангалы и металл", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("🌸 Памятные изделия", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    
    keyboard.add_button("🎁 Сувениры и подарки", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    
    keyboard.add_button("🧮 Быстрый расчёт", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("📍 Адрес", color=VkKeyboardColor.SECONDARY)
    
    return keyboard.get_keyboard()

def get_design_need_keyboard():
    """Шаг 3 брифов Вывески / Сувениры (Вопрос про макет)"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("🎨 Нет макета, нужен дизайн", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("🔙 Назад", color=VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()

def get_delivery_keyboard():
    """Шаг 3 брифа Памятные изделия"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("🚚 Доставка", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("🏪 Самовывоз", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("✍️ Уточним позже", color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button("🔙 Назад", color=VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()

def get_design_transition_keyboard():
    """Переход к дизайн-брифу"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("▶️ Заполнить бриф", color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button("⏩ Пропустить, менеджер уточнит", color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button("🔙 Главное меню", color=VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()

def get_mood_keyboard():
    """Вопрос 4 в дизайн-брифе"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("⚡ Энергия", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("🏆 Профессионализм", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("☀️ Уют", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("✍️ Своё", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("🔙 Назад", color=VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()

def get_calculator_keyboard(services):
    """Меню выбора услуг для калькулятора"""
    keyboard = VkKeyboard(one_time=False)
    
    for i, (key, name) in enumerate(services):
        if i > 0 and i % 2 == 0:
            keyboard.add_line()
        keyboard.add_button(name, color=VkKeyboardColor.PRIMARY, payload={"type": "calc_service", "item": key})
        
    keyboard.add_line()
    keyboard.add_button("🔙 Назад", color=VkKeyboardColor.NEGATIVE)
    
    return keyboard.get_keyboard()

def get_calc_result_keyboard():
    """Кнопки после завершения калькулятора"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("🔄 Считать ещё", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("📋 Оформить заявку", color=VkKeyboardColor.POSITIVE)
    return keyboard.get_keyboard()

def get_cancel_keyboard():
    """Кнопка отмены для сценариев"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("🔙 Назад", color=VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()

def get_back_keyboard():
    """Кнопка назад"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("🔙 Назад", color=VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()

def get_finish_keyboard():
    """Клавиатура завершения диалога"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("🔄 Заказать ещё", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("📍 Адрес и контакты", color=VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()

