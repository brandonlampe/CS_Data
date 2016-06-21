import sys
import numpy as np
import os
import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from matplotlib.ticker import FuncFormatter
from scipy import interpolate
# from scipy import optimize
from scipy import linalg
import pickle
# import lmfit

# relative path to module
sys.path.append(sys.path[0])
import DataAnalysisFunc as daf
REPO_DIR = os.path.dirname(sys.path[0])  # PATH TO REPOSITORY DIRECTORY

##################################
# CHOOSE ANALYSIS OPTIONS
##################################
RUN_FIT_FDEN = 1  # SHOULD THE FIT TO FDEN BE CALCULATED
ALTDOMAIN_FIT_FDEN = 1  # FIT FDEN TO AN ALTERNATE DOMAIN THAN DEFINED BY
  # DUR_START AND DUR_STOP
MODEL_TYPE = 5  # need to write summary of model types
PLOT = 1  # SHOULD THE RESULTS BE PLOTTED
SAVEFIG = 1  # SHOULD THE PLOTS BE SAVED
SAVECSV = 1  # SHOULD A .CSV OF THE RESULTS BE SAVED
PLOT_FITDATA = 1  # SHOULD RESIDUALS OF THE FIT BE PRINTED
PLOT_CSMOD = 0  # PLOT RESULTS FROM CS MODEL, MUST DEFINE FILE TO LOAD DATA
STAGE_ID = '_FitToDayNine'  # '_Stage01'  # IF TEST CONSISTS OF MULTIPLE STAGES
ADJUST_FOR_TEMP = 1  # MODIFY FDEN WHEN MEASURED WITH ISCO (TEMP. COMPENSATE)

# IF RESULTS FROM CS MODEL ARE TO BE PLOTTED ALSO, DEFINE PATH TO DATA
PATH_CSMOD = '/Users/Lampe/GrantNo456417/Modeling/constit/' + \
             'UNM_WP_HY_175_09_OUT' + '.csv'

# DUR_START = 2.096  # START PLOTTING (days)
# DUR_END = 2.9  # END PLOTTING (days)
DUR_START = 2.093  # START PLOTTING (days)
DUR_END = 19.9  # END PLOTTING (days)
ALT_START = 2.093
ALT_END = 9

# interpolation spacing
INTERP_INC = 10  # SECONDS, SIZE OF INTERPOLATION INCREMENT

# FOLDER_DIR = 'UNM_WP_HY_90_02'
# FOLDER_DIR = 'UNM_WP_HY_90_03'
# FOLDER_DIR = 'UNM_WP_HY_90_04'
# FOLDER_DIR = 'UNM_WP_HY_90_08'
# FOLDER_DIR = 'UNM_WP_HY_175_01'
# FOLDER_DIR = 'UNM_WP_HY_175_03'
FOLDER_DIR = 'UNM_WP_HY_175_04'
# FOLDER_DIR = 'UNM_WP_HY_175_09'

# load tests data - .csv file that has been exported directly from .xlsx
TEST_NAME = FOLDER_DIR[10:]  # + '_comp'
print(TEST_NAME)

# DEFINE COLUMN INDEX IN .CSV FILES
COL_TIME, COL_TEMP, COL_PCON, COL_PPOR, COL_FDEN = daf.column_idx(TEST_NAME)


RHOIS = 2160.0  # ASSUMED IN-SITU DENSITY (KG/M3), FOR STRAIN MEASURE
COL_MAX = max(COL_TIME, COL_TEMP, COL_PCON, COL_PPOR, COL_FDEN) + 1
USECOLS = (np.arange(0, COL_MAX, 1))
IMPORT_FNAME = REPO_DIR + '/' + FOLDER_DIR + '/' + TEST_NAME + '.csv'
print("File Path: " + IMPORT_FNAME)

# Import .csv file and save it as an array: IMPORT_ARR
IMPORT_ARR = np.genfromtxt(fname=IMPORT_FNAME, delimiter=',', skip_header=1,
                           usecols=USECOLS, dtype=float)

# define vectors containing all rows a selected clumns, noted with "ALL"
TIME_ALL = daf.xldate_to_datetime(IMPORT_ARR[:, COL_TIME])
TIME_SHIFT = datetime.timedelta(days=DUR_START)
TIME_START = TIME_ALL[0] + TIME_SHIFT

print("Time of analysis start: " + TIME_START.strftime('%Y/%m/%d %H:%M:%S.%f').rstrip('0'))
DUR_DAY_ALL = daf.duration(IMPORT_ARR[:, COL_TIME])  # ALL DURATION DATA
FDEN_ALL = IMPORT_ARR[:, COL_FDEN]  # NO TIME AVERAGEING
PCON_ALL = IMPORT_ARR[:, COL_PCON] / 145.0
TEMP_ALL = IMPORT_ARR[:, COL_TEMP]
if COL_PPOR == 0:
    PPOR_ALL = np.zeros(len(PCON_ALL))
else:
    PPOR_ALL = IMPORT_ARR[:, COL_PPOR] / 145.0

# define a subset of data, identified by DUR_START and DUR_END
# if the defined duration limits are changed, so will these values
if DUR_END > DUR_DAY_ALL[-1]:
    DUR_END = DUR_DAY_ALL[-1]
    print("DUR_END has been modified, Max. Duration = " +
          str(DUR_DAY_ALL[-1]) + " days")

IDX_MAX = daf.find_nearest(DUR_DAY_ALL, DUR_END)  # IDX, MAX. DUR VALUE
IDX_MIN = daf.find_nearest(DUR_DAY_ALL, DUR_START)  # IDX, MIN. DUR VALUE
DUR_DAY = DUR_DAY_ALL[IDX_MIN:IDX_MAX]
DUR_SEC = DUR_DAY * 24 * 3600
FDEN = FDEN_ALL[IDX_MIN:IDX_MAX]
PCON = PCON_ALL[IDX_MIN:IDX_MAX]
PPOR = PPOR_ALL[IDX_MIN:IDX_MAX]
TEMP = TEMP_ALL[IDX_MIN:IDX_MAX]

# time measures needed for interpolation
# INTERP values are evenly spaced time intervals, accounts for variable sample
# spacing
DUR_DAY_LEN = (DUR_END - DUR_START)  # scalar value, days
DUR_SEC_LEN = DUR_DAY_LEN * 24 * 3600  # scalar value, SECONDS
INTERP_NUM = int(DUR_SEC_LEN / INTERP_INC) + 1  # NUM. OF INTERPOLATION inc
print("INTERP NUM: " + str(INTERP_NUM))
DUR_DAY_INTERP = np.linspace(DUR_START, DUR_END, num=INTERP_NUM, endpoint=True)
DUR_SEC_INTERP = DUR_DAY_INTERP * 24 * 3600

# functionS for interpolating the fractional density
FUNC_FDEN_INTERP = interpolate.interp1d(DUR_DAY_ALL, FDEN_ALL)
FUNC_PCON_INTERP = interpolate.interp1d(DUR_DAY_ALL, PCON_ALL)
FUNC_PPOR_INTERP = interpolate.interp1d(DUR_DAY_ALL, PPOR_ALL)
FUNC_TEMP_INTERP = interpolate.interp1d(DUR_DAY_ALL, TEMP_ALL)

# vectors OF interpolated values
FDEN_INTERP = FUNC_FDEN_INTERP(DUR_DAY_INTERP)
PCON_INTERP = FUNC_PCON_INTERP(DUR_DAY_INTERP)
PPOR_INTERP = FUNC_PPOR_INTERP(DUR_DAY_INTERP)
TEMP_INTERP = FUNC_TEMP_INTERP(DUR_DAY_INTERP)

# CALCULATE ALTERNATE FITTING DOMAIN IF
if ALTDOMAIN_FIT_FDEN == 1:
    ALT_DAY_LEN = (ALT_END - ALT_START)
    ALT_SEC_LEN = ALT_DAY_LEN * 24 * 3600
    ALT_INTERP_NUM = int(ALT_SEC_LEN / INTERP_INC) + 1
    ALT_DUR_DAY_INTERP = np.linspace(ALT_START, ALT_END, num=ALT_INTERP_NUM,
                                      endpoint=True)
    ALT_FDEN_INTERP = FUNC_FDEN_INTERP(ALT_DUR_DAY_INTERP)

if ADJUST_FOR_TEMP == 1:  # MODIFICATION TO FDEN MEASUREMENT FOR DELTA TEMP.
    MOD_FACT = 0.0016  # 1/DEGREE C
    DELTA_TEMP = np.gradient(TEMP_INTERP)
    # plt.plot(DUR_DAY_INTERP, FDEN_INTERP, 'g-', label='Original')
    FDEN_INTERP = FDEN_INTERP + np.cumsum(DELTA_TEMP) * MOD_FACT
    if ALTDOMAIN_FIT_FDEN == 1:
        ALT_TEMP_INTERP = FUNC_TEMP_INTERP(ALT_DUR_DAY_INTERP)
        ALT_DELTA_TEMP = np.gradient(ALT_TEMP_INTERP)
        ALT_FDEN_INTERP = ALT_FDEN_INTERP + \
            np.cumsum(ALT_DELTA_TEMP) * MOD_FACT
    print("FDEN was modified for changing temp. by: " +
          str(MOD_FACT) + " (1/DEGREE C)")
    # plt.plot(DUR_DAY_INTERP, FDEN_INTERP, 'r-', label='Adjusted')
    # plt.grid()
    # plt.legend(loc=0)
    # plt.show()

PCON_AVG_PSI = np.mean(PCON_INTERP) * 145
PCON_AVG_MPA = np.mean(PCON_INTERP)
PPOR_AVG_PSI = np.mean(PPOR_INTERP) * 145
PPOR_AVG_MPA = np.mean(PPOR_INTERP)
TEMP_AVG_C = np.mean(TEMP_INTERP)

print("Avg. Confining Pressure (MPa): " + str(PCON_AVG_MPA))
print("Avg. Pore Pressure (MPa): " + str(PPOR_AVG_MPA))
print("Avg. Confining Pressure (psi): " + str(PCON_AVG_PSI))
print("Avg. Pore Pressure (psi): " + str(PPOR_AVG_PSI))
print('Avg. Temperature (C): ' + str(TEMP_AVG_C))

# calculated volume strain rate by fitting model to fractional density
FDEN0 = FDEN_INTERP[0]  # INITIAL FRACTIONAL DENSITY

# CALCULATE VOLUME STRAIN AND VOLUME STRAIN RATE
VSTRN = -np.log(FDEN0 / FDEN)  # POSITIVE IN COMPRESSION
VSTRN_INTERP = -np.log(FDEN0 / FDEN_INTERP)  # POSITIVE IN COMPRESSION
DELTA_VSTRN = np.gradient(VSTRN)
DELTA_VSTRN_INTERP = np.gradient(VSTRN_INTERP)
DELTA_SEC = np.gradient(DUR_SEC)
DELTA_SEC_INTERP = np.gradient(DUR_SEC_INTERP)
VSTRN_RATE = DELTA_VSTRN / DELTA_SEC
VSTRN_RATE_INTERP = DELTA_VSTRN_INTERP / DELTA_SEC_INTERP

if RUN_FIT_FDEN == 1:
    if ALTDOMAIN_FIT_FDEN == 1:
        FIT_DOMAIN = ALT_DUR_DAY_INTERP
        FIT_RANGE = ALT_FDEN_INTERP
    else:
        FIT_DOMAIN = DUR_DAY_INTERP
        FIT_RANGE = FDEN_INTERP

    FDEN_FIT_INTERP, MODEL = daf.fit_fden(fden_interp=FIT_RANGE,
                                          dur_day_interp=FIT_DOMAIN,
                                          which_mod=MODEL_TYPE,
                                          whole_domain=DUR_DAY_INTERP)

    print(MODEL.best_values)
    print(MODEL.fit_report())
    print(MODEL.ci_out)

    FIT_REPORT = MODEL.fit_report()
    FIT_CI = MODEL.ci_out
    # FIT_RESID = MODEL.residual
    FIT_RESID = FDEN_FIT_INTERP - FDEN_INTERP
    # CALCULATED THE SCALED P-NORM (2)
    FIT_RESID_NORM = linalg.norm(FIT_RESID) / len(FIT_RESID)**(1. / 2)
    print("Scaled Error Norm of Fit: " + str(FIT_RESID_NORM))

    if PLOT_FITDATA == 1:
        FIG0, FITPLOT = plt.subplots(2, figsize=(13, 8), sharex=True)
        FITPLOT[0].set_title("Test: " + FOLDER_DIR, fontsize=18)
        # MODEL.plot_residuals()
        FITPLOT[0].plot(DUR_DAY_INTERP, FIT_RESID, 'b.')
        FITPLOT[0].grid()
        FITPLOT[0].set_ylabel("Residual (Fractional Density)")

        LBL_FIT = ["Initial Guess", "Best Fit", "Interpolated Data"]
        FITPLOT[1].plot(FIT_DOMAIN, MODEL.init_fit, 'g--')
        FITPLOT[1].plot(FIT_DOMAIN, MODEL.best_fit, 'b-')
        FITPLOT[1].plot(FIT_DOMAIN, FIT_RANGE, 'r-')
        FITPLOT[1].grid()
        FITPLOT[1].set_ylabel("Fractional Density")
        FITPLOT[1].set_xlabel("Test Duration (day)")
        FITPLOT[1].legend(LBL_FIT, loc=0)

        if PLOT == 0:
            plt.show()

    VSTRN_FIT_INTERP = -np.log(FDEN0 / FDEN_FIT_INTERP)
    DELTA_VSTRN_FIT_INTERP = np.gradient(VSTRN_FIT_INTERP)
    VSTRN_RATE_FIT_INTERP = DELTA_VSTRN_FIT_INTERP / DELTA_SEC_INTERP
else:  # returns null vectors for fits
    FDEN_FIT_INTERP = np.zeros(len(DUR_SEC_INTERP))
    VSTRN_FIT_INTERP = np.zeros(len(DUR_SEC_INTERP))
    VSTRN_RATE_FIT_INTERP = np.zeros(len(DUR_SEC_INTERP))

PTER_INTERP = PCON_INTERP - PPOR_INTERP  # Terzahi pressure
PSOL_INTERP = (PCON_INTERP - PPOR_INTERP * (1 - FDEN_INTERP)) / FDEN_INTERP

OUT_INTERP_DATA = np.zeros((len(DUR_SEC_INTERP), 11))
OUT_INTERP_DATA[:, 0] = DUR_SEC_INTERP
OUT_INTERP_DATA[:, 1] = DUR_DAY_INTERP
OUT_INTERP_DATA[:, 2] = FDEN_INTERP
OUT_INTERP_DATA[:, 3] = FDEN_FIT_INTERP
OUT_INTERP_DATA[:, 4] = VSTRN_FIT_INTERP
OUT_INTERP_DATA[:, 5] = VSTRN_RATE_FIT_INTERP
OUT_INTERP_DATA[:, 6] = PCON_INTERP
OUT_INTERP_DATA[:, 7] = PPOR_INTERP
OUT_INTERP_DATA[:, 8] = PTER_INTERP
OUT_INTERP_DATA[:, 9] = PSOL_INTERP
OUT_INTERP_DATA[:, 10] = TEMP_INTERP

##################################
# PLOTTING/EXPORTING BELOW
##################################

# LOAD DATA FROM CS MODEL SIMULATION TO PLOT AGAINST EXPERIMENTAL RESULTS
if PLOT_CSMOD == 1:
    COL_CSTIME_SEC = 1
    COL_CSFDEN = 9
    COL_CSMSTRS = 15
    COL_CSDSTRS = 16
    COL_CSTEMP = 23
    COL_CSVSTRN_RATE = 26
    COL_CSMOD_IMPORT = (COL_CSTIME_SEC, COL_CSFDEN, COL_CSTEMP,
                        COL_CSVSTRN_RATE, COL_CSMSTRS, COL_CSDSTRS)
    CSMOD_ARR = np.genfromtxt(fname=PATH_CSMOD, delimiter=',', skip_header=2,
                              usecols=COL_CSMOD_IMPORT, dtype=float)
    print("CS Model data loaded")
    CS_DUR_DAY = DUR_START + CSMOD_ARR[:, 0] / (3600 * 24)  # PLOTTING TIME
    CS_FDEN = CSMOD_ARR[:, 1]
    CS_TEMP = CSMOD_ARR[:, 2]
    CS_VSTRN_RATE = CSMOD_ARR[:, 3] * (-1)
    CS_PCON = CSMOD_ARR[:, 3]
    CS_PDEV = CSMOD_ARR[:, 4]

##################################
FS = 14  # FONT SIZE FOR PLOTTING
NUM_SUBPLOT = 3
FIG1, AXARR = plt.subplots(NUM_SUBPLOT, figsize=(13, 10), sharex=True)
AXARR[0].set_title("Test: " + FOLDER_DIR,
                   fontsize=18)
##################################
# EXACT VOLUME STRAIN AND FRACTIONAL DENSITY RELATION
##################################
# lbl_strn = ['Volumetric Strain', 'Fractional Density', 'Lateral Strain']
# AXARR[0].plot(DURATION_DAY, VSTRN, 'b-', lw=3)
# # AXARR[0].plot(PLT_TIME, PLT_ASTRN, 'g-', lw=3)
# # AXARR[0].plot(PLT_TIME, PLT_LSTRN, 'r-', lw=3)
# AXARR[0].grid(True)
# AXARR[0].set_ylabel("Strain", fontsize=FS)
# # AXARR[0].set_ylim(ymin=0)
# YMIN, YMAX = AXARR[0].get_ylim()
# YMIN = FDEN0 / np.exp(-YMIN)
# YMAX = FDEN0 / np.exp(-YMAX)
# AX2A = AXARR[0].twinx()
# AX2A.semilogy(DURATION_DAY, FDEN, 'r-', lw=2)
# AX2A.yaxis.set_minor_formatter(FormatStrFormatter("%.1f"))
# AX2A.yaxis.set_major_formatter(FormatStrFormatter("%.1f"))
# AX2A.set_ylabel("Fractional Density", fontsize=FS)
# AX2A.tick_params(labelsize=FS)
# AX2A.set_ylim(ymin=YMIN, ymax=YMAX)
# AX2A.lines[0].remove()
# # AXARR[0].legend(lbl_strn, frameon=1, framealpha=1, loc=0, fontsize=FS)
# AXARR[0].tick_params(labelsize=FS)
# AXARR[0].tick_params(labelsize=FS, pad=10)
#################################
# APPROXIMATE VOLUME STRAIN AND FRACTIONAL DENSITY
# #################################

LBL_FDEN = ["Measured", "Interpolated", "Fit", "CS Model"]
AXARR[0].plot(DUR_DAY, FDEN, linestyle='-', linewidth=1,
              marker='.', markersize=4, color='r', alpha=1)
AXARR[0].plot(DUR_DAY_INTERP, FDEN_INTERP, linestyle='-', linewidth=1,
              marker='.', markersize=4, color='y', alpha=1)
if RUN_FIT_FDEN == 1:
    AXARR[0].plot(DUR_DAY_INTERP, FDEN_FIT_INTERP, linestyle='-',
                  linewidth=4, marker=None, markersize=1, color='b',
                  alpha=1)
if PLOT_CSMOD == 1:
    AXARR[0].plot(CS_DUR_DAY, CS_FDEN, linestyle='-',
                  linewidth=2, marker=None, markersize=1, color='g',
                  alpha=1)
AXARR[0].grid(True)
AXARR[0].set_ylabel("Fractional Density", fontsize=FS)
# AXARR[0].set_ylim(ymin=FDEN0)
YMIN, YMAX = AXARR[0].get_ylim()
YMIN = -np.log(FDEN0 / YMIN)
YMAX = -np.log(FDEN0 / YMAX)
AX2A = AXARR[0].twinx()
AX2A.plot(DUR_DAY_INTERP, VSTRN_INTERP, 'r-', lw=3)
AX2A.yaxis.set_minor_formatter(FormatStrFormatter("%.2f"))
AX2A.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
AX2A.set_ylabel("Approx. Volumetric Strain", fontsize=FS)
AX2A.tick_params(labelsize=FS)
AX2A.set_ylim(ymin=YMIN, ymax=YMAX)
AX2A.lines[0].remove()
AXARR[0].legend(LBL_FDEN, frameon=1, framealpha=1, loc=4, fontsize=FS)
AXARR[0].tick_params(labelsize=FS)
AXARR[0].tick_params(labelsize=FS, pad=10)
#################################
LBL_STRNRATE = ["Interpolated", "Measured", "Fit", "CS Model"]
LBL_INTERVAL = ["Sampling"]
AXARR[1].semilogy(DUR_DAY_INTERP, VSTRN_RATE_INTERP, linestyle='-',
                  linewidth=1, marker='.', markersize=4,
                  color='y', alpha=1)
AXARR[1].semilogy(DUR_DAY, VSTRN_RATE, linestyle='-',
                  linewidth=1, marker='.', markersize=4,
                  color='r', alpha=1)
if RUN_FIT_FDEN == 1:
    AXARR[1].semilogy(DUR_DAY_INTERP, VSTRN_RATE_FIT_INTERP, linestyle='-',
                      linewidth=4, marker='None', markersize=4,
                      color='b', alpha=1)
if PLOT_CSMOD == 1:
    AXARR[1].semilogy(CS_DUR_DAY, CS_VSTRN_RATE, linestyle='-',
                      linewidth=2, marker='None', markersize=4,
                      color='G', alpha=1)

AXARR[1].grid(True)
AXARR[1].set_ylabel(r'Strain Rate (sec$^{-1}$)', fontsize=FS)

AX2B = AXARR[1].twinx()
AX2B.semilogy(DUR_DAY, DELTA_SEC, linestyle='-',
              linewidth=1, marker='.', markersize=4,
              color='k', alpha=1)
AX2B.set_ylabel("Seconds Per Sample", fontsize=FS)
AX2B.tick_params(labelsize=FS)
AXARR[1].legend(LBL_STRNRATE, frameon=1, framealpha=0.75, loc=1, fontsize=FS)
AX2B.legend(LBL_INTERVAL, frameon=1, framealpha=0.85, loc=4, fontsize=FS)

AXARR[1].tick_params(labelsize=FS)
AXARR[1].tick_params(labelsize=FS, pad=10)
#################################
LBL_STRS = ["Confining", "Pore", "Terzaghi",
            "Solid"]
LBL_TEMP = ["Temperature"]
AXARR[2].plot(DUR_DAY_INTERP, PCON_INTERP, linestyle='-',
              linewidth=1, marker='.', markersize=4,
              color='b', alpha=1)
AXARR[2].plot(DUR_DAY_INTERP, PPOR_INTERP, linestyle='-',
              linewidth=1, marker='.', markersize=4,
              color='g', alpha=1)
AXARR[2].plot(DUR_DAY_INTERP, PTER_INTERP, linestyle='-',
              linewidth=1, marker='.', markersize=4,
              color='r', alpha=1)
AXARR[2].plot(DUR_DAY_INTERP, PSOL_INTERP, linestyle='-',
              linewidth=1, marker='.', markersize=4,
              color='c', alpha=1)
AXARR[2].yaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x),
                                                                     ',')))
AXARR[2].grid(True)
AXARR[2].set_ylabel('Pressure (MPa)', fontsize=FS)

AX2C = AXARR[2].twinx()
AX2C.plot(DUR_DAY_INTERP, TEMP_INTERP, linestyle='-',
          linewidth=1, marker='.', markersize=4,
          color='k', alpha=1)
AX2C.set_ylabel(r'Temperature ($^o$C)', fontsize=FS)
AX2C.tick_params(labelsize=FS)

AXARR[2].legend(LBL_STRS, frameon=1, framealpha=.85, loc=4, fontsize=FS)
AX2C.legend(LBL_TEMP, frameon=1, framealpha=0.85, loc=3, fontsize=FS)

AXARR[2].tick_params(labelsize=FS)
AXARR[2].tick_params(labelsize=FS, pad=10)
#################################
LOWEST_CHART = NUM_SUBPLOT - 1
AXARR[LOWEST_CHART].set_xlabel("Test Duration [days]", fontsize=FS,
                               labelpad=10)
# MAJORFORMATTER = FormatStrFormatter('%2.3f')
# AXARR[LOWEST_CHART].xaxis.set_major_formatter(MAJORFORMATTER)
AXARR[LOWEST_CHART].tick_params(labelsize=FS, pad=10)
# AXARR[LOWEST_CHART].set_xlim(DUR_START, DUR_END)
# FIG1.tight_layout()
FIG0_NAME = TEST_NAME + STAGE_ID + "_PLOTS_RESID.pdf"
FIG1_NAME = TEST_NAME + STAGE_ID + "_PLOTS.pdf"
PATH = REPO_DIR + '/' + FOLDER_DIR + '/'
#################################
if SAVEFIG != 0:
    if PLOT_FITDATA == 1:
        FIG0.savefig(PATH + FIG0_NAME)
    FIG1.savefig(PATH + FIG1_NAME)
    print("Figure Saved As: " + FIG1_NAME)
if SAVECSV != 0:
    # SAVE RESULTS TO .CSV FILE
    OUT_FILENAME = PATH + TEST_NAME + STAGE_ID + '_OUT.csv'
    OUT_FILENAME_REPORT = PATH + TEST_NAME + STAGE_ID + '_FITREPORT.csv'
    OUT_FILENAME_PARM = PATH + TEST_NAME + STAGE_ID + '_PARM.bin'

    # HEADER = "Interpolated Data For Test: " + str(TEST_NAME) + "/n"
    LINE00 = "Analysis by Brandon Lampe, performed on: " +\
             datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S').rstrip('0')
    LINE01 = "Experimental results below begin at: " +\
             TIME_START.strftime('%Y/%m/%d %H:%M:%S').rstrip('0')

    LINE02 = "Duration (sec),Duration (day),Fractional Density," +\
             "Fit to Fractional Density," +\
             "Fit to Volume Strain,Fit to Volume Strain Rate (1/sec)," +\
             "Confining Pressure (MPa),Pore Pressure (MPa)," +\
             "Terzaghi Pressure (MPa),Solid Pressure (MPa)," +\
             "Temperature (C))"
    HEADER = '\n'.join([LINE00, LINE01, LINE02])
    np.savetxt(OUT_FILENAME, OUT_INTERP_DATA, fmt='%.6e', delimiter=',',
               newline='\n', header=HEADER, comments="")
    print("Saved Data As: " + OUT_FILENAME)

    # WRITE FIT REPORT
    OUT = open(OUT_FILENAME_REPORT, 'w')
    OUT.write(FIT_REPORT)

    # WRITE PARAMETER VALUES ONLY, for input into python later
    with open(OUT_FILENAME_PARM, 'wb') as handle:
        pickle.dump(MODEL.best_values, handle)

    # read parameter values from pickled file
    with open(OUT_FILENAME_PARM, 'rb') as handle:
        TEST_READ = pickle.loads(handle.read())

    print("Saved Fit Report As: " + OUT_FILENAME_REPORT)
    print("Saved Parameters As: " + OUT_FILENAME_PARM)
if PLOT != 0:
    plt.show()
