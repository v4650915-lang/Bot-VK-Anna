# Простой модуль версионности состояний in-memory
# В реальном продакшене лучше использовать Redis или Базу Данных

# Состояния
STATE_WELCOME = "WELCOME"
STATE_MENU = "MENU"

# Калькулятор
STATE_CALC_WAIT_QTY = "CALC_WAIT_QTY"

# Заказ
STATE_ORDER_WAIT_NAME = "ORDER_WAIT_NAME"
STATE_ORDER_WAIT_PHONE = "ORDER_WAIT_PHONE"
STATE_ORDER_WAIT_FILE = "ORDER_WAIT_FILE"

# Хранилище: {user_id: {"state": "...", "data": {...}}}
_storage = {}

def get_user_state(user_id):
    return _storage.get(user_id, {"state": STATE_WELCOME, "data": {}})

def set_user_state(user_id, state, data=None):
    if data is None:
        data = {}
    _storage[user_id] = {"state": state, "data": data}

def update_user_data(user_id, key, value):
    if user_id not in _storage:
        _storage[user_id] = {"state": STATE_WELCOME, "data": {}}
    _storage[user_id]["data"][key] = value

def clear_user_state(user_id):
    if user_id in _storage:
        del _storage[user_id]
