import time

import imgkit
import schedule
from waveshare_epd import epd7in5bc
from PIL import Image, ImageDraw, ImageFont


def renderhtml(url):
    try:
        config = imgkit.config()
        options = {
            'format': 'bmp',
            'width': 640,
            'height': 384
        }
        imgkit.from_url(url, FILE_PATH, config=config, options=options)
    except:
        print('error with rendering')


def print_page():
    print('Download')
    renderhtml('https://jupidev.de/view.html')
    print('Download done')
    image = Image.open(FILE_PATH).convert('L').crop((40, 0, 680, 384))
    LRYimage = Image.new('1', (epd.height, epd.width), 255)
    epd.display(epd.getbuffer(image), epd.getbuffer(LRYimage))
    print('Drawing Done')
    time.sleep(2)


def register_refresh():
    schedule.every(90).seconds.do(print_page, 'refresh')


def unregister_refresh():
    schedule.clear('refresh')
    image = Image.open('sleeping.bmp').crop((40, 0, 680, 384))
    LRYimage = Image.new('1', (epd.height, epd.width), 255)
    epd.display(epd.getbuffer(image), epd.getbuffer(LRYimage))

def run():
    print_page()
    schedule.every().day.at('04:30').do(register_refresh)

    schedule.every().day.at('22:00').do(unregister_refresh)

    while 1:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    FILE_PATH = '/home/pi/out.bmp'
    print('Wilkommen')
    epd = epd7in5bc.EPD()
    epd.init()
    run()
