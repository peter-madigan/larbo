
import argparse
import time

from data_logging import DataLogger

class RTDLogger(DataLogger):
    dtypes = {
        'timestamp': 'f8',
        'resistance': 'f8',
        'temperature': 'f8'
    }

    def init(self):
        print('initializing RTD...')
        import board
        import busio
        import digitalio
        import adafruit_max31865

        SCK = board.SCK
        MOSI = board.MOSI
        MISO = board.MISO
        CE = board.CE0

        R_NOM = 100.0
        R_REF = 430.0

        spi = busio.SPI(SCK, MOSI=MOSI, MISO=MISO)
        cs = digitalio.DigitalInOut(CE)
        self.rtd = adafruit_max31865.MAX31865(spi, cs, rtd_nominal=R_NOM, ref_resistor=R_REF)

    def read(self):
        return time.time(), self.rtd.resistance, self.rtd.temperature

    def parse(self, data):
        timestamp, resistance, temperature = zip(*data)
        return {
            'timestamp': timestamp,
            'resistance': resistance,
            'temperature': temperature
        }

    def close(self):
        print('closing...')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Log data from drizzle\'s RTD')
    parser.add_argument('outdir',
        help='''output directory for created datafiles''')
    parser.add_argument('--sample_rate', type=float, default=5,
        help='''sample rate in Hz (default=%(default)s''')
    parser.add_argument('--buffer_size', type=int, default=25,
        help='''number of samples to buffer before writing to a file''')
    args = parser.parse_args()

    outdir = args.outdir
    sample_rate = args.sample_rate
    buffer_size = args.buffer_size

    rtd_logger = RTDLogger('RTD', outdir=outdir, buffer_size=buffer_size, sample_rate=sample_rate)
    rtd_logger.init()
    rtd_logger.run()







