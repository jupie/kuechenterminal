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
    renderhtml('http://127.0.0.1:8080')
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
    server = page.Server()
    server.start()
    print_page()
    if 22 > time.localtime(time.time()).tm_hour > 4:
        register_refresh()
    else:
        unregister_refresh()

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
