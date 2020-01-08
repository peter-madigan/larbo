
import time
from datetime import datetime
import argparse
import h5py
import os
import errno
import filelock

def file_locking(func):
    def new_func(*args, **kwargs):
        lock = kwargs['filename'] + '.lock'
        with filelock.FileLock(lock):
            return func(*args, **kwargs)
    return new_func

class DataLogger(object):
    '''
    Base class for data logger

    To implement a data logger you must define:

        - ``dtype`` -> dict of dataset name, numpy type desc
        - ``init()`` -> (optional) put any setup code here
        - ``read()`` -> generates ``tuple`` of data values to store
        - ``parse()`` - > converts ``tuple`` of data values to dict of ``dataset name:value``

    A valid script using the custom data logger would then be:

    from <lib for custom logger> import CustomDataLogger
    logger = CustomDataLogger(<name>, outdir=<outdir>, buffer_size=100, sample_rate=1)
    logger.init()
    logger.run()

    '''

    dtypes = {}

    def __init__(self, name, outdir='./', buffer_size=1, sample_rate=1e6, **kwargs):
        self.name = name
        print('Creating new logger {}...'.format(self.name))
        self.outdir = outdir
        self.filename = self.gen_filename(self.outdir)
        print('Storing data at {}...'.format(self.filename))
        self.buffer_size = buffer_size
        self.buffer = []
        self.sample_rate = sample_rate
        print('buffer_size = {}'.format(self.buffer_size))
        print('sample_rate = {}Hz'.format(self.sample_rate))
        for arg,val in kwargs.items():
            setattr(self, arg, val)
            print('{} = {}'.format(arg, val))

    def init(self, *args, **kwargs):
        '''
        Method to be run before logging data
        Returns None

        '''
        raise NotImplementedError

    def read(self):
        '''
        Method to run each time you request a read
        Returns a tuple

        '''
        raise NotImplementedError
        return tuple()

    def parse(self, data):
        '''
        Method to run to convert list of tupled data to datasets
        Returns a dict of dataset_name:list

        '''
        raise NotImplementedError
        return dict()

    def close(self):
        '''
        Method to clean up system when exiting

        '''
        raise NotImplementedError

    def run(self):
        '''
        Collect data in a loop

        '''
        try:
            while True:
                self.buffer += [self.read()]
                print('\t'.join(['{}']*len(self.buffer[-1])).format(*self.buffer[-1]))
                if len(self.buffer) >= self.buffer_size:
                    print('updating {}...'.format(self.filename))
                    self.write(self.buffer, filename=self.filename)
                    self.buffer = []
                time.sleep(1./self.sample_rate)
        except:
            self.close()
            raise

    def gen_filename(self, directory):
        now = datetime.now()
        filename = now.strftime('{}_%Y-%m-%d_%H-%M-%S.h5'.format(self.name))
        return os.path.join(directory, filename)

    @file_locking
    def write(self, data, filename):
        if not os.path.isfile(filename):
            return self.create_new_file(data, filename)
        return self.append_to_file(data, filename)

    def create_new_file(self, data, filename):
        with h5py.File(filename,'w') as file:
            data_dict = self.parse(data)
            for dataset, dtype in self.dtypes.items():
                file.create_dataset(dataset, shape=(0,), maxshape=(None,), dtype=dtype)
                file[dataset].resize(len(data_dict[dataset]), axis=0)
                file[dataset][:] = data_dict[dataset]

    def append_to_file(self, data, filename):
        with h5py.File(filename,'a') as file:
            data_dict = self.parse(data)
            for dataset, values in data_dict.items():
                file[dataset].resize(len(file[dataset]) + len(values), axis=0)
                file[dataset][-len(values):] = values

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Example logger script')
    parser.add_argument('outdir',
        help='''output directory for created datafiles''')
    parser.add_argument('--sample_rate', type=float, default=5,
        help='''sample rate in Hz (default=%(default)s''')
    parser.add_argument('--buffer_size', type=int, default=50,
        help='''number of samples to buffer before writing to a file''')
    args = parser.parse_args()

    outdir = args.outdir
    sample_rate = args.sample_rate
    buffer_size = args.buffer_size

    logger = DataLogger('EX', outdir=outdir, buffer_size=buffer_size, sample_rate=sample_rate)
    logger.init()
    logger.run()
