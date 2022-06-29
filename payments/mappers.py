def payment_state_mapper(state, sub_state, code):
    if state == '0':
        if sub_state == '0':
            return 'Новый'
        if sub_state == '1':
            return 'Готов к обработке'
        if sub_state == '2':
            return 'Определение провайдера'
        if sub_state == '3' or sub_state == '4':
            return 'Fraud-control'
        if sub_state == '5':
            return 'Подтверждение'
        if sub_state == '6':
            return 'Провайдер не задан'
        if sub_state == '7':
            return 'Таймаут'
        if sub_state == '8':
            return 'Отложен'
        if sub_state == '9':
            return 'Ожидает подтверждения'
        if sub_state == '11':
            return 'Вознаграждение не задано'

    if state == '10':
        return "Платеж заблокирован"

    if state == '20':
        if sub_state == '1':
            return 'Готов к списанию'
        if sub_state == '2' or sub_state == '3':
            return 'Списание средств со счета'
        if sub_state == '4':
            return 'Недостаточно средств на счете'

    if state == '30':
        if sub_state == '1':
            return 'Готов к предварительной верификации'
        if sub_state == '2':
            return 'Предварительная верификация, в обработке'
        if sub_state == '3':
            return 'Верификация закончилась неоднозначной ошибкой'
        if sub_state == '4':
            return 'Не прошла проверку модулем предварительной проверки'

    if state == '40':
        if sub_state == '1':
            return 'Готов к проведению'
        if sub_state == '2' or sub_state == '3':
            return 'Проведение'
        if sub_state in ['4', '5', '6', '7']:
            return 'Ошибка проведения'
        if sub_state == '8':
            return 'Ожидается ответ от внешнего поставщика'
        if sub_state == '9':
            return 'Ожидание подтверждения от внешней системы'

    if state == '60':
        return "Статус успешного проведения (финальный)"

    if state == '80':
        if sub_state == '0':
            if code == '0':
                return "Успех"
            if code == '-100':
                return "Дублирующиеся атрибуты переданы"
            if code == '-2':
                return "Ошибка платежного инструмента"
            if code in ['1', '2']:
                return "Неверно указан номер"
            if code == '3':
                return "Сумма вне допустимого диапазона"
            if code == '4':
                return "Сервер провайдера недоступен"
            if code == '5':
                return "Ошибка авторизации"
            if code == '6':
                return "Сервер оператора недоступен"
            if code == '7':
                return "Общая ошибка провайдера"
            if code == '8':
                return "Нехватка средств"
            if code == '9':
                return "Неверные параметры проведения"
            if code == '10':
                return "Фатальная ошибка провайдера"
            if code == '30':
                return "Недостаточно средств для добавления платежа"
            if code == '33':
                return "Сервис недоступен для данного агента"
            if code == '50':
                return "Не прошел верификацию"
            return "Не известный код"

        if sub_state in ['1', '2', '3']:
            return 'Платеж отменен вручную'
        if sub_state == '4':
            return 'Недостаточно средств на счете'
        if sub_state == '5':
            return 'Ошибка проведения'
        if sub_state in ['6', '7', '8']:
            return 'Другая ошибка'
        if sub_state == '9':
            return 'Возврат средств'

    if state == '-1':
        return "Ошибка вставки операции в БД (нефинальный)"

    if state == '-2':
        return "Платеж не найден при проверке статуса (финальный)"

    return f"Неизвестная ошибка st: {state}; subst: {sub_state}"