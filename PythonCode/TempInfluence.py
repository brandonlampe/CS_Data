import numpy as np
import sys
import os
import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from matplotlib.ticker import FuncFormatter
from scipy import interpolate
# from scipy import optimize
from scipy import linalg
from scipy.stats.stats import pearsonr
# import lmfit

# relative path to module
sys.path.append(sys.path[0])
import DataAnalysisFunc as daf
REPO_DIR = os.path.dirname(sys.path[0])  # PATH TO REPOSITORY DIRECTORY

##################################
# CHOOSE ANALYSIS OPTIONS
##################################
PLOT = 0
SAVEFIG = 0
SAVECSV = 1
PLOT_RESID = 0
PLOT_CSMOD = 0  # PLOT RESULTS FROM CS MODEL, MUST DEFINE FILE TO LOAD DATA
STAGE_ID = ''  # IF TEST CONSISTS OF MULTIPLE STAGES

DUR_START = 0  # START PLOTTING (days)
DUR_END = 12  # END PLOTTING (days)
INTERP_INC = 10  # SECONDS, SIZE OF INTERPOLATION INCREMENT

FOLDER_DIR = 'UNM_WP_HY_175_04'

# load tests data - .csv file that has been exported directly from .xlsx
TEST_NAME = FOLDER_DIR[-6:] + '_TempAdj'

# DEFINE COLUMNS FOR:
# 'UNM_WP_HY_175_09'
COL_TIME = 0
COL_TEMP = 1
COL_FDEN = 2

IMPORT_FNAME = REPO_DIR + '/' + FOLDER_DIR + '/' + TEST_NAME + '.csv'
print("File Path: " + IMPORT_FNAME)

# Import .csv file and save it as an array: IMPORT_ARR
IMPORT_ARR = np.genfromtxt(fname=IMPORT_FNAME, delimiter=',', skip_header=1,
                           dtype=float)

# define vectors containing all rows a selected clumns, noted with "ALL"
TIME_ALL = daf.xldate_to_datetime(IMPORT_ARR[:, COL_TIME])
TIME_SHIFT = datetime.timedelta(days=DUR_START)
TIME_START = TIME_ALL[0] + TIME_SHIFT

print("Time of analysis start: " + TIME_START.strftime('%Y/%m/%d %H:%M:%S.%f').rstrip('0'))
DUR_DAY_ALL = daf.duration(IMPORT_ARR[:, COL_TIME])  # ALL DURATION DATA
FDEN_ALL = IMPORT_ARR[:, COL_FDEN]  # NO TIME AVERAGEING
TEMP_ALL = IMPORT_ARR[:, COL_TEMP]

# define a subset of data, identified by DUR_START and DUR_END
# if the defined duration limits are changed, so will these values
IDX_MAX = daf.find_nearest(DUR_DAY_ALL, DUR_END)  # IDX, MAX. DUR VALUE
IDX_MIN = daf.find_nearest(DUR_DAY_ALL, DUR_START)  # IDX, MIN. DUR VALUE
DUR_DAY = DUR_DAY_ALL[IDX_MIN:IDX_MAX]

IDX_FIT_MIN = daf.find_nearest(DUR_DAY, 2.63)  # IDX, MAX. DUR VALUE
IDX_FIT_MAX = daf.find_nearest(DUR_DAY, 2.67)  # IDX, MIN. DUR VALUE

DUR_SEC = DUR_DAY * 24 * 3600
FDEN = FDEN_ALL[IDX_MIN:IDX_MAX]
TEMP = TEMP_ALL[IDX_MIN:IDX_MAX]

# time measures needed for interpolation
# INTERP values are evenly spaced time intervals, accounts for variable sample
# spacing
DUR_DAY_LEN = (DUR_END - DUR_START)  # scalar value, days
DUR_SEC_LEN = DUR_DAY_LEN * 24 * 3600  # scalar value, SECONDS
INTERP_NUM = int(DUR_SEC_LEN / INTERP_INC) + 1  # NUM. OF INTERPOLATION
print("INTERP NUM: " + str(INTERP_NUM))
DUR_DAY_INTERP = np.linspace(DUR_START, DUR_END, num=INTERP_NUM, endpoint=True)
DUR_SEC_INTERP = DUR_DAY_INTERP * 24 * 3600

# functionS for interpolating the fractional density
FUNC_FDEN_INTERP = interpolate.interp1d(DUR_DAY_ALL, FDEN_ALL)
FUNC_TEMP_INTERP = interpolate.interp1d(DUR_DAY_ALL, TEMP_ALL)

# vectors OF interpolated values
FDEN_INTERP = FUNC_FDEN_INTERP(DUR_DAY_INTERP)
TEMP_INTERP = FUNC_TEMP_INTERP(DUR_DAY_INTERP)

TEMP_AVG_C = np.mean(TEMP_INTERP)
print('Avg. Temperature (C): ' + str(TEMP_AVG_C))

FIT_FDEN_TIME = np.polyfit(DUR_DAY_INTERP[IDX_FIT_MIN:IDX_FIT_MAX],
                           FDEN_INTERP[IDX_FIT_MIN:IDX_FIT_MAX],
                           deg=1, full=False)
FIT_TEMP_TIME = np.polyfit(DUR_DAY_INTERP[IDX_FIT_MIN:IDX_FIT_MAX],
                           TEMP_INTERP[IDX_FIT_MIN:IDX_FIT_MAX],
                           deg=1, full=False)
FIT_FDEN_TEMP = np.polyfit(TEMP_INTERP[IDX_FIT_MIN:IDX_FIT_MAX],
                           FDEN_INTERP[IDX_FIT_MIN:IDX_FIT_MAX],
                           deg=1, full=False)

TEMP_SMOOTH = daf.savitzky_golay(TEMP_INTERP, window_size=201,
                                 order=2, deriv=0)
DTEMP_SMOOTH = daf.savitzky_golay(TEMP_INTERP, window_size=201,
                                  order=2, deriv=1)
DTEMP = np.gradient(TEMP_INTERP)

print("FDEN - TIME RELATION: " + str(FIT_FDEN_TIME[0]))
print("TEMP - TIME RELATION: " + str(FIT_TEMP_TIME[0]))
print("DFDEN/DTEMP RELATION: " + str(FIT_FDEN_TIME[0] / FIT_TEMP_TIME[0]))

# TEST = FDEN_INTERP + .025 * DTEMP
TIME_FIT = np.linspace(DUR_START, DUR_END)
FDEN_FIT = FIT_FDEN_TIME[0] * TIME_FIT + FIT_FDEN_TIME[1]
TEMP_FIT = FIT_TEMP_TIME[0] * TIME_FIT + FIT_TEMP_TIME[1]

FDEN_ADJ = FDEN_INTERP + np.cumsum(DTEMP) * (0.0016)
# plt.figure(0)
# plt.plot(DUR_DAY_INTERP, FDEN_INTERP)
# plt.plot(TIME_FIT, FDEN_FIT, 'g-')
# plt.grid()

# plt.figure(1)
# plt.plot(DUR_DAY_INTERP, TEMP_INTERP)
# plt.plot(TIME_FIT, TEMP_FIT, 'r-')
# plt.grid()

# plt.plot(DUR_DAY_ALL, FDEN_ALL)
# plt.plot()
# plt.ylim(ymin=0.935, ymax=0.98)
# plt.grid()

plt.plot(DUR_DAY_INTERP, FDEN_ADJ, 'r-')
plt.plot(DUR_DAY_INTERP, FDEN_INTERP, 'g-')
# plt.ylim(ymin=0.935, ymax=0.98)
plt.grid()

plt.show()
