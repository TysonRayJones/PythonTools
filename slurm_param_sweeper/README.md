# SLURM param sweeper

This python library generates SLURM submission scripts which launch multiple jobs to 'sweep' a given
set of parameters; that is, a job is run for every possible configuration of the params.

For example, you might have a script which accepts parameters `a`, `b` and `c`, which you call (passing `a=1`, `b=2`,
`c=3`) like
```bash
myscript.sh 1 2 3
```
inside a SLURM submission script.

Say that `a` can be any value in `[1, 2, 3]`, while `b` is in `[4, 5, 6]` and `c` is in `[7, 8, 9]`. 
How can you run `myscript.sh` once for every possible configuration of `a`, `b` and `c`?
Creating multiple submission scripts which each contain one of
```bash
myscript.sh 1 4 7
myscript.sh 1 4 8
myscript.sh 1 4 9
myscript.sh 1 5 7
...
myscript.sh 3 6 9
```
becomes impractible for many parameters. While you can use the SLURM field `--array=0-26` to launch multiple
jobs in a single script, writing bash code to map
`$SLURM_ARRAY_TASK_ID` to a unique `a`,`b`,`c` configuration can be tedious.
`param_sweeper.py` creates a single submission script which does this mapping for you.

-----------------

## example

`param_sweeper.py` exposes `get_script` and `save_script` which accept a list of SLURM fields (e.g. `job_name`) and 
a dictionary where each key is a parameter name and each item is a list of values the parameter can take.

For example,
```python
from param_sweeper import save_script

fields = {
    'memory': 8,
    'job_name': 'abc_sweep',
    'time_h': 1
}

params = {
    'a':[1, 2, 3],
    'b':[4, 5, 6],
    'c':range(7,10)
}

save_script('mysubmit.sh', fields, params)
```
creates a file `mysubmit.sh` containing
```bash
#!/bin/env bash

#SBATCH --array=0-26
#SBATCH --job-name=abc_sweep
#SBATCH --mem=8GB
#SBATCH --time=0-1:0:0

a_values=( 1 2 3 )
b_values=( 4 5 6 )
c_values=($( seq 7 1 10 ))

trial=${SLURM_ARRAY_TASK_ID}
a=${a_values[$(( trial % ${#a_values[@]} ))]}
trial=$(( trial / ${#a_values[@]} ))
b=${b_values[$(( trial % ${#b_values[@]} ))]}
trial=$(( trial / ${#b_values[@]} ))
c=${c_values[$(( trial % ${#c_values[@]} ))]}

## use ${a}, ${b}, ${c} below
```

which, after adding `myscript.sh $a $b $c` to the bottom, can be submitted to SLURM via `sbatch mysubmit.sh`.

-------------

## customisation

`param_sweeper.py` contains a constant `TEMPLATE` which should be edited to add/remove custom code in the 
generated submission script. For example, the template

```python
TEMPLATE = '''

#!/bin/env bash

#SBATCH --array=0-{num_jobs}
#SBATCH --job-name={job_name}
#SBATCH --output={output}
#SBATCH --mem={memory}{memory_unit}
#SBATCH --time={time_d}-{time_h}:{time_m}:{time_s}
#SBATCH --nodes={num_nodes}
#SBATCH --cpus-per-task={num_cpus}
#SBATCH --reservation={reserve}

{param_arr_init}

trial=${{SLURM_ARRAY_TASK_ID}}
{param_val_assign}

source ../../prep.sh
export OMP_NUM_THREADS={num_cpus}
export OMP_PROC_BIND=spread

## use {param_list} below
myscript.sh $a $b

'''.strip()
```
when combined with the default fields
```python
DEFAULT_SLURM_FIELDS = {
    'memory': 64,
    'memory_unit': 'GB',
    'num_nodes': 1,
    'num_cpus': 16,
    'time_d': 0, 'time_h': 0, 'time_m': 0, 'time_s': 0,
    'reserve': 'nqit',
    'job_name': 'myjob',
    'output': 'output.txt'
}
```
after calling
```python
script = get_script({}, {'a':range(100), 'b':range(100)})
print(script)
````
produces
```bash
#!/bin/env bash

#SBATCH --array=0-9999
#SBATCH --job-name=myjob
#SBATCH --output=output.txt
#SBATCH --mem=64GB
#SBATCH --time=0-0:0:0
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
#SBATCH --reservation=nqit

a_values=($( seq 0 1 100 ))
b_values=($( seq 0 1 100 ))

trial=${SLURM_ARRAY_TASK_ID}
a=${a_values[$(( trial % ${#a_values[@]} ))]}
trial=$(( trial / ${#a_values[@]} ))
b=${b_values[$(( trial % ${#b_values[@]} ))]}

source ../../prep.sh
export OMP_NUM_THREADS=16
export OMP_PROC_BIND=spread

## use ${a}, ${b} below
myscript.sh $a $b

```
--------------

## arguments

Both `get_script` (returns a string) and `save_script` (writes to file) accept an optional argument 
`param_order` which explicitly specifies in what order to sweep the given parameters.
E.g.
```python
get_script(
    {}, 
    {'a':range(10), 'b':range(10), 'c':range(10)},
    param_order=['c','a','b']
)
```
produces a submission script which contains 
```bash
c_values=($( seq 0 1 10 ))
a_values=($( seq 0 1 10 ))
b_values=($( seq 0 1 10 ))

trial=${SLURM_ARRAY_TASK_ID}
c=${c_values[$(( trial % ${#c_values[@]} ))]}
trial=$(( trial / ${#c_values[@]} ))
a=${a_values[$(( trial % ${#a_values[@]} ))]}
trial=$(( trial / ${#a_values[@]} ))
b=${b_values[$(( trial % ${#b_values[@]} ))]}
```
and which would launch jobs where `b` is iterated the fastest:
```bash
myscript.sh 0 0 0
myscript.sh 0 1 0
myscript.sh 0 2 0
...
myscript.sh 1 0 0
myscript.sh 1 1 0
...
```
