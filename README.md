# Toolbox for Comparing Methods for Scheduling Offset-Free Systems

**Authors:** Yuri Hérouard, Matheus Ladeira

**Advisor:** Emmanuel Grolleau

**Contributors:** Fabien Bonneval, Gautier Hattenberger, Yassine Ouhammou

**Institution:** LIAS (ISAE-ENSMA, Université de Poitiers) - France


## Requirements

**Python Version:** 3.9 or greater. [Download and install Python](https://www.python.org/downloads/)

The use of a virtual environment can avoid issues with package dependencies:

```sh
python -m venv ./venv-name
source venv-name/bin/activate
```

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
- lxml
- docplex
- ortools
- z3

*To install DRS:

```sh
pip install git+https://github.com/dgdguk/drs.git#egg=drs
```

To install other modules:

```sh
pip install -r requirements.txt
```

## How to Compare Methods

1. Download an XML file from the Paparazzi project containing message periods. By default, we use [`default_rotorcraft.xml`](https://github.com/paparazzi/paparazzi/blob/master/conf/telemetry/default_rotorcraft.xml), already provided in the repository (hence, the download step can be skipped). The file must then be put in the root folder of the project (same path as `probabilityFromXml.py`).

2. Check the parameters and execute `probabilityFromXml.py`. Its parameters are described further in this document. To execute it, in the root folder of the project, run:

```sh
python probabilityFromXml.py
```

This will create a file containing the necessary information (prime factor distribution) for generating task periods. The information will be stored in the file `default_rotorcraft_xmlMatrix.csv` (created in the root folder), which will be used in the next step.

3. Check the parameters and execute `offsetAssignmentAnalysis.py` . Its parameters are described further in this document. To execute it, in the root folder of the project, run:

```sh
python offstAssignmentAnalysis.py
```

Once the calculations are complete, this will create the folder `res_filtered_NxTt_UX_YY_MM_DD_HHhMM` with files containing the results of the experiment (where *N* is the number of sets, *T* is the number of tasks in each set, *X* is the desired utilization of each task set, *YY_MM_DD* is the year-month-day representation of the current day, and *HHhMM* the Hour and Minutes representation of the current time). The folder will contain the plots representing the results of the simulation, as described in the published article, and a `log.txt` file containing the time it took to calculate the offsets for each method.

For experiments using the same prime factor distribution to generate random task sets, once steps 1 to 3 are executed, only step 3 has to be repeated.

### Parameters

#### `probabilityFromXml.py`

- *input_xmlFileName*: Name of the file from which prime factors will be extracted.
- *grmax*: Granularity of the prime factor distribution. Chances of a certain factor appearing will be rounded to the nearest rational number having the granularity as the denominator.

#### `offsetAssignmentAnalysis.py`

- *factorMatrixFile*: Name of the CSV file containing the matrix of period factors for task generation. Standard value: *default_rotorcraft_xmlMatrix.csv*
- *outputFolderRoot*:Root to be used when generating folders containing the results. Standard value: *res*
- *filterSets*: Boolean indicating whether to analyse only semi-harmonic sets (*True*) or not (*False*). Standard value: *True*
- Other boolean variables: Indicate which methods will be analysed.
- *numberSets*: Number of sets to be generated and evaluated.
- *numberTasks*: Number of periodic tasks/messages in each set.
- *U_target*: Target utilisation value for each set.
- *optimTimeLimit*: In case optimization toolboxes are used, defines the maximum amount of time allowed for each of them to calculate the offsets for each set.


### Experiments in the published article

- Using the default XML file, `offsetAssignmentAnalysis.py` is set with default values. Methods analysed (boolean variables set to *True*) are: `heur_new`, `heur_goossensCoupled`, `heur_can` and `heur_paparazzi` (the other methods are set to *False*). *numberSets* is set to 1000.
Data in Table 1 was obtained from the `log.txt` files created after running experiments 1000x8t_U70 and 1000x16t_U70.
Experiments in figures 6 to 9 are made according to the following table:

**Experiment** | **Figure** | **`numberTasks`** | **`U_target`**
--- | --- | --- | ---
1000x8t_U70 | 6 | 8 | 0.7
1000x8t_U95 | 7 | 8 | 0.95
1000x16t_U70 | 8 | 16 | 0.7
1000x16t_U95 | 9 | 16 | 0.95

Figure 10 is obtained gathering data from `log.txt` files in experiments such as the ones above, but with *numberTasks* set to 8 and *U_target* set to 0.5, 0.6, 0.7, 0.8, 0.9, 0.95 and 0.98. Figure 11 is obtained in a
similar way, but with *numberTasks* set to 16.


## How to Analyse Use-case

1. Make sure the file with message periods is in the main folder.

1. Analyse `case_offsetAssignmentAnalysis.py`, making sure input parameters are adequate, including the message sizes (line 131) and forced offsets (line 173), which have to be inserted manually in the code. Default values are already provided.

1. Execute `case_offsetAssignmentAnalysis.py`. To execute it, in the root folder of the project, run:

```sh
python case_offsetAssignmentAnalysis.py
```

Results will be put in the folder `paparazziAnalysis`. Results are written in a similar way as the ones for when running `offsetAssignmentAnalysis.py`.

### Input Parameters

#### `case_offsetAssignmentAnalysis.py`

Similar to `offsetAssignmentAnalysis.py`, without those relative to generating task sets, and adding:

- *input_xmlFileName*: XML file containing message periods to be analysed.

### Experiments in the published article

For generating Figure 12, we use `paparazzi_case3_tasks.xml`, provided in the root folder of the project. Other parameters are the same as in the other experiments.

Figures 13 and 14 cannot be reproduced using this artefact.
