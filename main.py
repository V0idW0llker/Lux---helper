import datetime
import random

import pyttsx3


def init_voice():
    engine = pyttsx3.init()
    engine.setProperty('rate', 180)
    # пробуем найти русский голос среди установленных в системе
    voices = engine.getProperty('voices')
    for voice in voices:
        if 'ru' in voice.id.lower() or 'russian' in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    return engine


def say(engine, text):
    print('Люкс: ' + text)
    engine.say(text)
    engine.runAndWait()


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


def get_time_text():
    now = datetime.datetime.now()
    return 'Сейчас ' + str(now.hour) + ' ' + str(now.minute).zfill(2)


def has_any(command, phrases):
    # проверяем, есть ли в команде хоть одна из фраз
    for phrase in phrases:
        if phrase in command:
            return True
    return False


def process_command(engine, command):
    # возвращаем False, если пора завершать программу
    command = command.lower().strip()

    if command == '':
        return True

    if has_any(command, ['выход', 'пока', 'до свидания', 'отключись', 'спокойной ночи']):
        say(engine, random.choice([
            'До встречи!',
            'Пока-пока!',
            'Хорошего дня, обращайся ещё!',
            'До свидания!',
        ]))
        return False
    elif has_any(command, ['как дела', 'как ты', 'чо как', 'че как', 'как жизнь', 'как настроение', 'как сам']):
        say(engine, random.choice([
            'Отлично, работаю в штатном режиме!',
            'Всё супер, спасибо что спросил!',
            'Лучше всех, ведь я разговариваю с тобой!',
            'Нормально, процессор не греется, настроение бодрое.',
        ]))
    elif has_any(command, ['привет', 'здравствуй', 'здорово', 'хай', 'ку', 'салют', 'добрый день', 'доброе утро', 'добрый вечер']):
        say(engine, random.choice([
            'Привет! Чем могу помочь?',
            'Приветствую! Слушаю тебя.',
            'Здравствуй! Что будем делать?',
            'Привет-привет!',
        ]))
    elif has_any(command, ['время', 'который час', 'сколько времени', 'часы']):
        say(engine, get_time_text())
    elif has_any(command, ['кто ты', 'как тебя зовут', 'ты кто', 'представься', 'твое имя', 'твоё имя']):
        say(engine, random.choice([
            'Я Люкс, твой голосовой помощник.',
            'Меня зовут Люкс, я живу в твоём компьютере.',
            'Люкс — местный голосовой помощник, к твоим услугам.',
        ]))
    elif has_any(command, ['помощь', 'что умеешь', 'что ты можешь', 'команды', 'помоги']):
        say(engine, 'Я умею здороваться, говорить время и отвечать на простые вопросы. Скоро научусь большему!')
    elif has_any(command, ['спасибо', 'благодарю', 'молодец']):
        say(engine, random.choice([
            'Всегда пожалуйста!',
            'Рад помочь!',
            'Обращайся!',
        ]))
    else:
        say(engine, random.choice([
            'Пока не знаю такую команду.',
            'Хм, этому меня ещё не научили.',
            'Не понял тебя, попробуй сказать по-другому.',
            'Такого я пока не умею, но обязательно научусь.',
        ]))

    return True


def main():
    engine = init_voice()
    say(engine, get_greeting())
    say(engine, 'Я Люкс, твой голосовой помощник.')

    working = True
    while working:
        command = input('Ты: ')
        working = process_command(engine, command)


if __name__ == '__main__':
    main()
