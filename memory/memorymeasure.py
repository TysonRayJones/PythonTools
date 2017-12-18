
_FIELDS = ['VmRSS', 'VmHWM', 'VmSize', 'VmPeak']


def get_memory():
    '''
    returns the current and peak, real and virtual memories
    used by the calling linux python process, in Bytes
    '''

    # read in process info
    with open('/proc/self/status', 'r') as file:
        lines = file.read().split('\n')

    # container of memory values (_FIELDS)
    values = {}

    # check all process info fields
    for line in lines:
        if ':' in line:
            name, val = line.split(':')

            # collect relevant memory fields
            if name in _FIELDS:
                values[name] = int(val.strip().split(' ')[0])  # strip off "kB"
                values[name] *= 1000  # convert to B

    # check we collected all info
    assert len(values)==len(_FIELDS)
    return values



if __name__ == '__main__':

    # a simple test
    print(get_memory())
    mylist = [1.5]*2**30
    print(get_memory())
    del mylist
    print(get_memory())

    
