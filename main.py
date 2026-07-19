import datetime
import random
import threading
import tkinter as tk

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


def speak(engine, text):
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


def get_answer(command):
    # возвращает ответ Люкса и флаг: работать дальше или завершаться
    command = command.lower().strip()

    if has_any(command, ['выход', 'пока', 'до свидания', 'отключись', 'спокойной ночи']):
        answer = random.choice([
            'До встречи!',
            'Пока-пока!',
            'Хорошего дня, обращайся ещё!',
            'До свидания!',
        ])
        return answer, False
    elif has_any(command, ['как дела', 'как ты', 'чо как', 'че как', 'как жизнь', 'как настроение', 'как сам']):
        answer = random.choice([
            'Отлично, работаю в штатном режиме!',
            'Всё супер, спасибо что спросил!',
            'Лучше всех, ведь я разговариваю с тобой!',
            'Нормально, процессор не греется, настроение бодрое.',
        ])
    elif has_any(command, ['привет', 'здравствуй', 'здорово', 'хай', 'ку', 'салют', 'добрый день', 'доброе утро', 'добрый вечер']):
        answer = random.choice([
            'Привет! Чем могу помочь?',
            'Приветствую! Слушаю тебя.',
            'Здравствуй! Что будем делать?',
            'Привет-привет!',
        ])
    elif has_any(command, ['время', 'который час', 'сколько времени', 'часы']):
        answer = get_time_text()
    elif has_any(command, ['кто ты', 'как тебя зовут', 'ты кто', 'представься', 'твое имя', 'твоё имя']):
        answer = random.choice([
            'Я Люкс, твой голосовой помощник.',
            'Меня зовут Люкс, я живу в твоём компьютере.',
            'Люкс — местный голосовой помощник, к твоим услугам.',
        ])
    elif has_any(command, ['помощь', 'что умеешь', 'что ты можешь', 'команды', 'помоги']):
        answer = 'Я умею здороваться, говорить время и отвечать на простые вопросы. Скоро научусь большему!'
    elif has_any(command, ['спасибо', 'благодарю', 'молодец']):
        answer = random.choice([
            'Всегда пожалуйста!',
            'Рад помочь!',
            'Обращайся!',
        ])
    else:
        answer = random.choice([
            'Пока не знаю такую команду.',
            'Хм, этому меня ещё не научили.',
            'Не понял тебя, попробуй сказать по-другому.',
            'Такого я пока не умею, но обязательно научусь.',
        ])

    return answer, True


def main():
    engine = init_voice()

    root = tk.Tk()
    root.title('Люкс — голосовой помощник')
    root.geometry('520x420')

    chat = tk.Text(root, state='disabled', wrap='word', font=('Segoe UI', 11))
    chat.pack(fill='both', expand=True, padx=10, pady=(10, 5))

    bottom = tk.Frame(root)
    bottom.pack(fill='x', padx=10, pady=(0, 10))

    entry = tk.Entry(bottom, font=('Segoe UI', 11))
    entry.pack(side='left', fill='x', expand=True, ipady=4)
    entry.focus()

    def add_message(author, text):
        chat.config(state='normal')
        chat.insert('end', author + ': ' + text + '\n')
        chat.config(state='disabled')
        chat.see('end')

    def lux_say(text):
        add_message('Люкс', text)
        # озвучиваем в отдельном потоке, чтобы окно не зависало
        threading.Thread(target=speak, args=(engine, text), daemon=True).start()

    def on_send(event=None):
        command = entry.get().strip()
        if command == '':
            return
        entry.delete(0, 'end')
        add_message('Ты', command)
        answer, working = get_answer(command)
        lux_say(answer)
        if not working:
            # даём договорить и закрываем окно
            root.after(2000, root.destroy)

    send_button = tk.Button(bottom, text='Отправить', command=on_send)
    send_button.pack(side='left', padx=(5, 0))

    root.bind('<Return>', on_send)

    lux_say(get_greeting())
    lux_say('Я Люкс, твой голосовой помощник.')

    root.mainloop()


if __name__ == '__main__':
    main()
