import time
import board
import busio
import displayio
import terminalio
from digitalio import DigitalInOut

from adafruit_display_text import label
from adafruit_display_shapes.triangle import Triangle
from adafruit_display_shapes.rect import Rect
from adafruit_bitmap_font import bitmap_font

import adafruit_requests as requests
#from adafruit_pyportal import PyPortal
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi

################### Global vars ########################################################
WHITE = 0xFFFFFF
BLACK = 0x000000
GREEN = 0x00FF00
RED =   0xFF0000
URL_BASE = "https://eodhistoricaldata.com/api/real-time/"
URL_APIKEY = "?api_token="
URL_FORMAT = "&fmt=json"
URL_ADDL_STOCKS = "&s="
URL1 = "https://eodhistoricaldata.com/api/real-time/AAPL?api_token=5e3667b5434e12.89123274&fmt=json"
URL2 = "https://eodhistoricaldata.com/api/real-time/GOOG?api_token=5e3667b5434e12.89123274&fmt=json"
URL3 = "https://eodhistoricaldata.com/api/real-time/TSLA?api_token=5e3667b5434e12.89123274&fmt=json"

num_loops = 0 # Useful for debugging, tracks how many times we've successfully requested and received all 3 stock data

######## Get info from secrets.py ######################################################
try:
    from secrets import secrets
except ImportError:
    print("WiFi credentials, API keys, and assets tracked are kept in secrets.py, please add them there!")
    raise

########### Set up display and load screen UI ##########################################
display = board.DISPLAY
display.rotation = 90
font = bitmap_font.load_font("fonts/LeagueSpartan-Bold-16.bdf")
loadscreen_group = displayio.Group()
loadscreen_label = label.Label(font, text="Connecting to WiFi...", scale=1, color=WHITE, x=50, y=150)
loadscreen_group.append(loadscreen_label)
display.show(loadscreen_group)

######## Wi-Fi setup ###################################################################
esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp32 = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

requests.set_socket(socket, esp32)

if esp32.status == adafruit_esp32spi.WL_IDLE_STATUS:
    print("ESP32 found and in idle mode")

print("Authenticating with WiFi...")
while not esp32.is_connected:
    try:
        esp32.connect_AP(secrets["ssid"], secrets["password"])
    except RuntimeError as e:
        print("could not connect to WiFi, retrying: ", e)
        continue
print("Connected to", str(esp32.ssid, "utf-8"), "\tRSSI:", esp32.rssi)
print("My IP address is", esp32.pretty_ip(esp32.ip_address))

api_key = secrets['api_key']

######## FINAL UI setup ##############################################################
indent_top = 48
indent_label = 24
indent_price = 112
indent_change = 240
vert_spacing = 48

pricedata_group = displayio.Group()
label_stockname1 = label.Label(font, text=secrets["stock1"], color=WHITE, x=indent_label, y=indent_top )
label_stockname2 = label.Label(font, text=secrets["stock2"], color=WHITE, x=indent_label, y=(indent_top + vert_spacing) )
label_stockname3 = label.Label(font, text=secrets["stock3"], color=WHITE, x=indent_label, y=(indent_top + vert_spacing*2) )
label_stockname4 = label.Label(font, text=secrets["stock4"], color=WHITE, x=indent_label, y=(indent_top + vert_spacing*3) )
label_stockname5 = label.Label(font, text=secrets["stock5"], color=WHITE, x=indent_label, y=(indent_top + vert_spacing*4) )
label_stockname6 = label.Label(font, text=secrets["stock6"], color=WHITE, x=indent_label, y=(indent_top + vert_spacing*5) )
label_stockname7 = label.Label(font, text=secrets["stock7"], color=WHITE, x=indent_label, y=(indent_top + vert_spacing*6) )
label_stockname8 = label.Label(font, text=secrets["stock8"], color=WHITE, x=indent_label, y=(indent_top + vert_spacing*7) )
label_stockname9 = label.Label(font, text=secrets["stock9"], color=WHITE, x=indent_label, y=(indent_top + vert_spacing*8) )

label_stock1_price = label.Label(font, text="wait...", scale=1, color=WHITE, x=indent_price, y=indent_top)
label_stock2_price = label.Label(font, text="wait...", scale=1, color=WHITE, x=indent_price, y=(indent_top + vert_spacing))
label_stock3_price = label.Label(font, text="wait...", scale=1, color=WHITE, x=indent_price, y=(indent_top + vert_spacing*2) )
label_stock4_price = label.Label(font, text="wait...", scale=1, color=WHITE, x=indent_price, y=(indent_top + vert_spacing*3) )
label_stock5_price = label.Label(font, text="wait...", scale=1, color=WHITE, x=indent_price, y=(indent_top + vert_spacing*4) )
label_stock6_price = label.Label(font, text="wait...", scale=1, color=WHITE, x=indent_price, y=(indent_top + vert_spacing*5) )
label_stock7_price = label.Label(font, text="wait...", scale=1, color=WHITE, x=indent_price, y=(indent_top + vert_spacing*6) )
label_stock8_price = label.Label(font, text="wait...", scale=1, color=WHITE, x=indent_price, y=(indent_top + vert_spacing*7) )
label_stock9_price = label.Label(font, text="wait...", scale=1, color=WHITE, x=indent_price, y=(indent_top + vert_spacing*8) )

label_stock1_change = label.Label(font, text=str(""), scale=1, color=WHITE, x=indent_change, y=indent_top)
label_stock2_change = label.Label(font, text=str(""), scale=1, color=WHITE, x=indent_change, y=(indent_top + vert_spacing))
label_stock3_change = label.Label(font, text=str(""), scale=1, color=WHITE, x=indent_change, y=(indent_top + vert_spacing*2) )
label_stock4_change = label.Label(font, text=str(""), scale=1, color=WHITE, x=indent_change, y=(indent_top + vert_spacing*3) )
label_stock5_change = label.Label(font, text=str(""), scale=1, color=WHITE, x=indent_change, y=(indent_top + vert_spacing*4) )
label_stock6_change = label.Label(font, text=str(""), scale=1, color=WHITE, x=indent_change, y=(indent_top + vert_spacing*5) )
label_stock7_change = label.Label(font, text=str(""), scale=1, color=WHITE, x=indent_change, y=(indent_top + vert_spacing*6) )
label_stock8_change = label.Label(font, text=str(""), scale=1, color=WHITE, x=indent_change, y=(indent_top + vert_spacing*7) )
label_stock9_change = label.Label(font, text=str(""), scale=1, color=WHITE, x=indent_change, y=(indent_top + vert_spacing*8) )

pricedata_group.append(label_stockname1)
pricedata_group.append(label_stockname2)
pricedata_group.append(label_stockname3)
pricedata_group.append(label_stockname4)
pricedata_group.append(label_stockname5)
pricedata_group.append(label_stockname6)
pricedata_group.append(label_stockname7)
pricedata_group.append(label_stockname8)
pricedata_group.append(label_stockname9)
pricedata_group.append(label_stock1_price)
pricedata_group.append(label_stock2_price)
pricedata_group.append(label_stock3_price)
pricedata_group.append(label_stock4_price)
pricedata_group.append(label_stock5_price)
pricedata_group.append(label_stock6_price)
pricedata_group.append(label_stock7_price)
pricedata_group.append(label_stock8_price)
pricedata_group.append(label_stock9_price)
pricedata_group.append(label_stock1_change)
pricedata_group.append(label_stock2_change)
pricedata_group.append(label_stock3_change)
pricedata_group.append(label_stock4_change)
pricedata_group.append(label_stock5_change)
pricedata_group.append(label_stock6_change)
pricedata_group.append(label_stock7_change)
pricedata_group.append(label_stock8_change)
pricedata_group.append(label_stock9_change)

display.show(pricedata_group)

def getprice(asset, pricelabel, changelabel):
    try:
        response = requests.get(URL_BASE + asset + URL_APIKEY + secrets["api_key"] + URL_FORMAT)
        response_json = response.json()

        price_unformatted = float(response_json["close"])
        price_delta_unformatted = float(response_json["change_p"])    # get the percentage change, which can be many decimal places

        price = "%.2f" % price_unformatted                            # Create a string from a float and round the price to 2 decimal places
        price_delta = "%.1f" % price_delta_unformatted                # Create a string from a float and round the price to 2 decimal places 

        #price_delta = round(price_delta_unformatted, 1)              # Round the percentage change 1 decimal place

        if price_delta_unformatted >= 0:
            pricelabel.color = GREEN
            changelabel.color = GREEN
        else:
            pricelabel.color = RED
            changelabel.color = RED
        pricelabel.text = price
        changelabel.text = price_delta + "%"

    except (ValueError, RuntimeError) as e:
        print("Error occurred when requesting data from server, retrying in 60 seconds. -", e)
        print("Resetting esp32")
        esp32.reset()
        time.sleep(60)


######## MAIN LOOP #####################################################################
while True:
    getprice(secrets["stock1"], label_stock1_price, label_stock1_change)
    getprice(secrets["stock2"], label_stock2_price, label_stock2_change)
    getprice(secrets["stock3"], label_stock3_price, label_stock3_change)
    getprice(secrets["stock4"], label_stock4_price, label_stock4_change)
    getprice(secrets["stock5"], label_stock5_price, label_stock5_change)
    getprice(secrets["stock6"], label_stock6_price, label_stock6_change)
    getprice(secrets["stock7"], label_stock7_price, label_stock7_change)
    getprice(secrets["stock8"], label_stock8_price, label_stock8_change)
    getprice(secrets["stock9"], label_stock9_price, label_stock9_change)

    num_loops += 1
    print("Loops=" + str(num_loops) )
    time.sleep(60)
