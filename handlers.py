import json
import vk_api
from vk_api.utils import get_random_id
import config
import keyboards
from services import storage, calculator
from data import questions

def send_message(vk, user_id, message, keyboard=None, attachment=None):
    try:
        data = {'user_id': user_id, 'message': message, 'random_id': get_random_id()}
        if keyboard: data['keyboard'] = keyboard
        if attachment: data['attachment'] = attachment
        vk.messages.send(**data)
    except Exception as e:
        print(f"Ошибка отправки сообщения: {e}")

def get_attachments_links(attachments):
    try:
        links = []
        for att in attachments:
            atype = att['type']
            if atype == 'photo':
                largest = att['photo']['sizes'][-1]
                links.append(f"📷 Фото: {largest['url']}")
            elif atype == 'doc':
                doc = att['doc']
                links.append(f"📄 Документ ({doc.get('title', 'doc')}): {doc.get('url', '')}")
            elif atype == 'wall':
                links.append(f"🔗 Пост: https://vk.com/wall{att['wall']['to_id']}_{att['wall']['id']}")
        return "\n".join(links) if links else ""
    except Exception as e:
        return "[Ошибка получения ссылок]"

def notify_admin(vk, user_id, user_data, order_type="BRIEF"):
    if order_type == "CALC":
        report = f"🛒 НОВЫЙ ЗАКАЗ (КАЛЬКУЛЯТОР) ОТ vk.com/id{user_id}\n\n"
        report += user_data.get('calc_result', '')
    else:
        report = f"📋 НОВЫЙ ЗАКАЗ ({order_type}) ОТ vk.com/id{user_id}\n\n"
        answers = user_data.get("answers", {})
        
        # Получаем правильный список вопросов для отчета
        q_list = []
        if order_type == "ВЫВЕСКИ И ФАСАДЫ": q_list = questions.SIGN_QUESTIONS
        elif order_type == "БАННЕРЫ И ПЕЧАТЬ": q_list = questions.PRINT_QUESTIONS
        elif order_type == "СУВЕНИРЫ И ПОДАРКИ": q_list = questions.SOUVENIR_QUESTIONS
        elif order_type == "МАНГАЛЫ И МЕТАЛЛ": q_list = questions.MANGAL_QUESTIONS
        elif order_type == "ПАМЯТНЫЕ ИЗДЕЛИЯ": q_list = questions.MEMORIAL_QUESTIONS
        elif order_type == "РЕЗКА И ФРЕЗЕРОВКА": q_list = questions.CUT_QUESTIONS
        
        for i, q in enumerate(q_list):
            key = q["key"]
            ans = answers.get(key, "Нет ответа")
            report += f"{i+1}️⃣ {q['text'].splitlines()[0]}\n✏️ {ans}\n\n"
            
        file_links = user_data.get("attachments_links", "")
        if file_links:
            report += f"📎 Файлы клиента:\n{file_links}\n\n"
            
        if user_data.get("design_answers"):
            report += "🎨 ДИЗАЙН-БРИФ:\n"
            d_ans = user_data.get("design_answers", {})
            for i, q in enumerate(questions.DESIGN_QUESTIONS):
                key = q["key"]
                report += f"{q['text'].splitlines()[0]}: {d_ans.get(key, 'Нет ответа')}\n"
                
    report += f"\n🔗 Ссылка на диалог: https://vk.com/gim{config.GROUP_ID}?sel={user_id}"
    
    try:
        send_message(vk, config.ADMIN_ID, f"🔔 {report}")
    except Exception as e:
        pass

def handle_event(vk, event, upload):
    try:
        msg = dict(event.obj.message)
    except:
        return

    if msg.get('out', 0) == 1:
        return

    user_id = msg.get('from_id')
    if not user_id or user_id <= 0:
        return

    text = msg.get('text', '').strip()
    attachments = msg.get('attachments', [])
    ref = msg.get('ref', '')
    payload = msg.get('payload', '')

    # Парсинг deep link ref через payload (кнопка Начать или ссылка)
    if not ref and payload:
        try:
            pl = json.loads(payload)
            if 'command' in pl and pl['command'] == 'start' and 'ref' in msg:
                pass # В старом API ref передается отдельно
            if 'ref' in pl:
                ref = pl['ref']
        except:
            pass

    user_data = storage.get_user_state(user_id)
    state = user_data["state"]

    # --- Обработка Cancel / Назад (откат на 1 шаг или в Главное меню) ---
    if text == "❌ Отмена" or text == "🔙 Назад" or text == "🔙 Главное меню":
        if state == storage.STATE_CALC_WAIT_QTY:
            storage.set_user_state(user_id, storage.STATE_MENU)
            send_message(vk, user_id, "Выберите услугу для расчета:", keyboards.get_calculator_keyboard(calculator.get_services_list()))
            return
        elif state == "DESIGN_TRANSITION":
            storage.set_user_state(user_id, storage.STATE_MENU)
            send_message(vk, user_id, "Вы вернулись в главное меню.", keyboards.get_main_keyboard())
            return
        elif any(state.startswith(pref) for pref in ["SIGN_STEP_", "PRINT_STEP_", "MANGAL_STEP_", "MEMORIAL_STEP_", "SOUVENIR_STEP_", "DESIGN_STEP_"]):
            prefix = state.split("_STEP_")[0]
            step_index = int(state.split("_STEP_")[1])
            
            if prefix == "SIGN": q_list = questions.SIGN_QUESTIONS
            elif prefix == "PRINT": q_list = questions.PRINT_QUESTIONS
            elif prefix == "MANGAL": q_list = questions.MANGAL_QUESTIONS
            elif prefix == "MEMORIAL": q_list = questions.MEMORIAL_QUESTIONS
            elif prefix == "SOUVENIR": q_list = questions.SOUVENIR_QUESTIONS
            elif prefix == "DESIGN": q_list = questions.DESIGN_QUESTIONS
            
            if step_index > 0:
                # Откат на шаг назад
                prev_step = step_index - 1
                storage.set_user_state(user_id, f"{prefix}_STEP_{prev_step}", user_data.get("data", {}))
                
                # Показываем предыдущий вопрос со стандартной кнопкой "Назад"
                # (для 4-го вопроса дизайна или конца особых брифов нужно поставить правильную клаву, но т.к. мы откатываемся
                # то это не конец. Разве что для дизайна 4 шаг, но там step_index=3, поэтому если возвращаемся на него:
                if prefix == "DESIGN" and prev_step == 3:
                     send_message(vk, user_id, q_list[prev_step]["text"], keyboards.get_mood_keyboard())
                else:
                     send_message(vk, user_id, q_list[prev_step]["text"], keyboards.get_cancel_keyboard())
                return
            else:
                # Если step_index == 0, возвращаемся в меню (или в конец основного брифа, если это был дизайн-бриф)
                if prefix == "DESIGN":
                    # Возврат на развилку
                    storage.set_user_state(user_id, "DESIGN_TRANSITION", user_data.get("data", {}))
                    send_message(vk, user_id, "Возврат к вопросу о дизайне макета.", keyboards.get_design_transition_keyboard())
                else:
                    storage.set_user_state(user_id, storage.STATE_MENU)
                    send_message(vk, user_id, "Вы вернулись в главное меню.", keyboards.get_main_keyboard())
                return
                
        # Если прочие состояния, просто сброс в главное меню
        storage.set_user_state(user_id, storage.STATE_MENU)
        send_message(vk, user_id, "Вы вернулись в главное меню.", keyboards.get_main_keyboard())
        return

    # --- Обработка Deep Links ---
    branch_map = {
        "sign": ("SIGN_STEP_0", questions.SIGN_QUESTIONS[0]["text"], keyboards.get_cancel_keyboard()),
        "banner": ("PRINT_STEP_0", questions.PRINT_QUESTIONS[0]["text"], keyboards.get_cancel_keyboard()),
        "mangal": ("MANGAL_STEP_0", questions.MANGAL_QUESTIONS[0]["text"], keyboards.get_cancel_keyboard()),
        "memorial": ("MEMORIAL_STEP_0", questions.MEMORIAL_QUESTIONS[0]["text"], keyboards.get_cancel_keyboard()),
        "souvenir": ("SOUVENIR_STEP_0", questions.SOUVENIR_QUESTIONS[0]["text"], keyboards.get_cancel_keyboard()),
        "calc": (storage.STATE_MENU, "Выберите услугу для расчета:", keyboards.get_calculator_keyboard(calculator.get_services_list()))
    }
    
    if ref in branch_map:
        new_st, reply, kb = branch_map[ref]
        storage.set_user_state(user_id, new_st)
        send_message(vk, user_id, reply, kb)
        return

    # --- Логика Приветствия ---
    if state == storage.STATE_WELCOME:
        if "Выбрать из меню" in text or "Да, знаю что хочу" in text or "Оформить заявку" in text:
            storage.set_user_state(user_id, storage.STATE_MENU)
            send_message(vk, user_id, "Выберите, что вас интересует 👇", keyboards.get_main_keyboard())
        else:
            # Любое другое сообщение - показываем приветствие
            storage.set_user_state(user_id, storage.STATE_WELCOME)
            welcome_text = (
                "Привет! 👋 Я помогу рассчитать стоимость или оформить заявку на вывески, баннеры и металлоизделия.\n\n"
                "🚀 Открыть наше приложение с примерами и актуальными прайсами можно по этой безопасной ссылке:\n"
                "👉 https://tehnologiya-nv.duckdns.org/\n\n"
                "После просмотра вы можете перейти к заказу, нажав кнопку ниже:"
            )
            send_message(vk, user_id, welcome_text, keyboards.get_welcome_keyboard())


    # --- Логика ГЛАВНОГО МЕНЮ ---
    elif state == storage.STATE_MENU:
        if text == "🪧 Вывески и фасады":
            storage.set_user_state(user_id, "SIGN_STEP_0")
            send_message(vk, user_id, questions.SIGN_QUESTIONS[0]["text"], keyboards.get_cancel_keyboard())
        elif text == "🖨 Баннеры и печать":
            storage.set_user_state(user_id, "PRINT_STEP_0")
            send_message(vk, user_id, questions.PRINT_QUESTIONS[0]["text"], keyboards.get_cancel_keyboard())
        elif text == "🔥 Мангалы и металл":
            storage.set_user_state(user_id, "MANGAL_STEP_0")
            send_message(vk, user_id, questions.MANGAL_QUESTIONS[0]["text"], keyboards.get_cancel_keyboard())
        elif text == "🌸 Памятные изделия":
            storage.set_user_state(user_id, "MEMORIAL_STEP_0")
            send_message(vk, user_id, questions.MEMORIAL_QUESTIONS[0]["text"], keyboards.get_cancel_keyboard())
        elif text == "🎁 Сувениры и подарки":
            storage.set_user_state(user_id, "SOUVENIR_STEP_0")
            send_message(vk, user_id, questions.SOUVENIR_QUESTIONS[0]["text"], keyboards.get_cancel_keyboard())
        elif text == "🧮 Быстрый расчёт":
            send_message(vk, user_id, "Выберите услугу для расчета:", keyboards.get_calculator_keyboard(calculator.get_services_list()))
        elif text == "📍 Адрес":
            send_message(vk, user_id, config.CONTACTS_INFO, keyboards.get_main_keyboard())
        else:
            # Чекнем, может это выбор в калькуляторе
            found_service = None
            for key, val in calculator.PRICES.items():
                if val['name'] == text:
                    found_service = key
                    break
            
            if found_service:
                storage.set_user_state(user_id, storage.STATE_CALC_WAIT_QTY, {"item": found_service})
                send_message(vk, user_id, f"Вы выбрана услуга: {text}.\nВведите тираж (количество):", keyboards.get_cancel_keyboard())
            else:
                # Если ерунда
                storage.set_user_state(user_id, storage.STATE_WELCOME)
                welcome_text = (
                    "Привет! 👋 Я помогу рассчитать стоимость или оформить заявку на вывески, баннеры и металлоизделия.\n\n"
                    "🚀 Открыть наше приложение с примерами и актуальными прайсами можно по этой безопасной ссылке:\n"
                    "👉 https://tehnologiya-nv.duckdns.org/\n\n"
                    "После просмотра вы можете перейти к заказу, нажав кнопку ниже:"
                )
                send_message(vk, user_id, welcome_text, keyboards.get_welcome_keyboard())
                
    # --- Логика Калькулятора ---
    elif state == storage.STATE_CALC_WAIT_QTY:
        item_key = user_data["data"]["item"]
        success, result = calculator.calculate_cost(item_key, text)
        if success:
            send_message(vk, user_id, result)
            send_message(vk, user_id, "Хотите посчитать что-то ещё?", keyboards.get_calc_result_keyboard())
            storage.set_user_state(user_id, "CALC_FINISHED", {"calc_result": result})
        else:
            send_message(vk, user_id, f"{result}\nПожалуйста, введите корректное число или нажмите «Отмена».", keyboards.get_cancel_keyboard())

    elif state == "CALC_FINISHED":
        if text == "🔄 Считать ещё":
             storage.set_user_state(user_id, storage.STATE_MENU)
             send_message(vk, user_id, "Выберите услугу для расчета:", keyboards.get_calculator_keyboard(calculator.get_services_list()))
        elif text == "📋 Оформить заявку":
             storage.set_user_state(user_id, storage.STATE_MENU)
             send_message(vk, user_id, "Выберите, что вас интересует 👇", keyboards.get_main_keyboard())
        else:
             notify_admin(vk, user_id, user_data.get("data", {}), order_type="CALC")
             storage.clear_user_state(user_id)
             handle_event(vk, event, upload) # Рекурсия для обработки как в WELCOME

    # --- Поддержка Transition для Design Брифа ---
    elif state == "DESIGN_TRANSITION":
        if text == "▶️ Заполнить бриф":
            storage.set_user_state(user_id, "DESIGN_STEP_0", user_data["data"])
            send_message(vk, user_id, questions.DESIGN_QUESTIONS[0]["text"], keyboards.get_cancel_keyboard())
        elif text == "⏩ Пропустить, менеджер уточнит":
            order_type = user_data["data"].get("order_type_name", "UNKNOWN")
            notify_admin(vk, user_id, user_data["data"], order_type=order_type)
            msg = "✅ Заявка принята!\n\nМенеджер уже получил вашу заявку и скоро выйдет на связь.\nОбычно отвечаем в течение 1 часа в рабочее время ⏱"
            send_message(vk, user_id, msg, keyboards.get_finish_keyboard())
            storage.set_user_state(user_id, "FINISH_SCREEN")
        else:
            send_message(vk, user_id, "Пожалуйста, ответьте на вопрос выше или нажмите 🔙 Главное меню", keyboards.get_design_transition_keyboard())

    # --- FINISH SCREEN (кнопки Заказать еще и Адрес) ---
    elif state == "FINISH_SCREEN":
        if text == "🔄 Заказать ещё":
            storage.set_user_state(user_id, storage.STATE_MENU)
            send_message(vk, user_id, "Выберите, что вас интересует 👇", keyboards.get_main_keyboard())
        elif text == "📍 Адрес и контакты":
            send_message(vk, user_id, config.CONTACTS_INFO, keyboards.get_finish_keyboard())
        else:
            storage.set_user_state(user_id, storage.STATE_WELCOME)
            handle_event(vk, event, upload)

    # --- Универсальная логика FSM для Брифов ---
    elif any(state.startswith(pref) for pref in ["SIGN_STEP_", "PRINT_STEP_", "MANGAL_STEP_", "MEMORIAL_STEP_", "SOUVENIR_STEP_", "DESIGN_STEP_"]):
        prefix = state.split("_STEP_")[0]
        step_index = int(state.split("_STEP_")[1])
        
        # Определяем ветку
        if prefix == "SIGN":
            q_list = questions.SIGN_QUESTIONS
            order_type = "ВЫВЕСКИ И ФАСАДЫ"
        elif prefix == "PRINT":
            q_list = questions.PRINT_QUESTIONS
            order_type = "БАННЕРЫ И ПЕЧАТЬ"
        elif prefix == "MANGAL":
            q_list = questions.MANGAL_QUESTIONS
            order_type = "МАНГАЛЫ И МЕТАЛЛ"
        elif prefix == "MEMORIAL":
            q_list = questions.MEMORIAL_QUESTIONS
            order_type = "ПАМЯТНЫЕ ИЗДЕЛИЯ"
        elif prefix == "SOUVENIR":
            q_list = questions.SOUVENIR_QUESTIONS
            order_type = "СУВЕНИРЫ И ПОДАРКИ"
        elif prefix == "DESIGN":
            q_list = questions.DESIGN_QUESTIONS
            order_type = user_data["data"].get("order_type_name", "ДИЗАЙН")
            
        current_key = q_list[step_index]["key"]
        
        ans_text = text
        if attachments:
            links = get_attachments_links(attachments)
            if links:
                ans_text += f"\n📎 Вложения:\n{links}"
            
        # Инициализируем хранилище
        if "data" not in user_data: user_data["data"] = {}
        
        if prefix == "DESIGN":
            if "design_answers" not in user_data["data"]: user_data["data"]["design_answers"] = {}
            user_data["data"]["design_answers"][current_key] = ans_text
            storage.update_user_data(user_id, "design_answers", user_data["data"]["design_answers"])
        else:
            if "answers" not in user_data["data"]: user_data["data"]["answers"] = {}
            user_data["data"]["answers"][current_key] = ans_text
            storage.update_user_data(user_id, "answers", user_data["data"]["answers"])
            storage.update_user_data(user_id, "order_type_name", order_type)
            
            # Собираем все ссылки из всех ответов (если нужно)
            if attachments:
                exist_links = user_data["data"].get("attachments_links", "")
                exist_links += get_attachments_links(attachments) + "\n"
                storage.update_user_data(user_id, "attachments_links", exist_links)
        
        next_step = step_index + 1
        
        if next_step < len(q_list):
            next_q = q_list[next_step]
            storage.set_user_state(user_id, f"{prefix}_STEP_{next_step}", user_data["data"])
            
            # Определяем, какую клаву послать на следующий вопрос
            if next_step == len(q_list) - 1: # если следующий вопрос - последний
                if prefix in ["SIGN", "SOUVENIR"]:
                    send_message(vk, user_id, next_q["text"], keyboards.get_design_need_keyboard())
                elif prefix == "MEMORIAL":
                    send_message(vk, user_id, next_q["text"], keyboards.get_delivery_keyboard())
                else:
                    send_message(vk, user_id, next_q["text"], keyboards.get_cancel_keyboard())
            else:
                if prefix == "DESIGN" and next_step == 3: # 4й вопрос (Mood)
                    send_message(vk, user_id, next_q["text"], keyboards.get_mood_keyboard())
                else:
                    send_message(vk, user_id, next_q["text"], keyboards.get_cancel_keyboard())
        else:
            # Бриф окончен
            # Проверяем, нужно ли предложить дизайн бриф
            if prefix in ["SIGN", "SOUVENIR"] and text == "🎨 Нет макета, нужен дизайн":
                # Переход к дизайн брифу
                storage.set_user_state(user_id, "DESIGN_TRANSITION", user_data["data"])
                msg = "Отлично! Наш дизайнер поможет создать макет 🎨\nЗаполните короткий дизайн-бриф — займёт 3–4 минуты."
                send_message(vk, user_id, msg, keyboards.get_design_transition_keyboard())
            else:
                # Финал
                notify_admin(vk, user_id, user_data["data"], order_type=order_type)
                msg = "✅ Заявка принята!\n\nМенеджер уже получил вашу заявку и скоро выйдет на связь.\nОбычно отвечаем в течение 1 часа в рабочее время ⏱"
                send_message(vk, user_id, msg, keyboards.get_finish_keyboard())
                storage.set_user_state(user_id, "FINISH_SCREEN")

    # --- Если стейта нет (fallback), идем в Welcome ---
    else:
        storage.set_user_state(user_id, storage.STATE_WELCOME)
        welcome_text = (
            "Привет! 👋 Я помогу рассчитать стоимость или оформить заявку на вывески, баннеры и металлоизделия.\n\n"
            "🚀 Открыть наше приложение с примерами и актуальными прайсами можно по этой безопасной ссылке:\n"
            "👉 https://tehnologiya-nv.duckdns.org/\n\n"
            "После просмотра вы можете перейти к заказу, нажав кнопку ниже:"
        )
        send_message(vk, user_id, welcome_text, keyboards.get_welcome_keyboard())
