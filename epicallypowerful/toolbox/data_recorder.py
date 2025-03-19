import os
import time
import threading
import warnings

DELIMS = {
    'comma':',',
    'tab':'\t',
    'space':' ',
    'semicolon':';',
    'pipe':'|'
}
EXTENSIONS = {
    ',':'.csv',
    '\t':'.txt',
    ' ':'.txt',
    ';':'.txt',
    '|':'.txt',
}

def write_to_file(fname, buffer, lock):
    with lock:
        with open(fname, 'a') as f:
            f.writelines(buffer)


def resample_data_file(fpath, sample_rate):
    """Takes a saved .csv file and resamples the data to a given frequency. This
    process will destroy the real-time stamps which will be replaced with perfect
    interval timestamps. Numeric values will be interpolated with a linear
    interpolator. Non-numeric columns will be intepolated with 'nearest' interpolation.

    Args:
        fpath (string): file path of original file

    Raises:
        NotImplementedError: Function not yet implemented
    """
    raise NotImplementedError


class DataRecorder():
    def __init__(self, file: str, headers: list, delimiter: str=',', overwrite: bool=False, time_as_relative: bool=True, buffer_limit: int=200, verbose: bool=False):
        """_summary_

        Args:
            file (str): The file path of the file to be saved. If the file already exists, a new file will be created with an incremented index.
            headers (list): A list of strings that will be used as the header for the file.
            delimiter (str, optional): Delimiter type to use. This is almost always ','. Defaults to ','.
            overwrite (bool, optional): Whether to overwrite a file with the same name as the provided file path if the file already exists. Defaults to False.
            time_as_relative (bool, optional): Whether the time recorded in the default `time` column should be relative to the first recording or device time. Defaults to True.
            buffer_limit (int, optional): The number of lines to add before writing to the file. if an error occurs during operation, it is likley that this many lines will be lost
                Passing ``None`` will not save any data to disk until :py:func:`finalize` is called. Defaults to 200.
            verbose (bool, optional): Whether to print out information about the file being created and saved to. Defaults to False.

        Raises:
            TypeError: Raises if the headers are not a valid list of strings.
            ValueError: Raises if the delimiter is not a valid delimiter.
        """
        self.time_as_relative = time_as_relative
        self.t0 = 0
        self.lines_written = 0
        self.prev_time = 0
        self.buffer = []
        self.buffer_len = 0
        self.buffer_limit = buffer_limit
        self.verbose = verbose
        self.lock = threading.Lock() # Lock for writing to file
        
        # Sanitize header inputs
        if type(headers) is not list:
            raise TypeError("header argument must a list of strings")
        else:
            self.headers = headers.copy()
            self.data_length = len(self.headers)
        self.headers.insert(0, 'time')

        # Sanitize Delimiters
        if delimiter in DELIMS.values():
            self.delimiter = delimiter
        elif delimiter in DELIMS.keys():
            self.delimiter = DELIMS[delimiter]
        else:
            raise ValueError(f"delimiter argument must be one of the following values:\n{list(DELIMS.keys())}")
        
        target_ext = EXTENSIONS[self.delimiter]


        file = os.path.abspath(file)

        basename = os.path.basename(file)
        directory = os.path.dirname(file)

        filename, file_ext = os.path.splitext(basename)

        if target_ext != file_ext and file_ext != '.txt':
            swapped_delims = dict((v,k) for k,v in DELIMS.items())
            warnings.warn(f"You are using {swapped_delims[delimiter]} delimiters with an {file_ext} extension. This may results in errors reading the file later. Please consider a more appropriate extension")

        os.makedirs(directory, exist_ok=True)

        if not overwrite:
            idx = 1
            while (os.path.isfile(file)):
                file = os.path.join(directory, f'{filename}_{idx}{file_ext}')
                idx += 1
    
        self.fullpath = file
        if self.verbose: print(f'Creating and saving to {self.fullpath}')
        self.file_handle = open(self.fullpath, 'w')
        self.file_handle.write(self.delimiter.join(self.headers)+'\n')
        self.file_handle.close()

        
   
    def save(self, input_data: list):
        """Saves the provided list as a new line in the text file. Data in list
        will be seperated by the delimiter specifed when the DataRecorder is 
        created.

        Args:
            input_data (list): the input data to be saved as a list of values
        """
        if len(input_data) != self.data_length:
            warnings.warn(f"INPUT DATA LENGTH NOT EQUAL ({len(input_data)}) TO EXPECTED COLUMNS ({self.data_length})")
        
        current_time = time.perf_counter()
        if (self.time_as_relative and self.lines_written==0):
            self.t0 = current_time

        record_time = (current_time - self.t0)

        self.buffer.append(f'{round(record_time,6)}{self.delimiter}{self.delimiter.join([str(value) for value in input_data])}\n')
        if self.buffer_limit != None: self.buffer_len += 1
        if self.buffer_len == self.buffer_limit:
            threading.Thread(target=lambda: write_to_file(self.fullpath, self.buffer)).start()
 
            self.buffer = []
            self.buffer_len = 0

        self.prev_time = record_time
        self.lines_written += 1

    def finalize(self):
        """Closes the file handle and ensures all data is written to the file.
        """
        write_to_file(self.fullpath, self.buffer)
        if self.verbose: print(f'Closing file {self.fullpath}')    


if __name__ == "__main__":
    from epicallypowerful.utils.clocking import LoopTimer
    from epicallypowerful.utils.jetson_performance import jetson_performance
    from epicallypowerful.utils.clocking import LoopTimer

    jetson_performance()
    looper = LoopTimer(300)
    recorder = DataRecorder('test_file.csv', ['x', 'y', 'z'], buffer_limit=None)
    t0 = time.perf_counter()
    while True:
        # if time.perf_counter() - t0 > 0.005:
        #     print("This part here Slow")
        # t0 = time.perf_counter()
        if looper.continue_loop():
            # if time.perf_counter() - t0 > 0.005:
            #     print("This part Slow")
            # t0 = time.perf_counter()
            recorder.save([1,2,3])
            # if time.perf_counter() - t0 > 0.005:
            #     print("This Other part Slow")
            # t0 = time.perf_counter()

