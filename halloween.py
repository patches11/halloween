import time
import RPi.GPIO as GPIO
 
# Import the WS2801 module.
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI
 
import SimpleHTTPServer
import SocketServer

import threading
import sys

# Configure the count of pixels:
PIXEL_COUNT = 50
 
# Alternatively specify a hardware SPI connection on /dev/spidev0.0:
SPI_PORT   = 0
SPI_DEVICE = 0

UPDATES_PER_SECOND = 50

PORT = 9067

pixels = Adafruit_WS2801.WS2801Pixels(PIXEL_COUNT, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE), gpio=GPIO)

def lightning(pixels):
    pixels.clear()
    pixels.show()

global state
state = 999

class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def goHome(self):
        self.send_response(302)
        self.send_header('Location', "/")
        self.end_headers()

    def do_GET(self):
        print(self.path)
        if self.path == "/green":
            global state
            state = 0
            self.goHome()
        if self.path == "/red":
            global state
            state = 1
            self.goHome()
        if self.path == "/lightning":
            global state
            state = 2
            self.goHome()
        if self.path == "/clear":
            global state
            state = 999
            self.goHome()
        else:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

if __name__ == "__main__":
    Handler = ServerHandler

    httpd = SocketServer.TCPServer(("", PORT), Handler)
    thread = threading.Thread(target = httpd.serve_forever)
    thread.daemon = True
    try:
        thread.start()
        while True:
            if state == 0:
                # Green
                pixels.set_pixels(Adafruit_WS2801.RGB_to_color(0, 255, 0))
                pixels.show()
            if state == 1:
                # Red
                pixels.set_pixels(Adafruit_WS2801.RGB_to_color(255, 0, 0))
                pixels.show()
            if state == 2:
                lightning(pixels)
            if state == 999:
                pixels.clear()
                pixels.show()

            time.sleep(1.0/UPDATES_PER_SECOND)
    except KeyboardInterrupt:
        print("KeyboardInterruptHandler")
        httpd.shutdown()
        sys.exit(0)

    