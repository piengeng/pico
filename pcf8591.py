#!/usr/bin/python3 -u
import math
from smbus2 import SMBus  # type: ignore
from time import sleep
from datetime import datetime
from pathlib import Path
import csv


def getLevel(bus_, address_, controlByteInHex):
    # workaround for On-chip track and hold circuit
    bus_.read_byte_data(address_, controlByteInHex)
    return bus_.read_byte_data(address_, controlByteInHex)


def ratio(adc_value, denominator=255.0):
    return adc_value / denominator


def invert_percent(adc_value, denominator=255.0):
    return (1 - adc_value / denominator) * 100


def percent(adc_value, denominator=255.0):
    return adc_value / denominator * 100


def trm(f, points=2):
    return f"%.{points}f" % f


def celcius(value):
    # the problem with buying modules without schematics and datasheet, sigh~
    # Vref -> R10k(R4, 10kOhm) -> AIN2 -> Rth(R6, MF58, 10kOhm, B~3650) -> GND
    Beta = 3650
    R10k = 10000
    K0 = 273.15
    level = ratio(value)
    # Vref = 5 # Vth = ratio * Vref
    # Rth via voltage divider formula
    Rth = (level * R10k) / (1 - level)
    # https://en.wikipedia.org/wiki/Thermistor#B_or_%CE%B2_parameter_equation
    invT0 = 1 / (25 + K0)
    invB0 = math.log(Rth / R10k) / Beta
    Kth = 1 / (invT0 + invB0)
    Cth = Kth - K0
    return trm(Cth, 1)


def brightness(value):
    return trm(invert_percent(value), 1)


def divider(value):
    return trm(percent(value), 1)


def looper(to_screen=True):
    while True:
        t = celcius(getLevel(bus, address, A2))
        ldr = brightness(getLevel(bus, address, A1))
        pm = divider(getLevel(bus, address, A0))
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if to_screen:
            print(
                f"{dt} thermistor({t}°C), photoresistor({ldr}%), potentiometer({pm}%)"
            )
            sleep(1)
        else:
            csvfile = Path(__file__).parent / 'sensors.csv'
            with open(csvfile, mode='a') as f:
                writer = csv.writer(f,
                                    delimiter=',',
                                    quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)
                writer.writerow([dt, t, ldr, pm])
            sleep(20)


if __name__ == '__main__':
    channel = 1
    address = 0x48
    bus = SMBus(channel)
    A0 = 0x00  # potentiometer
    A1 = 0x01  # Light Dependent Resistor 0=brighter, 255=darker
    A2 = 0x02  # thermistor 0=hotter, 255=colder
    A3 = 0x03  # no connection
    try:
        looper(to_screen=False)

    except KeyboardInterrupt:
        print("ended by keyboard")
        pass
