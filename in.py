import sys
import time

import numpy as np
import pyaudio as pa
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtWidgets import QInputDialog


# функции генерации волн


def square(x):
    return np.clip(np.ceil(np.sin(x)), 0, 0.5)


def saw(x):
    c = x / np.pi - 0.5
    return 0.5 * (c - np.floor(0.5 + c)) + 0.25


def triangle(x):
    return np.abs(x % 6 - 3) / (2 * np.pi)


# запись звука и воспроизведение


class Writing(QTimer):
    def __init__(self):
        super().__init__()
        self.work()

    def work(self):
        self.counter = 0
        self.count = 10000

    def start_timer(self, count=1, interval=100):
        print(1)

        def handler():
            self.counter += 100
            if self.counter >= count:
                timer.stop()
                timer.deleteLater()

        timer = QTimer()
        timer.timeout.connect(handler)
        timer.start(interval)

    # таймер

    def timer1(self, time):
        c = (self.a[0][time] * 1000) - 170
        print(c)
        QTimer().singleShot(c, self.play_sounds)

    def play(self):
        self.a = Example.turn(self)
        global p, stream
        p = pa.PyAudio()
        stream = p.open(format=p.get_format_from_width(width=2),
                        channels=2,
                        rate=SAMPLE_RATE,
                        output=True)
        self.number = 0
        self.timer1(0)

    def play_sounds(self):
        global p, stream
        p = pa.PyAudio()
        stream = p.open(format=p.get_format_from_width(width=2),
                        channels=2,
                        rate=SAMPLE_RATE,
                        output=True)
        stream.write(self.a[1][self.number])
        self.number += 1
        if self.number < len(self.a[1]):
            self.timer1(self.number)


# основной интерфейс


class Example(QWidget, Writing):
    def __init__(self):
        super().__init__()
        self.initUI()

    # функции генерации звука

    def generate_sample(self, freq, duration, volume):
        self.gen_func_list = (
            ('np.sin', ord('W')),
            ('square', ord('E')),
            ('saw', ord('R')),
            ('triangle', ord('T'))
        )
        amplitude = np.round((2 ** 16) * volume)
        total_samples = np.round(SAMPLE_RATE * duration)
        w = 2.0 * np.pi * freq / SAMPLE_RATE
        k = np.arange(0, total_samples)
        task = {'square': square, 'saw': saw, 'triangle': triangle, 'np.sin': np.sin}
        return np.round(amplitude * task[self.gen_func](k * w))

    def generate_tones(self, duration):
        tones = []
        for freq in self.freq_array:
            tone = np.array(self.generate_sample(freq, duration, 1.0), dtype=np.int16)
            tones.append(tone)
        return tones

    def initUI(self):
        self.setGeometry(300, 300, 400, 400)
        self.setWindowTitle('Синтезатор')

        self.button_1 = QPushButton(self)
        self.button_1.move(20, 40)
        self.button_1.setText("  выбор октавы  ")
        self.button_1.clicked.connect(self.run)

        self.flag = 0
        self.flag1 = 0
        self.gen_func = np.sin
        self.gen_func_list = (
            ('np.sin', ord('W')),
            ('square', ord('E')),
            ('saw', ord('R')),
            ('triangle', ord('T'))
        )
        self.key_names = ['A', 'S', 'D', 'F', 'G', 'H', 'J']
        self.key_list = list(map(lambda x: ord(x), self.key_names))
        self.key_dict = dict([(key, False) for key in self.key_list])
        self.SAMPLE_RATE = 44100
        #                      0       1       2      3        4       5       6
        #                      до      ре      ми     фа       соль    ля      си
        self.freq_array = np.array([261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88])
        self.duration_tone = 1 / 2.0
        self.button_2 = QPushButton(self)
        self.button_2.move(120, 40)
        self.button_2.setText("выбор волн")
        self.button_2.clicked.connect(self.run1)

        self.button_3 = QPushButton(self)
        self.button_3.move(200, 40)
        self.button_3.setText("выбор длительнности звуков")
        self.button_3.clicked.connect(self.run2)

        self.button_4 = QPushButton(self)
        self.button_4.move(20, 100)
        self.button_4.setText("запись")
        self.button_4.clicked.connect(self.run3)

        self.button_5 = QPushButton(self)
        self.button_5.move(120, 100)
        self.button_5.setText("воспроизведеие")
        self.button_5.clicked.connect(self.run4)

        self.button_6 = QPushButton(self)
        self.button_6.move(20, 140)
        self.button_6.setText("стоп")
        self.button_6.clicked.connect(self.run5)

        self.SAMPLE_RATE = 44100
        #                      0       1       2      3        4       5       6
        #                      до      ре      ми     фа       соль    ля      си
        self.freq_array = np.array([261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88])
        self.key_names = ['A', 'S', 'D', 'F', 'G', 'H', 'J']
        self.key_list = list(map(lambda x: ord(x), self.key_names))
        self.key_dict = dict([(key, False) for key in self.key_list])

        self.freqdict = {"Субконтроктава": self.freq_array / 16, "Контроктава": self.freq_array / 8,
                         "Большая октава": self.freq_array / 4, 'Малая октава': self.freq_array / 2,
                         'Первая октава': self.freq_array, 'Вторая октава': self.freq_array * 2,
                         'Третья октава': self.freq_array * 4, 'Четвёртая октава': self.freq_array * 8,
                         'Пятая октава': self.freq_array * 16}
        self.gen_func = 'np.sin'
        self.gen_func_list = (
            ('np.sin', ord('W')),
            ('square', ord('E')),
            ('saw', ord('R')),
            ('triangle', ord('T'))
        )
        self.duration_tone = 1 / 2.0
        self.tones = self.generate_tones(self.duration_tone)

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
            self.freq_array = self.freqdict[i]
            self.tones = self.generate_tones(self.duration_tone)

    def run1(self):
        i, okBtnPressed = QInputDialog.getItem(
            self,
            "Выберите волну",
            'вы можете менять виды синтезируемых волн на кнопки w, e, r, t',
            ('np.sin', 'square', 'saw', 'triangle'),
            0,
            False
        )
        if okBtnPressed:
            self.gen_func = i
            self.tones = self.generate_tones(self.duration_tone)

    def run2(self):
        i, okBtnPressed = QInputDialog.getItem(
            self,
            "Выберите длительности",
            'вы можете менять длительность на кнопки - и =',
            ('0.125', '0.25', '0.5', '1.0', '2.0'),
            2,
            False
        )
        if okBtnPressed:
            self.duration_tone = float(i)
            self.tones = self.generate_tones(self.duration_tone)

    def run3(self):
        self.time = time.time()
        self.sounds = []
        self.times = []
        self.counter1 = 0
        self.flag = 1
        self.flag1 = 1

    def run4(self):
        if (self.flag1 == 1) and (self.flag == 0):
            super(Example, self).play()

    def run5(self):
        self.flag = 0

    def turn(self):
        return (self.times, self.sounds)

    def keyPressEvent(self, event):
        global p, stream
        p = pa.PyAudio()
        stream = p.open(format=p.get_format_from_width(width=2),
                        channels=2,
                        rate=SAMPLE_RATE,
                        output=True)
        if event.key() == ord('-'):
            self.duration_tone /= 2
            print('duration_tone =', self.duration_tone)
            self.tones = self.generate_tones(self.duration_tone)
        if event.key() == ord('='):
            self.duration_tone *= 2
            print('duration_tone =', self.duration_tone)
            self.tones = self.generate_tones(self.duration_tone)
        if event.key() == ord('1'):
            self.freq_array /= 2
            print('freq_array =', self.freq_array)
            self.tones = self.generate_tones(self.duration_tone)
        if event.key() == ord('2'):
            self.freq_array *= 2
            print('freq_array =', self.freq_array)
            self.tones = self.generate_tones(self.duration_tone)
        for (function, key) in self.gen_func_list:
            if event.key() == key:
                print('gen_function =', function)
                self.gen_func = function
                self.tones = self.generate_tones(self.duration_tone)
        for (index, key) in enumerate(self.key_list):
            if event.key() == key:
                stream.write(self.tones[index])
                if self.flag != 0:
                    self.sounds.append(self.tones[index])
                    self.time1 = time.time()
                    self.times.append(self.time1 - self.time)
                    self.time = self.time1
                    self.counter1 = self.counter


if __name__ == '__main__':
    e = []
    SAMPLE_RATE = 44100
    #                      0       1       2      3        4       5       6
    #                      до      ре      ми     фа       соль    ля      си
    freq_array = np.array([261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88])
    key_names = ['a', 's', 'd', 'f', 'g', 'h', 'j']
    key_list = list(map(lambda x: ord(x), key_names))
    key_dict = dict([(key, False) for key in key_list])
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
