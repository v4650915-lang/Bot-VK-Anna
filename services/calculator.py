from data.prices import PRICES

def calculate_cost(item_type, quantity):
    """
    Рассчитывает стоимость заказа.
    
    :param item_type: Ключ услуги (cards, flyers, banners)
    :param quantity: Тираж (шт)
    :return: (is_success, result_message)
    """
    if item_type not in PRICES:
        return False, "Ошибка: Неизвестный тип услуги."
    
    service = PRICES[item_type]
    
    try:
        qty = int(quantity)
    except ValueError:
        return False, "Ошибка: Тираж должен быть числом."
        
    if qty < service["min_qty"]:
        return False, f"Минимальный тираж для этой услуги: {service['min_qty']} шт."
        
    # Формула: База + (Количество * Цена за шт)
    # Для баннеров логика может отличаться (считаем пока просто штуки)
    total_cost = service["base_price"] + (qty * service["price_per_item"])
    
    return True, f"💰 Стоимость заказа:\n— Услуга: {service['name']}\n— Тираж: {qty} шт.\n\nИтого: {int(total_cost)} руб."

def get_services_list():
    """Возвращает список доступных услуг для кнопок"""
    return [(key, val["name"]) for key, val in PRICES.items()]
