import ctypes
import datetime
import random
import subprocess
import webbrowser


def has_any(command, phrases):
    # проверяем, есть ли в команде хоть одна из фраз
    for phrase in phrases:
        if phrase in command:
            return True
    return False


def get_greeting():
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return 'Доброе утро!'
    elif 12 <= hour < 18:
        return 'Добрый день!'
    elif 18 <= hour < 23:
        return 'Добрый вечер!'
    else:
        return 'Доброй ночи!'


def get_time_text(command):
    now = datetime.datetime.now()
    return 'Сейчас ' + str(now.hour) + ' ' + str(now.minute).zfill(2)


def get_date_text(command):
    now = datetime.datetime.now()
    days = ['понедельник', 'вторник', 'среда', 'четверг',
            'пятница', 'суббота', 'воскресенье']
    months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля',
              'августа', 'сентября', 'октября', 'ноября', 'декабря']
    day = days[now.weekday()]
    return 'Сегодня ' + day + ', ' + str(now.day) + ' ' + months[now.month - 1]


def flip_coin(command):
    return random.choice(['Выпал орёл!', 'Выпала решка!'])


def roll_dice(command):
    return 'Выпало ' + str(random.randint(1, 6)) + '!'


def weather_stub(command):
    return 'Прогноз погоды пока не подключён, но за окном наверняка прекрасно!'


def press_key(code, times=1):
    # нажимаем и отпускаем системную клавишу (0 — нажать, 2 — отпустить)
    for _ in range(times):
        ctypes.windll.user32.keybd_event(code, 0, 0, 0)
        ctypes.windll.user32.keybd_event(code, 0, 2, 0)


def change_volume(command):
    VK_VOLUME_MUTE = 0xAD
    VK_VOLUME_DOWN = 0xAE
    VK_VOLUME_UP = 0xAF
    if has_any(command, ['громче', 'погромче', 'прибавь']):
        press_key(VK_VOLUME_UP, 5)
        return 'Сделал погромче.'
    elif has_any(command, ['тише', 'потише', 'убавь']):
        press_key(VK_VOLUME_DOWN, 5)
        return 'Сделал потише.'
    else:
        press_key(VK_VOLUME_MUTE)
        return 'Переключил звук.'


# какая опасная команда ждёт подтверждения (None — ничего не ждёт)
pending = None


def do_shutdown(command):
    global pending
    pending = 'shutdown'
    return 'Точно выключить компьютер? Скажи «да» или «нет».'


def do_reboot(command):
    global pending
    pending = 'reboot'
    return 'Точно перезагрузить компьютер? Скажи «да» или «нет».'


def cancel_shutdown(command):
    # снимаем запланированное выключение, если оно было
    try:
        subprocess.Popen('shutdown /a')
    except Exception:
        pass
    return 'Отменил выключение.'


def open_something(command):
    # смотрим, что именно просят открыть, и запускаем это
    if has_any(command, ['ютуб', 'youtube']):
        webbrowser.open('https://www.youtube.com')
        return 'Открываю Ютуб!'
    elif has_any(command, ['мтс музык', 'мтс', 'музык']):
        webbrowser.open('https://music.mts.ru/')
        return 'Открываю МТС Музыку!'
    elif has_any(command, ['браузер', 'интернет', 'гугл', 'google']):
        webbrowser.open('https://www.google.com')
        return 'Открываю браузер!'
    elif 'блокнот' in command:
        subprocess.Popen('notepad.exe')
        return 'Открываю блокнот!'
    elif 'калькулятор' in command:
        subprocess.Popen('calc.exe')
        return 'Открываю калькулятор!'
    elif 'проводник' in command:
        subprocess.Popen('explorer.exe')
        return 'Открываю проводник!'
    else:
        return 'Не понял, что нужно открыть. Я умею открывать браузер, ютуб, блокнот, калькулятор и проводник.'


# таблица команд: для каждой — какие фразы её включают и что отвечать.
# 'answers' — берём случайный ответ из списка, 'action' — вызываем функцию.
# порядок важен: берётся первая подходящая команда сверху вниз.
COMMANDS = [
    {'phrases': ['выход', 'пока', 'до свидания', 'отключись', 'спокойной ночи'],
     'answers': ['До встречи!', 'Пока-пока!',
                 'Хорошего дня, обращайся ещё!', 'До свидания!'],
     'stop': True},

    {'phrases': ['громче', 'погромче', 'тише', 'потише', 'прибавь', 'убавь', 'звук'],
     'action': change_volume},

    {'phrases': ['выключи компьютер', 'выключи комп', 'заверши работу'],
     'action': do_shutdown},

    {'phrases': ['перезагрузи', 'перезагрузка', 'ребут'],
     'action': do_reboot},

    {'phrases': ['отмена', 'не выключай', 'передумал'],
     'action': cancel_shutdown},

    {'phrases': ['открой', 'запусти', 'включи'],
     'action': open_something},

    {'phrases': ['как дела', 'как ты', 'чо как', 'че как', 'как жизнь',
                 'как настроение', 'как сам'],
     'answers': ['Отлично, работаю в штатном режиме!',
                 'Всё супер, спасибо что спросил!',
                 'Лучше всех, ведь я разговариваю с тобой!',
                 'Нормально, процессор не греется, настроение бодрое.']},

    {'phrases': ['привет', 'здравствуй', 'здорово', 'хай', 'салют',
                 'добрый день', 'доброе утро', 'добрый вечер'],
     'answers': ['Привет! Чем могу помочь?',
                 'Приветствую! Слушаю тебя.',
                 'Здравствуй! Что будем делать?',
                 'Привет-привет!']},

    {'phrases': ['время', 'который час', 'сколько времени', 'часы'],
     'action': get_time_text},

    {'phrases': ['дата', 'число', 'какой день', 'день недели',
                 'сегодня день', 'какое сегодня'],
     'action': get_date_text},

    {'phrases': ['монетк', 'орёл или решка', 'орел или решка', 'подбрось монету'],
     'action': flip_coin},

    {'phrases': ['кубик', 'кинь кости', 'брось кости'],
     'action': roll_dice},

    {'phrases': ['погода', 'прогноз погоды'],
     'action': weather_stub},

    {'phrases': ['кто ты', 'как тебя зовут', 'ты кто', 'представься',
                 'твое имя', 'твоё имя'],
     'answers': ['Я Люкс, твой голосовой помощник.',
                 'Меня зовут Люкс, я живу в твоём компьютере.',
                 'Люкс — местный голосовой помощник, к твоим услугам.']},

    {'phrases': ['помощь', 'что умеешь', 'что ты можешь', 'команды', 'помоги'],
     'answers': ['Я умею говорить время и дату, открывать браузер, ютуб, МТС Музыку, '
                 'блокнот, калькулятор и проводник, менять громкость, бросать кубик и '
                 'монетку, выключать компьютер. И просто поболтать!']},

    {'phrases': ['спасибо', 'благодарю', 'молодец'],
     'answers': ['Всегда пожалуйста!', 'Рад помочь!', 'Обращайся!']},
]


def get_answer(command):
    # возвращает ответ Люкса и флаг: работать дальше или завершаться
    global pending
    command = command.lower().strip()

    # если ждём подтверждения опасной команды — сначала разбираем ответ да/нет
    if pending is not None:
        if has_any(command, ['да', 'давай', 'подтверждаю', 'конечно', 'выключай']):
            action = pending
            pending = None
            if action == 'shutdown':
                subprocess.Popen('shutdown /s /t 30')
                return 'Выключаю компьютер через 30 секунд. Скажи «отмена», чтобы передумать.', True
            else:
                subprocess.Popen('shutdown /r /t 30')
                return 'Перезагружаю компьютер через 30 секунд. Скажи «отмена», чтобы передумать.', True
        else:
            pending = None
            return 'Хорошо, отменил.', True

    # ищем первую подходящую команду в таблице
    for cmd in COMMANDS:
        if has_any(command, cmd['phrases']):
            if 'action' in cmd:
                answer = cmd['action'](command)
            else:
                answer = random.choice(cmd['answers'])
            return answer, not cmd.get('stop', False)

    # ничего не подошло
    answer = random.choice([
        'Пока не знаю такую команду.',
        'Хм, этому меня ещё не научили.',
        'Не понял тебя, попробуй сказать по-другому.',
        'Такого я пока не умею, но обязательно научусь.',
    ])
    return answer, True
