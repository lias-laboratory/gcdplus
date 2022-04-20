# Toolbox for Comparing Methods for Scheduling Offset-Free Systems

**Authors:** Yuri Hérouard, Matheus Ladeira
**Institution:** LIAS (ISAE-ENSMA)


## Requirements

**Python Version:** 3.9
**Modules:** 

- drs*
- matplotlib
- numpy
- random
- csv
- math
- functools
- time
- datetime
- typing
- sys
- os
- itertools
- copy
- pathlib
- heapq

*To install DRS:

```sh
pip install git+https://github.com/dgdguk/drs.git#egg=drs
```

## How to Use

1. Execute `probabilityFromXml.py` in the presence of `default_rotorcraft.xml` (downloaded from [Paparazzi's GitHub](https://github.com/paparazzi/paparazzi/blob/master/conf/telemetry/default_rotorcraft.xml)). This will create the matrix for generating matrix periods. The matrix will be in the file `default_rotorcraft_xmlMatrix.csv`, which will be used in the next step.

1. Execute `offstAssignmentAnalysis.py`. Once the calculations are complete, this will create the folder `res_filtered_YY_MM_DD_HHhMM` with files containing the results of the experiment (where *YY_MM_DD* is the year-month-day representation of the current day, and *HHhMM* the Hour and Minutes representation of the current time).


## Changing Input Parameters

### `offstAssignmentAnalysis.py`

- *factorMatrixFile*: Name of the CSV file containing the matrix of period factors for task generation. Standard value: *default_rotorcraft_xmlMatrix.csv*
- *outputFolderRoot*: Root to be used when generating folders containing the results. Standard value: *res*
- *filterSets*: Boolean indicating whether to analyse only semi-harmonic sets (*True*) or not (*False*). Standard value: *True*
- Other boolean variables: Indicate which methods will be analysed.
- *numberSets*: Number of sets to be generated and evaluated.
- *numberTasks*: Number of periodic tasks/messages in each set.
- *U_target*: Target utilisation value for each set.
- *optimTimeLimit*: In case optimization toolboxes are used, defines the maximum amount of time allowed for each of them to calculate the offsets for each set.