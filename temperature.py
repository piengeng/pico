from machine import ADC
import utime

conversion_factor = 3.3 / 65536  # 2**16 / 2<<15
offset = 7.30 + 27


def loop():
    mean = 0
    while True:
        reading = ADC(4).read_u16() * conversion_factor
        # The temperature sensor measures the Vbe voltage of a biased bipolar diode, connected to the fifth ADC channel
        # Typically, Vbe = 0.706V at 27 degrees C, with a slope of -1.721mV (0.001721) per degree.
        temperature = offset - (reading - 0.706) / 0.001721

        # to smooth out readings
        mean = (mean + temperature) / 2 if mean != 0 else temperature

        print(temperature, mean)
        utime.sleep(2)


# rshell --buffer-size=512 -p /dev/ttyACM0
# cp temperature.py /pyboard/
# from temperature import loop
