import os
import queue
import threading
import tkinter as tk

import pyttsx3
from PIL import Image, ImageTk

from commands import get_answer, get_greeting


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


def start_voice_worker():
    # фразы говорит отдельный поток, забирая их из очереди по порядку.
    # Движок создаём заново на каждую фразу: у pyttsx3 на Windows есть баг —
    # если пользоваться одним движком, звук пропадает после первой фразы,
    # хотя ошибок нет. Со свежим движком озвучивается всё.
    say_queue = queue.Queue()

    def worker():
        while True:
            text = say_queue.get()
            try:
                engine = init_voice()
                engine.say(for_speech(text))
                engine.runAndWait()
                engine.stop()
                del engine
            except Exception:
                pass

    threading.Thread(target=worker, daemon=True).start()
    return say_queue


def for_speech(text):
    # правим слова, которые синтезатор читает не так, как пишется
    return text.replace('помощник', 'помошник')


BG_COLOR = '#141420'
USER_BUBBLE = '#4c6ef5'
LUX_BUBBLE = '#26263a'
TEXT_COLOR = '#e8e8f0'

# сейчас тема одна — тёмная. В будущем будут светлая и цветные,
# логотипы под них назовём с суффиксом цвета: logo_dark.png, logo_light.png и т.д.
THEME = 'dark'

# желаемая высота логотипа-надписи в шапке (в пикселях)
LOGO_HEIGHT = 56


def load_logo(path, height):
    # обрезаем пустые поля вокруг рисунка и масштабируем до нужной высоты
    img = Image.open(path).convert('RGBA')
    gray = img.convert('L')
    bg = gray.getpixel((2, 2))  # цвет фона берём из угла
    # маска: где картинка заметно отличается от фона — это и есть логотип
    mask = gray.point(lambda p: 255 if abs(p - bg) > 40 else 0)
    box = mask.getbbox()
    if box:
        img = img.crop(box)
    ratio = height / img.height
    img = img.resize((int(img.width * ratio), height), Image.LANCZOS)
    return ImageTk.PhotoImage(img)


def set_taskbar_icon(root, ico_path):
    # панель задач берёт иконку не через iconbitmap, а через WM_SETICON —
    # шлём картинку прямо хэндлу окна
    import ctypes
    user32 = ctypes.windll.user32
    IMAGE_ICON = 1
    LR_LOADFROMFILE = 0x00000010
    WM_SETICON = 0x0080
    ICON_SMALL, ICON_BIG = 0, 1
    hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
    for size, which in ((16, ICON_SMALL), (32, ICON_BIG)):
        hicon = user32.LoadImageW(None, ico_path, IMAGE_ICON, size, size,
                                  LR_LOADFROMFILE)
        if hicon:
            user32.SendMessageW(hwnd, WM_SETICON, which, hicon)

# задержка перед ответом и пауза между буквами при печати (в миллисекундах)
ANSWER_DELAY = 200
TYPE_SPEED = 55


def main():
    say_queue = start_voice_worker()

    # говорим Windows, что мы отдельное приложение, а не python.exe,
    # иначе на панели задач будет иконка питона вместо нашей
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('lux.assistant')
    except Exception:
        pass

    root = tk.Tk()
    root.title('Люкс')
    root.geometry('420x560')
    root.configure(bg=BG_COLOR)
    root.minsize(320, 400)

    assets = os.path.join(os.path.dirname(__file__), 'assets')

    # значок приложения: Windows для панели задач хочет .ico, поэтому делаем
    # его из png один раз и сохраняем рядом
    icon_path = os.path.join(assets, 'Logo_' + THEME + '.png')
    if os.path.exists(icon_path):
        try:
            ico_path = os.path.join(assets, 'Logo_' + THEME + '.ico')
            src = Image.open(icon_path).convert('RGBA')
            # логотип занимает лишь малую часть картинки, а вокруг прозрачно —
            # сначала обрезаем до самого рисунка, иначе в иконке он будет крохотным
            box = src.split()[3].getbbox()
            if box:
                src = src.crop(box)
            # затем вписываем в квадрат с небольшим полем: Windows показывает
            # только строго квадратные иконки (16x16, 32x32 и т.д.)
            side = int(max(src.size) * 1.1)
            square = Image.new('RGBA', (side, side), (0, 0, 0, 0))
            square.paste(src, ((side - src.width) // 2, (side - src.height) // 2))
            square.save(ico_path, sizes=[(16, 16), (32, 32), (48, 48), (256, 256)])
            root.iconbitmap(default=ico_path)
            # окно должно быть создано, поэтому иконку панели задач ставим чуть позже
            root.after(100, lambda: set_taskbar_icon(root, ico_path))
        except Exception:
            root.iconphoto(True, tk.PhotoImage(file=icon_path))

    # шапка: логотип с названием вместо обычного текста
    header = tk.Frame(root, bg=BG_COLOR)
    header.pack(fill='x', padx=14, pady=(12, 4))

    header_path = os.path.join(assets, 'LogoName_' + THEME + '.png')
    if os.path.exists(header_path):
        header_logo = load_logo(header_path, LOGO_HEIGHT)
        title = tk.Label(header, image=header_logo, bg=BG_COLOR)
        title.image = header_logo  # держим ссылку, иначе картинку съест сборщик мусора
    else:
        title = tk.Label(header, text='Люкс', font=('Segoe UI', 14, 'bold'),
                         bg=BG_COLOR, fg=TEXT_COLOR)
    title.pack(side='left')

    # поле ввода закрепляем за низом окна ДО чата, иначе при маленьком окне
    # чат разрастается и выталкивает поле ввода за край
    bottom = tk.Frame(root, bg=BG_COLOR)
    bottom.pack(side='bottom', fill='x', padx=12, pady=12)

    entry = tk.Entry(bottom, font=('Segoe UI', 11), bg=LUX_BUBBLE, fg=TEXT_COLOR,
                     bd=0, insertbackground=TEXT_COLOR,
                     highlightthickness=1, highlightbackground='#33334d',
                     highlightcolor=USER_BUBBLE)
    entry.pack(fill='x', ipady=8, ipadx=8)
    entry.focus()

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
    # ещё не напечатанные буквы красим в цвет пузырька — они занимают место,
    # но не видны, поэтому текст не прыгает при переносе строки
    chat.tag_config('hidden', foreground=LUX_BUBBLE)
    chat.tag_raise('hidden')

    def add_message(author, text):
        chat.config(state='normal')
        chat.insert('end', ' ' + text + ' \n', author)
        chat.config(state='disabled')
        chat.see('end')

    is_typing = False
    # данные текущей печати, чтобы можно было мгновенно её допечатать
    typing_job = {'after': None, 'start': None, 'n': 0}

    def finish_typing():
        # сразу показываем весь текущий ответ и снимаем блокировку
        nonlocal is_typing
        if typing_job['after'] is not None:
            root.after_cancel(typing_job['after'])
            typing_job['after'] = None
        if typing_job['start'] is not None:
            chat.config(state='normal')
            end = typing_job['start'] + '+%dc' % typing_job['n']
            chat.tag_remove('hidden', typing_job['start'], end)
            chat.config(state='disabled')
            chat.see('end')
        is_typing = False

    def reveal_char(start, i, n):
        # открываем по одной букве: снимаем с неё тег hidden, и она становится
        # видимой. Текст вставлен целиком заранее, поэтому перенос строк уже
        # посчитан и ничего не прыгает — получается плавная печать по буквам
        nonlocal is_typing
        if i < n:
            chat.config(state='normal')
            here = start + '+%dc' % i
            chat.tag_remove('hidden', here, here + '+1c')
            chat.config(state='disabled')
            chat.see('end')
            typing_job['after'] = root.after(TYPE_SPEED, reveal_char, start, i + 1, n)
        else:
            typing_job['after'] = None
            is_typing = False

    def lux_say(text):
        nonlocal is_typing
        is_typing = True
        # кладём фразу в очередь озвучки — говорит постоянный поток
        say_queue.put(text)
        chat.config(state='normal')
        start = chat.index('end-1c')
        chat.insert('end', ' ' + text + ' \n', ('lux', 'hidden'))
        chat.config(state='disabled')
        chat.see('end')
        # открываем начиная с первой буквы текста (пропускаем ведущий пробел)
        text_start = start + '+1c'
        typing_job['start'] = text_start
        typing_job['n'] = len(text)
        typing_job['after'] = root.after(ANSWER_DELAY, reveal_char, text_start, 0, len(text))

    def on_send(event=None):
        # если Люкс ещё печатает — мгновенно допечатываем прошлый ответ,
        # чтобы новая команда не терялась, и продолжаем
        if is_typing:
            finish_typing()
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
