
import argparse
import json
import time
from collections import OrderedDict

from data_logging import DataLogger

class ADCLogger(DataLogger):
    dtypes = {
        'timestamp': 'f8',
        'gain': 'f8'
    }

    def init(self):
        '''
        Requires the channel_spec and gain attributes to be set

        gain can be one of 2/3, 1, 2, 4, 8, 16

        channel_spec should be a list of dicts, each dict should be either::

            {'single': '<pin name>'}

        or::

            {'differential': ['<+ pin name>', '<- pin name>']}

        Valid pin names are 'P0', 'P1', 'P2', or 'P3'

        '''
        print('initializing ADC...')
        import board
        import busio
        import adafruit_ads1x15.ads1115 as ADS
        from adafruit_ads1x15.analog_in import AnalogIn

        i2c = busio.I2C(board.SCL, board.SDA)

        self.ads = ADS.ADS1115(i2c)

        self.ads.gain = self.gain
        print('gain set to {}...'.format(self.ads.gain))

        self.channels = OrderedDict()
        for spec in self.channel_spec:
            if 'single' in spec:
                print('declaring single-ended channel on {}...'.format(spec['single']))
                pin = getattr(ADS, spec['single'])
                self.channels['s{}'.format(spec['single'])] = AnalogIn(self.ads, pin)
            elif 'differential' in spec:
                print('declaring differential channel on {}, {}...'.format(*spec['differential']))
                pins = [getattr(ADS, pin) for pin in spec['differential']]
                self.channels['d{}{}'.format(*spec['differential'])] = AnalogIn(self.ads, ADS.P0, ADS.P1)

        for channel in self.channels:
            self.dtypes[channel] = 'f8'
            self.dtypes[channel+'_v'] = 'f8'

    def read(self):
        data = [0] * 2 * len(self.channels)
        for sample in range(self.smoothing):
            for i in range(2 * len(self.channels)):
                channel = list(self.channels.keys())[i//2]
                if i%2 == 0:
                    data[i] += self.channels[channel].value / self.smoothing
                elif i%2 == 1:
                    data[i] += self.channels[channel].voltage / self.smoothing
        return tuple([time.time()] + data + [self.gain])

    def parse(self, data):
        channel_data = list(zip(*data))
        return_dict = dict()
        return_dict['timestamp'] = channel_data[0]
        for i in range(2 * len(self.channels)):
            if i%2 == 0:
                channel = list(self.channels.keys())[i//2]
                return_dict[channel] = channel_data[i+1]
            elif i%2 == 1:
                channel = list(self.channels.keys())[i//2]+'_v'
                return_dict[channel] = channel_data[i+1]
        return_dict['gain'] = channel_data[-1]
        return return_dict

    def close(self):
        print('closing...')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Log data from drizzle\'s ADC')
    parser.add_argument('outdir',
        help='''output directory for created datafiles''')
    parser.add_argument('--sample_rate', type=float, default=2,
        help='''sample rate in Hz (default=%(default)s''')
    parser.add_argument('--buffer_size', type=int, default=10,
        help='''number of samples to buffer before writing to a file''')
    parser.add_argument('--gain', type=float, default=1,
        help='''gain setting for adc''')
    parser.add_argument('--smoothing', type=int, default=10,
        help='''number of samples to average together''')
    parser.add_argument('--channel_spec', type=json.loads, default='''[{"differential":["P0","P1"]}, {"single":"P2"}, {"single":"P3"}]''',
        help='''channel specification as formatted as json string, see ADCLogger.init for more details''')
    args = parser.parse_args()

    outdir = args.outdir
    sample_rate = args.sample_rate
    buffer_size = args.buffer_size
    gain = args.gain
    smoothing = args.smoothing
    channel_spec = args.channel_spec

    adc_logger = ADCLogger('ADC', outdir=outdir, buffer_size=buffer_size, sample_rate=sample_rate, channel_spec=channel_spec, gain=gain, smoothing=smoothing)
    adc_logger.init()
    adc_logger.run()







