
import time
import argparse

from data_logging import DataLogger

class PGLogger(DataLogger):
    dtypes = {
        'timestamp': 'f8',
        'pressure': 'f8',
        'temperature': 'f8',
        'pressure_max': 'f8',
        'pressure_min': 'f8'
    }
    AUTO_SHUTDOWN_OFF = b'HC_AUTO_OFF\r'
    AUTO_SHUTDOWN_ON = b'HC_AUTO_ON\r'
    STREAM_ON = b'STREAM_ON\r'
    STREAM_OFF = b'STREAM_OFF\r'
    Q_UNIT_PRES = b'PRES_UNIT?\r'
    Q_UNIT_TEMP = b'TEMP_UNIT?\r'
    Q_FAULT = b'FAULT?\r'
    Q_TARE = b'TARE?\r'
    Q_ID = b'*IDN?\r'
    Q_TEMP = b'TEMP?\r'
    Q_MIN = b'MIN?\r'
    Q_MAX = b'MAX?\r'
    RST_MINMAX = b'MINMAX_RST\r'
    RST_FAULT = b'*CLS\r'

    def init(self, timeout=1):
        import serial
        self.pg = serial.Serial(self.port, baudrate=9600)
        self.pg.timeout = timeout
        if not self.pg.is_open:
            self.pg.open()
        self.pg.flushInput()

        self.pg.write(self.Q_ID)
        resp = self.read_resp()
        if resp:
            print('serial device {} found'.format(resp))
        else:
            raise RuntimeError('serial device could not be found!')

        self.pg.write(self.Q_FAULT)
        resp = self.read_resp()
        if resp:
            print('device reports fault {}'.format(resp))
        self.pg.write(self.RST_FAULT)

        self.pg.write(self.Q_UNIT_TEMP)
        resp = self.read_resp()
        print('temp units {}'.format(resp))

        self.pg.write(self.Q_UNIT_PRES)
        resp = self.read_resp()
        print('pressure units {}'.format(resp))

        self.pg.write(self.Q_TARE)
        resp = self.read_resp()
        print('tare {}'.format(resp))

        self.pg.write(self.AUTO_SHUTDOWN_OFF)

    def read(self):
        self.pg.write(self.STREAM_ON)
        self.pg.flushInput()
        timestamp, pressure, temperature = 0, 0, 0
        for sample in range(self.smoothing):
            resp = self.read_resp().split(' ')
            timestamp += time.time() / self.smoothing
            pressure += float(resp[0].split(',')[0]) / self.smoothing
            temperature += float(resp[-1].split(',')[0]) / self.smoothing
        self.pg.write(self.STREAM_OFF)
        self.pg.flushInput()

        self.pg.write(self.Q_MAX)
        pressure_max = float(self.read_resp().split(',')[0])
        self.pg.write(self.Q_MIN)
        pressure_min = float(self.read_resp().split(',')[0])
        self.pg.write(self.RST_MINMAX)
        return timestamp, pressure, temperature, pressure_max, pressure_min

    def parse(self, data):
        timestamp, pressure, temperature, pressure_max, pressure_min = zip(*data)
        return {
            'timestamp': timestamp,
            'pressure': pressure,
            'temperature': temperature,
            'pressure_max': pressure_max,
            'pressure_min': pressure_min
        }

    def read_resp(self):
        resp = self.pg.read_until(terminator=b'\r')
        return str(resp.strip(b'\r').decode('utf-8'))

    def close(self):
        print('closing device...')
        self.pg.write(self.STREAM_OFF)
        self.pg.write(self.AUTO_SHUTDOWN_ON)
        self.pg.flushOutput()
        self.pg.flushInput()

        self.pg.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Log data from Omega pressure gauge')
    parser.add_argument('outdir',
        help='''output directory for created datafiles''')
    parser.add_argument('--sample_rate', type=float, default=10,
        help='''sample rate in Hz (default=%(default)s''')
    parser.add_argument('--buffer_size', type=int, default=20,
        help='''number of samples to buffer before writing to a file''')
    parser.add_argument('--port', type=str, required=True, help='''serial port pressure gauge is connected to''')
    parser.add_argument('--smoothing', type=int, default=1, help='''number of samples to smooth over''')
    args = parser.parse_args()

    outdir = args.outdir
    sample_rate = args.sample_rate
    buffer_size = args.buffer_size
    port = args.port
    smoothing = args.smoothing

    pg_logger = PGLogger('PG', outdir=outdir, buffer_size=buffer_size, sample_rate=sample_rate, port=port, smoothing=smoothing)
    pg_logger.init()
    pg_logger.run()







