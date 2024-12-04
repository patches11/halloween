import time
import RPi.GPIO as GPIO
 
# Import the WS2801 module.
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI
 
import SimpleHTTPServer
import SocketServer

import threading
import sys
import random

# Configure the count of pixels:
PIXEL_COUNT = 50
 
# Alternatively specify a hardware SPI connection on /dev/spidev0.0:
SPI_PORT   = 0
SPI_DEVICE = 0

UPDATES_PER_SECOND = 50

PORT = 9067

FLASHES_MAX = 8
LIGHTNING_PROB = 0.1

pixels = Adafruit_WS2801.WS2801Pixels(PIXEL_COUNT, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE), gpio=GPIO)

class Lightning:
    def __init__(self):
        self.flash = 0
        self.ledStart = 0
        self.ledLen = 0
        self.delay = 0
        self.last = 0

    def fadeToBlackBy(self, amount):
        for i in range(PIXEL_COUNT):
            color = pixels.get_pixel_rgb(i)
            pixels.set_pixel_rgb(i, max(0, color[0] - amount), max(0, color[1] - amount), max(0, color[2] - amount))
        pixels.show()

    def run(self):
        self.fadeToBlackBy(10)

        dimmer = random.randrange(1, 3)

        if self.flash == 0:
            if random.random() < LIGHTNING_PROB:
                self.flash = random.randrange(3, FLASHES_MAX)
                self.ledStart = random.randrange(PIXEL_COUNT)
                self.ledLen = random.randrange(PIXEL_COUNT - self.ledStart)
                self.last = time.time() * 1000
                self.delay = -2
                dimmer = 5

        if self.flash > 0 and self.last + self.delay < time.time() * 1000:
            #Flash
            for i in range(self.ledStart, self.ledStart + self.ledLen):
                pixels.set_pixel_rgb(i, 255 / dimmer, 255 / dimmer, 255 / dimmer)
            pixels.show()
            time.sleep(random.randrange(4,10) / 1000.0)
            for i in range(self.ledStart, self.ledStart + self.ledLen):
                pixels.set_pixel_rgb(i, 0, 0, 0)
            pixels.show()

            if (dimmer == 5):
                self.delay = 150
            else:
                self.delay = random.randrange(50,150)

            self.last = time.time() * 1000
            self.flash -= 1

global state
state = 0

class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def goHome(self):
        self.send_response(302)
        self.send_header('Location', "/")
        self.end_headers()

    def do_GET(self):
        global state
        if self.path == "/green":
            state = 0
            self.goHome()
        if self.path == "/red":
            state = 1
            self.goHome()
        if self.path == "/lightning":
            state = 2
            self.goHome()
        if self.path == "/clear":
            state = 999
            self.goHome()
        else:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

def flow(i):
    return ((i * 2 + int(time.time() * 20)) % 200) + 56

if __name__ == "__main__":
    Handler = ServerHandler

    lightning = Lightning()

    httpd = SocketServer.TCPServer(("", PORT), Handler)
    thread = threading.Thread(target = httpd.serve_forever)
    thread.daemon = True
    try:
        thread.start()
        while True:
            if state == 0:
                # Green
                for i in range(PIXEL_COUNT):
                    pixels.set_pixel_rgb(i, 0, flow(i), 0)
                pixels.show()
            if state == 1:
                # Red
                for i in range(PIXEL_COUNT):
                    pixels.set_pixel_rgb(i, flow(i), 0, 0)
                pixels.show()
            if state == 2:
                lightning.run()
            if state == 999:
                pixels.clear()
                pixels.show()

            time.sleep(1.0/UPDATES_PER_SECOND)
    except KeyboardInterrupt:
        print("KeyboardInterruptHandler")
        httpd.shutdown()
        sys.exit(0)

    
