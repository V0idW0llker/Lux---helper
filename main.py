import datetime
import random
import subprocess
import threading
import tkinter as tk
import webbrowser

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


def open_something(command):
    # смотрим, что именно просят открыть, и запускаем это
    if has_any(command, ['ютуб', 'youtube']):
        webbrowser.open('https://www.youtube.com')
        return 'Открываю Ютуб!'
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
    elif has_any(command, ['открой', 'запусти', 'включи']):
        answer = open_something(command)
    elif has_any(command, ['как дела', 'как ты', 'чо как', 'че как', 'как жизнь', 'как настроение', 'как сам']):
        answer = random.choice([
            'Отлично, работаю в штатном режиме!',
            'Всё супер, спасибо что спросил!',
            'Лучше всех, ведь я разговариваю с тобой!',
            'Нормально, процессор не греется, настроение бодрое.',
        ])
    elif has_any(command, ['привет', 'здравствуй', 'здорово', 'хай', 'салют', 'добрый день', 'доброе утро', 'добрый вечер']):
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
        answer = 'Я умею говорить время, открывать браузер, ютуб, блокнот, калькулятор и проводник. И просто поболтать!'
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


BG_COLOR = '#141420'
USER_BUBBLE = '#4c6ef5'
LUX_BUBBLE = '#26263a'
TEXT_COLOR = '#e8e8f0'

# задержка перед ответом и скорость печати (в миллисекундах)
ANSWER_DELAY = 200
TYPE_SPEED = 25


def main():
    engine = init_voice()

    root = tk.Tk()
    root.title('Люкс')
    root.geometry('420x560')
    root.configure(bg=BG_COLOR)
    root.minsize(320, 400)

    chat = tk.Text(root, state='disabled', wrap='word', font=('Segoe UI', 11),
                   bg=BG_COLOR, fg=TEXT_COLOR, bd=0, highlightthickness=0,
                   padx=14, pady=10, cursor='arrow')
    chat.pack(fill='both', expand=True)

    # стили сообщений: свои — справа синим, Люкса — слева серым
    chat.tag_config('user', justify='right', background=USER_BUBBLE,
                    foreground='white', lmargin1=80, lmargin2=80, rmargin=6,
                    spacing1=4, spacing3=10)
    chat.tag_config('lux', justify='left', background=LUX_BUBBLE,
                    foreground=TEXT_COLOR, lmargin1=6, lmargin2=6, rmargin=80,
                    spacing1=4, spacing3=10)

    bottom = tk.Frame(root, bg=BG_COLOR)
    bottom.pack(fill='x', padx=12, pady=12)

    entry = tk.Entry(bottom, font=('Segoe UI', 11), bg=LUX_BUBBLE, fg=TEXT_COLOR,
                     bd=0, insertbackground=TEXT_COLOR,
                     highlightthickness=1, highlightbackground='#33334d',
                     highlightcolor=USER_BUBBLE)
    entry.pack(fill='x', ipady=8, ipadx=8)
    entry.focus()

    def add_message(author, text):
        chat.config(state='normal')
        chat.insert('end', ' ' + text + ' \n', author)
        chat.config(state='disabled')
        chat.see('end')

    is_typing = False

    def type_char(text, i):
        nonlocal is_typing
        chat.config(state='normal')
        if i < len(text):
            chat.insert('end', text[i], 'lux')
            chat.config(state='disabled')
            chat.see('end')
            root.after(TYPE_SPEED, type_char, text, i + 1)
        else:
            chat.insert('end', ' \n', 'lux')
            chat.config(state='disabled')
            chat.see('end')
            is_typing = False

    def lux_say(text):
        nonlocal is_typing
        is_typing = True
        # озвучиваем в отдельном потоке, чтобы окно не зависало
        threading.Thread(target=speak, args=(engine, text), daemon=True).start()
        chat.config(state='normal')
        chat.insert('end', ' ', 'lux')
        chat.config(state='disabled')
        root.after(ANSWER_DELAY, type_char, text, 0)

    def on_send(event=None):
        # пока Люкс печатает, новые сообщения не отправляем
        if is_typing:
            return
        command = entry.get().strip()
        if command == '':
            return
        entry.delete(0, 'end')
        add_message('user', command)
        answer, working = get_answer(command)
        lux_say(answer)
        if not working:
            # даём допечатать и договорить, потом закрываем окно
            root.after(2500, root.destroy)

    entry.bind('<Return>', on_send)

    lux_say(get_greeting() + ' Я Люкс, твой голосовой помощник.')

    root.mainloop()


if __name__ == '__main__':
    main()
