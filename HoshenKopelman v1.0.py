from PIL import Image, ImageDraw
from random import randint

# Объявляем глоюальные переменные
colors = [(0, 0, 205), (0, 191, 255), (0, 255, 0), (46, 139, 87),
          (255, 255, 0), (205, 92, 92), (255, 0, 0), (255, 20, 147),
          (160, 32, 240), (255, 246, 143)]
clusters = {}
mark = 0

def colorGen(color=colors):
    # Случайным образом выбирает цвет из входного массива.
    return colors[randint(0, len(colors)-1)]

def convertToBMP(adress):
    # Конвертирует входящее изображение в формат bmp для улучшения качества
    # и устранения шумов. Принимает 1 аргумент - адрес изображения, возвращает
    # адрес конвертированого изображения.
    img = Image.open(adress)
    if img.format != 'BMP':
        adress = adress.split('.')[0]+'.bmp'
    img.save('image\\'+adress, 'BMP')
    return 'image\\'+adress

def filterAndLines(adress):
    # Дорисовывает по верхнему и левому краю изображения две белых линии.
    img = Image.open(adress)
    width, height = img.size[0], img.size[1]
    draw = ImageDraw.Draw(img)
    draw.line((0, 0, 0, height), fill=(255, 255, 255))  # линия слева
    draw.line((0, 0, width, 0), fill=(255, 255, 255))   # линия сверху
    del draw
    img.save(adress, 'BMP')
    return adress

def firstClustPix(temp, mark, dic, i, j):
    # Часть алгоритма, описывает порядок действий при встрече элемента не имеющего
    # соседей сверху и слева. Принимает аргументы: temp - текущая строка пикселей
    # в изображении; mark - последняя кластерная метка; i,j - координаты пикселя.
    # Возвращает текущую кластерную метку
    mark += 1
    temp.append(mark)
    dic[mark] = []
    dic[mark].append((j, i))
    return mark

def upclustApply(temp, marked, dic, i, j):
    # Добавляет в словарь элемент имеющий соседа сверху (с кластерной меткой соседа).
    # marked - предыдущая строка изображения, сосотоящая из кластерных меток.
    dic[marked[j-1]].append((j, i))
    temp.append(marked[j-1])

def leftclustApply(temp, dic, i, j):
    # Добавляет в словарь элемент имеющий соседа слева(с кластерной меткой соседа).
    # temp - текущая строка; dic - словарь с ключами из кластерных меток; i,j -
    # координаты текущего пикселя.
    dic[temp[-1]].append((j, i))
    temp.append(temp[-1])
    
def clustCompareAdd(temp, marked, dic, i, j):
    # Проверяет кластерные метки соседа слева и сверху выбирая из них наименьшую.
    # Можно оптимизировать, заменив два последних цикла констр. try...except.
    lmark = min(temp[-1], marked[j-1])
    umark = max(temp[-1], marked[j-1])
    temp.append(lmark)
    dic[lmark].append((j, i))
    if lmark!=umark:
        for item in dic.pop(umark):
            dic[lmark].append(item)
        for k in range(len(marked)):
            if marked[k] == umark:
                marked[k] = lmark
        for k in range(len(temp)):
            if temp[k] == umark:
                temp[k] = lmark


def hoshenKopelmanAnalysis(img, mark=mark):
    # Тело алгоритма, выполняет попикселный анализ изображения.
    # img - объект-изображение; mark - текущая кластерная метка.
    width, height = img.size[0], img.size[1]
    pix = img.load()
    for i in range(1, height):
        temp = []
        for j in range(1, width):
            pixel = (pix[j, i][0]+pix[j, i][1]+pix[j, i][2])/3
            if pixel<=100:
                pix[j, i] = (0, 0, 0)
                pixel = 0
            else:
                pix[j, i] = (255, 255, 255)
                pixel = 255
            upix = (pix[j, i-1][0]+pix[j, i-1][1]+pix[j, i-1][2])/3   # пиксель сверху
            lpix = (pix[j-1, i][0]+pix[j-1, i][1]+pix[j-1, i][2])/3   # пиксель снизу
            if pixel==0:
                if lpix==255 and upix==255:
                    mark = firstClustPix(temp, mark, clusters, i, j)
                elif lpix==0 and upix==0:
                    clustCompareAdd(temp, marked, clusters, i, j)
                elif lpix==0 and upix!=0:
                    leftclustApply(temp, clusters, i, j)
                elif lpix!=0 and upix==0:
                    upclustApply(temp, marked, clusters, i, j)
            else:
                temp.append(0)
        marked = temp

def variegation(dic, img):
    # Раскрашивает полученные кластеры.
    draw = ImageDraw.Draw(img)
    for item in dic.keys():
        if len(dic[item])>100:
            color = colorGen()
            for elem in dic[item]:
                draw.point((elem[0], elem[1]), color)
    del draw


adress=input("Write an adress of initial image: ")
adress = filterAndLines(convertToBMP(adress))
img = Image.open(adress)                   
hoshenKopelmanAnalysis(img)
variegation(clusters, img)
img.save(adress, 'BMP')
