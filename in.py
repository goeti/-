import sys

import numpy as np
import pyaudio as pa
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtWidgets import QInputDialog

SAMPLE_RATE = 44100
#                      0       1       2      3        4       5       6
#                      до      ре      ми     фа       соль    ля      си
freq_array = np.array([261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88])
key_names = ['a', 's', 'd', 'f', 'g', 'h', 'j']
key_list = list(map(lambda x: ord(x), key_names))
key_dict = dict([(key, False) for key in key_list])


# функции генерации волн
def square(x):
    return np.clip(np.ceil(np.sin(x)), 0, 0.5)


def saw(x):
    c = x / np.pi - 0.5
    return 0.5 * (c - np.floor(0.5 + c)) + 0.25


def triangle(x):
    return np.abs(x % 6 - 3) / (2 * np.pi)


gen_func = np.sin
gen_func_list = (
    (np.sin, ord('w')),
    (square, ord('e')),
    (saw, ord('r')),
    (triangle, ord('t'))
)


def generate_sample(freq, duration, volume):
    amplitude = np.round((2 ** 16) * volume)
    total_samples = np.round(SAMPLE_RATE * duration)
    w = 2.0 * np.pi * freq / SAMPLE_RATE
    k = np.arange(0, total_samples)
    return np.round(amplitude * gen_func(k * w))


def generate_tones(duration):
    tones = []
    for freq in freq_array:
        tone = np.array(generate_sample(freq, duration, 1.0), dtype=np.int16)
        tones.append(tone)
    return tones


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 300, 300)
        self.setWindowTitle('Синтезатор')

        self.button_1 = QPushButton(self)
        self.button_1.move(20, 40)
        self.button_1.setText("  выбор октавы  ")
        self.button_1.clicked.connect(self.run)

        self.button_2 = QPushButton(self)
        self.button_2.move(120, 40)
        self.button_2.setText("выбор волн")
        self.button_2.clicked.connect(self.run1)
        self.show()

    def run(self):
        i, okBtnPressed = QInputDialog.getItem(
            self,
            "Выберите октаву",
            'вы можете менять октаву на кнопки 1 и 2',
            ("Субконтроктава", "Контроктава", "Большая октава", 'Малая октава', 'Первая октава', 'Вторая октава',
             'Третья октава', 'Четвёртая октава', 'Пятая октава'),
            4,
            False
        )
        if okBtnPressed:
            self.button_1.setText(i)

    def run1(self):
        i, okBtnPressed = QInputDialog.getItem(
            self,
            "Выберите волну",
            'вы можете менять виды синтезируемых волн на кнопки w, e, r, t',
            ("sin", "square", "saw", 'triangle'),
            0,
            False
        )
        if okBtnPressed:
            self.button_2.setText(i)

    def keyPressEvent(self, event):
        SAMPLE_RATE = 44100
        #                      0       1       2      3        4       5       6
        #                      до      ре      ми     фа       соль    ля      си
        freq_array = np.array([261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88])
        key_names = ['a', 's', 'd', 'f', 'g', 'h', 'j']
        key_list = list(map(lambda x: ord(x), key_names))
        key_dict = dict([(key, False) for key in key_list])

        gen_func = np.sin
        gen_func_list = (
            (np.sin, ord('w')),
            (square, ord('e')),
            (saw, ord('r')),
            (triangle, ord('t'))
        )

        p = pa.PyAudio()
        stream = p.open(format=p.get_format_from_width(width=2),
                        channels=2,
                        rate=SAMPLE_RATE,
                        output=True)
        duration_tone = 1 / 2.0
        tones = generate_tones(duration_tone)
        if event.key == ord('-'):
            duration_tone /= 2
            print('duration_tone =', duration_tone)
            tones = generate_tones(duration_tone)
        if event.key == ord('='):
            duration_tone *= 2
            print('duration_tone =', duration_tone)
            tones = generate_tones(duration_tone)
        if event.key == ord('1'):
            freq_array /= 2
            print('freq_array =', freq_array)
            tones = generate_tones(duration_tone)
        if event.key == ord('2'):
            freq_array *= 2
            print('freq_array =', freq_array)
            tones = generate_tones(duration_tone)
        for (function, key) in gen_func_list:
            if key == event.key:
                print('gen_function =', function.__name__)
                gen_func = function
                tones = generate_tones(duration_tone)
        for (index, key) in enumerate(key_list):
            if event.key == key:
                key_dict[key] = True
        if event.type == Qt.KEYUP:
            for (index, key) in enumerate(key_list):
                if event.key == key:
                    key_dict[key] = False
        for (index, key) in enumerate(key_list):
            if key_dict[key] is True:
                stream.write(tones[index])


if __name__ == '__main__':
    duration_tone = 1 / 2.0
    tones = generate_tones(duration_tone)
    p = pa.PyAudio()
    stream = p.open(format=p.get_format_from_width(width=2),
                    channels=2,
                    rate=SAMPLE_RATE,
                    output=True)
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    stream.stop_stream()
    stream.close()
    p.terminate()
    sys.exit(app.exec())