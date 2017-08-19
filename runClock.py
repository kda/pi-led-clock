#!/usr/bin/env python

import time
import signal
#from neopixel import *
import neopixel

#def Color(red, green, blue):
#    return red << 16 | green << 8 | blue

def decodeColor(rgb):
    return [rgb >> 16, rgb >> 8 & 0xFF, rgb & 0xFF]

LED_COUNT      = 50      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

HIGH_POWER = 10

C_BLACK = neopixel.Color(0, 0, 0)
C_RED = neopixel.Color(HIGH_POWER, 0, 0)
C_ORANGE = neopixel.Color(HIGH_POWER, (0x45 * HIGH_POWER)/LED_BRIGHTNESS, 0)
C_YELLOW = neopixel.Color((0x33 * HIGH_POWER)/LED_BRIGHTNESS, (0x33 * HIGH_POWER)/LED_BRIGHTNESS, 0)
C_GREEN = neopixel.Color(0, HIGH_POWER, 0)
C_BLUE = neopixel.Color(0, 0, HIGH_POWER)
C_INDIGO = neopixel.Color((0x4B * HIGH_POWER)/LED_BRIGHTNESS, 0, (0x82 * HIGH_POWER)/LED_BRIGHTNESS)
C_VIOLET = neopixel.Color((0xEE * HIGH_POWER)/LED_BRIGHTNESS, (0x82 * HIGH_POWER)/LED_BRIGHTNESS, (0xEE * HIGH_POWER)/LED_BRIGHTNESS)
C_WHITE = neopixel.Color(HIGH_POWER, HIGH_POWER, HIGH_POWER)

strip = 0

def allOff(strip):
    color = neopixel.Color(0, 0, 0)
    for i in range(LED_COUNT):
        strip.setPixelColor(i, color)
    strip.show()

def singleLight(strip, index, color):
    strip.setPixelColor(index, color)
    strip.show()


blackAndWhite = [C_BLACK, C_WHITE]
roygbiv = [
    C_BLACK,
    C_RED,
    C_ORANGE,
    C_YELLOW,
    C_GREEN,
    C_BLUE,
    C_INDIGO,
    C_VIOLET,
    C_WHITE,
    ]
blackAndRed = [C_BLACK, C_RED]

colorRange = blackAndRed

pixels = [
        [36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47],
        [24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35],
        [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
        [ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11],
        ]

centerPixel = 48

def selectColor(colors, numerator, denominator):
    #print numerator, '/', denominator
    #print colors
    colorCount = len(colors) - 1
    if (colorCount == 0):
        print "ERROR: not enough colors (", colors, ")"
        exit
    fromIndex = (colorCount * numerator) / denominator
    toIndex = fromIndex + 1
    #print fromIndex, toIndex
    fromColor = decodeColor(colors[fromIndex])
    toColor = decodeColor(colors[toIndex])
    #print fromColor, toColor
    targetColor = []
    rationalized_denominator = denominator / colorCount
    rationalized_numerator = numerator % rationalized_denominator
    for i in range(len(fromColor)):
        diff = toColor[i] - fromColor[i]
        adjustment = (diff * rationalized_numerator) / rationalized_denominator
        targetColor.append(fromColor[i] + adjustment)
    return neopixel.Color(targetColor[0], targetColor[1], targetColor[2])

def displayHand(index, color, length):
    global strip
    for i in range(length):
        print 'setPixel: index=%d color=%06x' % (pixels[i][index], color)
        singleLight(strip, pixels[i][index], color)

def displayShortHand(index, color):
    displayHand(index, color, 2)

def displayLongHand(index, color):
    displayHand(index, color, 4)

def displayHour(timeStruct):
    hour = timeStruct[3]
    minute = timeStruct[4]
    zero = (hour + 11) % 12
    primary = hour % 12
    secondary = (hour + 1) % 12
    #print primary, secondary
    colorRangeReverse = list(colorRange)
    colorRangeReverse.reverse()
    primaryColor = selectColor(colorRangeReverse, minute, 60)
    secondaryColor = selectColor(colorRange, minute, 60)
    print "displayHour primary:", primary
    displayShortHand(primary, primaryColor)
    print "displayHour secondary:", secondary
    displayShortHand(secondary, secondaryColor)
    #print '%06x %06x' % (primaryColor, secondaryColor)

def displayMinute(timeStruct):
    #print timeStruct[4]
    minute = timeStruct[4]
    second = timeStruct[5]
    zero = ((minute + 55) / 5) % 12
    primary = (minute / 5) % 12
    secondary = (((minute + 5)/ 5) % 12)
    #print primary, secondary
    colorRangeReverse = list(colorRange)
    colorRangeReverse.reverse()
    secondsElapsed = ((minute % 5) * 60) + second
    primaryColor = selectColor(colorRangeReverse, secondsElapsed, 300)
    secondaryColor = selectColor(colorRange, secondsElapsed, 300)
    displayLongHand(zero, C_BLACK)
    print "displayMinute primary:", primary
    displayLongHand(primary, primaryColor)
    print "displayMinute secondary:", secondary
    displayLongHand(secondary, secondaryColor)
    #print '%06x %06x' % (primaryColor, secondaryColor)

def displayTime(timeStruct):
    global strip
    #print timeStruct[3]
    #print timeStruct[4]
    #print timeStruct[5]
    displayMinute(timeStruct)
    displayHour(timeStruct)
    strip.show()
#    print timeStruct['tm_hour']
#    print timeStruct['tm_min']
#    print timeStruct['tm_sec']



def main():
    global strip
    strip = neopixel.Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
    strip.begin()
    allOff(strip)

    def signalHandler(signal, frame):
        #print('You pressed Ctrl+C!')
        allOff(strip)
        sys.exit(0)
    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)

    theTime = time.time()
    while True:
        timeStruct = time.localtime(theTime)
        print time.asctime(timeStruct)
        displayTime(timeStruct)
        time.sleep(1)
        theTime = time.time()
        #theTime = theTime + 60

##     strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
##     strip.begin()
## 
##     singleLight(strip, 0, C_RED)
##     singleLight(strip, 1, C_ORANGE)
##     singleLight(strip, 2, C_YELLOW)
##     singleLight(strip, 3, C_GREEN)
##     singleLight(strip, 4, C_BLUE)
##     singleLight(strip, 5, C_INDIGO)
##     singleLight(strip, 6, C_VIOLET)
##     time.sleep(5)
## 
##     print "hello, world!"
##     allOff(strip)

if __name__ == "__main__":
    main()
