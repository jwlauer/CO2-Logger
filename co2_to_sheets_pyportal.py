import re
import time
import board
import busio
from digitalio import DigitalInOut
from analogio import AnalogIn
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font

from adafruit_esp32spi import adafruit_esp32spi
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
#import adafruit_requests as prequests
import adafruit_requests as requests

from secrets import secrets
#Define colors
YELLOW = 0xFFFF00
RED = 0xFF0000
GREEN = 0x00FF00
ORANGE = 0xFFA500
BLACK = 0x000000
BLUE = 0x0000FF
WHITE = 0xFFFFFF

def version_compare(version1, version2):
    def normalize(v):
        return [int(x) for x in re.sub(r'(\.0+)*$','', v).split(".")]
    return (normalize(version1) > normalize(version2)) - (normalize(version1) < normalize(version2))

def update_screen(number, message, outercolor, innercolor, bordersize, textcolor, messagecolor):
    cwd = ("/"+__file__).rsplit('/', 1)[0]
    display = board.DISPLAY


    # Make the display context
    splash = displayio.Group()
    display.show(splash)

    color_bitmap = displayio.Bitmap(display.width, display.height, 1)
    color_palette = displayio.Palette(1)
    color_palette[0] = outercolor  

    bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
    splash.append(bg_sprite)

    # Draw a smaller inner rectangle
    inner_bitmap = displayio.Bitmap(display.width-int(bordersize), display.height-int(bordersize), 1)
    inner_palette = displayio.Palette(1)
    inner_palette[0] = innercolor 
    inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=int(bordersize/2), y=int(bordersize/2))
    splash.append(inner_sprite)

    # Draw another label
    text_group = displayio.Group(scale=1, x=50, y=80)
    text = "This is a note to the user"
    font = bitmap_font.load_font(cwd+"/fonts/Arial-ItalicMT-23.bdf")
    text_area = label.Label(font, text=message, color=messagecolor)
    text_group.append(text_area)  # Subgroup for text scaling
    splash.append(text_group)
    
    # Draw a label
    text_group = displayio.Group(scale=2, x=50, y=200)
    #font = bitmap_font.load_font(cwd+"/fonts/Arial-ItalicMT-23.bdf")
    font = bitmap_font.load_font(cwd+"/fonts/Urbanist-Medium-75.bdf")
    text_area = label.Label(font, text=str(number), color=textcolor)
    text_group.append(text_area)  # Subgroup for text scaling
    splash.append(text_group)

def read_co2():
    code = b'\xFF\x01\x86\x00\x00\x00\x00\x00\x79'
    ser.readline()
    ser.write(code)
    time.sleep(1)
    response = ser.readline()
    co2 = 256*response[2]+response[3]
    print('Carbon Dioxide ppm = %s' % co2)
    return(co2)

esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

requests.set_socket(socket,esp)

if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
    print("ESP32 found and in idle mode")

# Get the ESP32 fw version number, remove trailing byte off the returned bytearray
# and then convert it to a string for prettier printing and later comparison
firmware_version = ''.join([chr(b) for b in esp.firmware_version[:-1]])
print("Firmware vers.", firmware_version)

print("MAC addr:", [hex(i) for i in esp.MAC_address])

assert version_compare(firmware_version, "1.3.0") >= 0, (
    "Incorrect ESP32 firmware version; >= 1.3.0 required.")

esp.wifi_set_network(secrets["entssid"].encode("ascii"))
esp.wifi_set_entusername(secrets["entusername"].encode("ascii"))
esp.wifi_set_entpassword(secrets["entpassword"].encode("ascii"))

#Use this for an enterprise wifi
#esp.wifi_set_entenable()
#time.sleep(3)
#while not esp.is_connected:
#    esp.wifi_set_entenable()
#    time.sleep(2)
#    print('.')

#Use this for a non-enterprise wifi
while not esp.is_connected:
    esp.connect_AP(secrets["ssid"], secrets["password"])
    time.sleep(2)
    print('*')

#    except RuntimeError as e:
#        print("could not connect to WPA IP, trying WPA ENT:", e)
#        time.sleep(2)
#        try:
#            esp.wifi_set_entenable()
#            time.sleep(2)
#            continue
#        except:
#            print("could not connect to WPA2 Enterprise AP, retrying")
#    continue

print("")
print("Connected to", str(esp.ssid, 'utf-8'), "\tRSSI:", esp.rssi)
print("My IP address is", esp.pretty_ip(esp.ip_address))

analog_in = AnalogIn(board.LIGHT)

ser = busio.UART(rx=board.D4,tx=board.D3)

while True:
    light = analog_in.value
    co2 = read_co2()
    #P1 = 1
    #P2 = 2
    #T1 = 10
    #T2 = 20
    #WaterLevelDifference = 4
    #battery = 3.3
    data = {}
    data['Light'] = light
    data['CO2'] = co2
    #data['Tatm'] = T1
    #data['PH2O'] = P2
    #data['TH2O'] = T2
    #data['Depth'] = WaterLevelDifference
    #data['Battery'] = battery
    gKey = secrets['gKey']
    gSheetKey = secrets['gSheetKey']
    data['Sheet_id'] = gSheetKey
    url = 'https://script.google.com/macros/s/'+gKey+'/exec'
    #import adafruit_requests as prequests
    header_data = { "content-type": 'application/json; charset=utf-8'}

    if co2 < 600:
        screencolor = GREEN
    elif co2 < 800:
        screencolor = BLUE
    elif co2 < 1000:
        screencolor = ORANGE
    else:
        screencolor = RED
        
    update_screen(co2,"This is a sensor reading",WHITE,screencolor,20,BLACK,WHITE)

    try:
        #pass
        #response = prequests.post(url, json=data)
        response = requests.post(url, headers = header_data, json = data)
    except:
        pass

    time.sleep(20)
