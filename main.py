import os
from PyQt5.QtWidgets import (
    QApplication, QWidget,
    QFileDialog,
    QLabel, QPushButton, QListWidget,
    QHBoxLayout, QVBoxLayout, QInputDialog
)
from PyQt5.QtCore import Qt  # потрібна константа Qt.KeepAspectRatio для зміни розмірів із збереженням пропорцій
from PyQt5.QtGui import QPixmap  # оптимізована для показу на екрані картинка

from PIL import Image, ImageEnhance
from PIL.ImageFilter import SHARPEN

app = QApplication([])
win = QWidget()
win.resize(700, 500)
win.setWindowTitle('Easy Editor')

# Чорна тема і круглі кнопки

app.setStyleSheet("""
    QWidget {
        background-color: #2e2e2e;
        color: #b0b0b0;  
    }
    QLabel {
        color: #b0b0b0;  
    }
    QPushButton {
        background-color: #555555;
        border: 1px solid #000000;  
        color: #b0b0b0;  
        padding: 5px;
        border-radius: 10px;  
    }
    QPushButton:hover {
        background-color: #666666;
    }
    QListWidget {
        background-color: #444444;
        color: #b0b0b0;  
        border: 1px solid #000000;  
    }
    QLineEdit {
        background-color: #444444;
        color: #b0b0b0;  
        border: 1px solid #000000;  
    }
""")

lb_size = QLabel("Розміри: 0 x 0")  # Ініціалізація мітки з початковими значеннями
lb_image = QLabel("Картинка")
btn_dir = QPushButton("Папка")
lw_files = QListWidget()

btn_left = QPushButton("Вліво")
btn_right = QPushButton("Вправо")
btn_flip = QPushButton("Відзеркалити")
btn_sharp = QPushButton("Різкість")
btn_bw = QPushButton("Ч/Б")
btn_brightness = QPushButton("Яскравість")
btn_contrast = QPushButton("Контрастність")
btn_crop = QPushButton("Обрізати")
btn_res = QPushButton("Скинути")

row = QHBoxLayout()  # Головна лінія
col1 = QVBoxLayout()  # ділиться на два стовпці
col2 = QVBoxLayout()
col1.addWidget(btn_dir)  # в першому - кнопка вибору каталогу
col1.addWidget(lw_files)  # і список файлов
col2.addWidget(lb_image, 95)  # в другому - картинка
col2.addWidget(lb_size)  # Додавання мітки до другого стовпця інтерфейсу
row_tools = QHBoxLayout()  # і ряд кнопок
row_tools.addWidget(btn_left)
row_tools.addWidget(btn_right)
row_tools.addWidget(btn_flip)
row_tools.addWidget(btn_sharp)
row_tools.addWidget(btn_bw)
row_tools.addWidget(btn_brightness)
row_tools.addWidget(btn_contrast)  # кнопка для контрастності
row_tools.addWidget(btn_crop)  # для обрізання зображення
row_tools.addWidget((btn_res))
col2.addLayout(row_tools)

row.addLayout(col1, 20)
row.addLayout(col2, 80)
win.setLayout(row)

win.show()

workdir = ''


def filter(files, extensions):
    result = []
    for filename in files:
        for ext in extensions:
            if filename.endswith(ext):
                result.append(filename)
    return result


def chooseWorkdir():
    global workdir
    workdir = QFileDialog.getExistingDirectory()


def showFilenamesList():
    extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    chooseWorkdir()
    filenames = filter(os.listdir(workdir), extensions)

    lw_files.clear()
    for filename in filenames:
        lw_files.addItem(filename)


btn_dir.clicked.connect(showFilenamesList)


class ImageProcessor():
    def __init__(self):
        self.image = None
        self.dir = None
        self.filename = None
        self.save_dir = "Modified/"
        self.original_img = None

    def loadImage(self, filename):
        ''' під час завантаження запам'ятовуємо шлях та ім'я файлу '''
        self.filename = filename
        fullname = os.path.join(workdir, filename)
        self.image = Image.open(fullname)
        self.original_img = self.image.copy()

    def saveImage(self):
        ''' зберігає копію файлу у підпапці '''
        path = os.path.join(workdir, self.save_dir)
        if not (os.path.exists(path) or os.path.isdir(path)):
            os.mkdir(path)
        fullname = os.path.join(path, self.filename)

        self.image.save(fullname)

    def do_bw(self):
        self.image = self.image.convert("L")
        self.saveImage()
        image_path = os.path.join(workdir, self.save_dir, self.filename)
        self.showImage(image_path)

    def do_left(self):
        self.image = self.image.transpose(Image.ROTATE_90)
        self.saveImage()
        image_path = os.path.join(workdir, self.save_dir, self.filename)
        self.showImage(image_path)

    def do_right(self):
        self.image = self.image.transpose(Image.ROTATE_270)
        self.saveImage()
        image_path = os.path.join(workdir, self.save_dir, self.filename)
        self.showImage(image_path)

    def do_flip(self):
        self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT)
        self.saveImage()
        image_path = os.path.join(workdir, self.save_dir, self.filename)
        self.showImage(image_path)

    def do_sharpen(self):
        self.image = self.image.filter(SHARPEN)
        self.saveImage()
        image_path = os.path.join(workdir, self.save_dir, self.filename)
        self.showImage(image_path)

    def showImage(self, path):
        lb_image.hide()
        pixmapimage = QPixmap(path)
        w, h = lb_image.width(), lb_image.height()
        lb_size.setText(f"Розміри: {pixmapimage.width()} x {pixmapimage.height()}")  # Оновлення мітки розміру
        pixmapimage = pixmapimage.scaled(w, h, Qt.KeepAspectRatio)
        lb_image.setPixmap(pixmapimage)
        lb_image.show()

    def resetImage(self):
        if self.original_img:
            self.image = self.original_img.copy()
            self.saveImage()
            image_path = os.path.join(workdir, self.save_dir, self.filename)
            self.showImage(image_path)

    def do_brightness(self):
        enhancer = ImageEnhance.Brightness(self.image)
        # Збільшуємо яскравість на 20% кожен раз, коли натискається кнопка
        self.image = enhancer.enhance(1.2)
        self.saveImage()
        image_path = os.path.join(workdir, self.save_dir, self.filename)
        self.showImage(image_path)

    def do_contrast(self):
        ''' Змінює контрастність зображення '''
        enhancer = ImageEnhance.Contrast(self.image)
        self.image = enhancer.enhance(2.0)  # Збільшення контрастності у 2 рази
        self.saveImage()
        image_path = os.path.join(workdir, self.save_dir, self.filename)
        self.showImage(image_path)

    def do_crop(self):
        ''' Запитує у користувача розміри та здійснює обрізку зображення '''
        area = QInputDialog.getText(win, 'Обрізати зображення',
                                    'Введіть координати області обрізання (x, y, ширина, висота):')
        if area[1]:
            x, y, w, h = map(int, area[0].split(','))
            self.image = self.image.crop((x, y, x + w, y + h))
            self.saveImage()
            image_path = os.path.join(workdir, self.save_dir, self.filename)
            self.showImage(image_path)

def showChosenImage():
    if lw_files.currentRow() >= 0:
        filename = lw_files.currentItem().text()
        workimage.loadImage(filename)
        workimage.showImage(os.path.join(workdir, workimage.filename))


workimage = ImageProcessor()  # поточне робоче зображення для роботи
lw_files.currentRowChanged.connect(showChosenImage)

btn_bw.clicked.connect(workimage.do_bw)
btn_left.clicked.connect(workimage.do_left)
btn_right.clicked.connect(workimage.do_right)
btn_sharp.clicked.connect(workimage.do_sharpen)
btn_flip.clicked.connect(workimage.do_flip)
btn_brightness.clicked.connect(workimage.do_brightness)
btn_contrast.clicked.connect(workimage.do_contrast)
btn_crop.clicked.connect(workimage.do_crop)
btn_res.clicked.connect(workimage.resetImage)

app.exec()