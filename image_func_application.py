import datetime
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
import config_file


def get_cat_image_with_date() -> BytesIO:
    # Текущая дата в заданном формате на момент отправки сообщения
    message = str(datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S'))
    # Открываем локально скачанную картинку
    cat_image: Image.Image = Image.open(config_file.config.get('cat_image_path'))
    width, height = cat_image.size
    # Задаём шрифт и размер для картинки
    image_font = ImageFont.truetype("arial.ttf", 100)
    # Объект для отрисовки сообщения с датой на картинке
    draw = ImageDraw.Draw(cat_image)
    # Создаём bbox, внутри которого размещаем текстом дату
    _, _, w, h = draw.textbbox(xy=(0, 0), text=message, font=image_font)
    # Отрисовываем на картинке дату
    draw.text(
        xy=((width - w) / 2, (height - h) * 0.75),
        text=message,
        fill=(227, 38, 54),
        font=image_font,
        align='left'
    )

    bio = BytesIO()
    bio.name = 'cat.jpeg'
    cat_image.save(bio, 'JPEG')
    bio.seek(0)

    return bio
