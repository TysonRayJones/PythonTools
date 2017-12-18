### Measure memory of a Linux process in Python

The module

```python
from memorymeasure import get_memory
```
provides a single function `get_memory` which returns the current and peak, 
real and virtual memories (in bytes, accurate to ~kilobytes) used by your Python code's Linux process, 
in a dictionary. The same module but in C can be found [here](https://github.com/TysonRayJones/CTools/tree/master/memory).

Calling
```python
get_memory()
```
returns a dictionary with keys `VmHWM`, `VmPeak`, `VmRSS` and `VmSize`, e.g.
```python
{'VmHWM': 6436000, 'VmPeak': 122260000, 'VmRSS': 6436000, 'VmSize': 122244000}
```
though will raise a `FileNotFoundError` if ran on a non-linux machine.

--------------------

Real memory ([resident set size](https://en.wikipedia.org/wiki/Resident_set_size)) 
is the amount of physical RAM your process is using, and virtual memory is the size of 
the memory address space your process is using. Linux chooses what in your virtual memory gets to
reside in RAM. Note that in addition to your program data, these memories include the space taken 
up by your code itself, and any libraries your code 
is using (which may be shared by other running processes, skewing your usage). 
A good explanation can
be found [here](https://superuser.com/questions/618687/why-do-programs-on-linux-kernel-use-so-much-more-vmem-than-resident-memory).

Peak memory is the maximum amount of memory your process has used over its lifetime so far.

---------------------

This module works by reading `/proc/self/status` which linux populates with info about your running process.
It uses fields

| Output      | status Field  | Description  |
| ------------|:-------------:|:-------------|
| currRealMem | VmRSS  | Resident set size |
| peakRealMem | VmHWM  | Peak resident set size ("high water mark") |
| currVirtMem | VmSize | Virtual memory size |
| peakVirtMem | VmPeak | Peak virtual memory size |

taken from under /proc/[pid]/status on the [proc man page](https://linux.die.net/man/5/proc).
