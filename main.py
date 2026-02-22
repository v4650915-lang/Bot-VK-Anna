import sys
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.upload import VkUpload
import config
from handlers import handle_event

def main():
    print("🤖 Запуск бота типографии (v2.0 Brief)...")
    
    # Авторизация
    try:
        vk_session = vk_api.VkApi(token=config.VK_TOKEN)
        vk = vk_session.get_api()
        upload = VkUpload(vk_session) # Для загрузки картинок
        longpoll = VkBotLongPoll(vk_session, config.GROUP_ID)
        print("✅ Бот успешно подключен к ВК!")
        print(f"📩 Ожидание сообщений... (Admin ID: {config.ADMIN_ID}, Email: {config.EMAIL_RECIPIENT})")
    except Exception as e:
        print(f"❌ Ошибка авторизации: {e}")
        return

    # Основной цикл
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            # Данные сообщения в BotLongPoll хранятся в event.message
            # print(f"📨 Новое сообщение от {event.message.from_id}: {event.message.text}")
            handle_event(vk, event, upload)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем.")
