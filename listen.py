import sounddevice as sd
import speech_recognition as sr

SAMPLE_RATE = 16000  # частота записи, которую хорошо понимает распознавание

# текущий поток записи и накопленные куски звука
stream = None
chunks = []


def start_recording():
    # включаем микрофон: звук копится кусками в списке, пока не остановим.
    # возвращаем False, если микрофон не удалось открыть
    global stream, chunks
    chunks = []

    def callback(indata, frames, time, status):
        chunks.append(bytes(indata))

    try:
        stream = sd.RawInputStream(samplerate=SAMPLE_RATE, channels=1,
                                   dtype='int16', callback=callback)
        stream.start()
        return True
    except Exception:
        stream = None
        return False


def stop_and_recognize():
    # останавливаем запись и отдаём звук на распознавание.
    # '' — ничего не расслышали, None — ошибка (нет интернета или микрофона)
    global stream
    if stream is None:
        return None
    try:
        stream.stop()
        stream.close()
    except Exception:
        pass
    stream = None

    data = b''.join(chunks)
    # короче полсекунды — просто случайный клик по кнопке
    if len(data) < SAMPLE_RATE:
        return ''

    audio = sr.AudioData(data, SAMPLE_RATE, 2)
    recognizer = sr.Recognizer()
    try:
        return recognizer.recognize_google(audio, language='ru-RU')
    except sr.UnknownValueError:
        return ''
    except Exception:
        return None
