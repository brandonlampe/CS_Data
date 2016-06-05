import numpy as np
import sys
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from matplotlib.ticker import FuncFormatter
REPO_DIR = '/Users/Lampe/GrantNo456417/CurrentTesting/CrushedSaltRepo'
sys.path.append(REPO_DIR + '/PythonCode')
import DataAnalysisFunc as daf
##################################
# CHOOSE TEST
##################################
PLOT = 1
SAVEFIG = 1
SAVECSV = 0

# TESTNAME = 'UNM_WP_HY_90_02'
# TESTNAME = 'UNM_WP_HY_90_03'
# TESTNAME = 'UNM_WP_HY_90_04'
# TESTNAME = 'UNM_WP_HY_90_08'
# TESTNAME = 'UNM_WP_HY_175_01'
# TESTNAME = 'UNM_WP_HY_175_03'
# TESTNAME = 'UNM_WP_HY_175_04'
FOLDER_DIR = 'UNM_WP_HY_175_09'
# load tests data - .csv file that has been exported directly from .xlsx
TESTNAME = FOLDER_DIR[-6:]

# DEFINE COLUMNS FOR:
# 'UNM_WP_HY_175_09'
COL_TIME = 1
COL_TEMP = 8
COL_PCON = 2
COL_PPOR = 14
COL_FDEN = 31

# print(daf.col_lbl(31))
RHOIS = 2160.0  # ASSUMED IN-SITU DENSITY (KG/M3), FOR STRAIN MEASURE
USECOLS = (np.arange(0, 32, 1))
IMPORT_FNAME = REPO_DIR + '/' + FOLDER_DIR + '/' + TESTNAME + '.csv'
# print("Imported Test: " + TESTNAME)
print("File Path: " + IMPORT_FNAME)

# IMPORT_ARR = np.loadtxt(fname=IMPORT_FNAME, delimiter=',', skiprows=2)
IMPORT_ARR = np.genfromtxt(fname=IMPORT_FNAME, delimiter=',', skiprows=1,
                           usecols=USECOLS)

WINDOWSIZE = 20  # NUMBER OF POINTS INCLUDED IN AVERAGING WINDOW
TRIM = int(WINDOWSIZE / 2.0)  # NUMBER OF POINTS TO TRIME FROM FRONT AND BACK
DATETIME = daf.xldate_to_datetime(IMPORT_ARR[TRIM:-TRIM, COL_TIME])
DURATION_DAY = daf.duration(IMPORT_ARR[TRIM:-TRIM, COL_TIME])
DURATION_DAYNOAVG = daf.duration(IMPORT_ARR[:, COL_TIME])
DURATION_SEC = DURATION_DAY * 24 * 3600
DURATION_SECNOAVG = DURATION_DAYNOAVG * 24 * 3600
FDEN_NOAVG = IMPORT_ARR[:, COL_FDEN]  # NO TIME AVERAGEING
FDEN0_NOAVG = FDEN_NOAVG[0]

VSTRN_NOAVG = -np.log(FDEN0_NOAVG / FDEN_NOAVG)  # POSITIVE IN COMPRESSION
VSTRN_RATENOAVG = np.diff(VSTRN_NOAVG) / np.diff(DURATION_SECNOAVG)  # SEC^-1

# SMOOTH OVER STRAIN RATE ITSELF
VSTRN_RATE_AVG = daf.moving_avg(VSTRN_RATENOAVG, WINDOWSIZE)  # SMOOTH

# SMOOTH OVER FRACTIONAL DENSITY MEASURMENTS
FDEN = daf.moving_avg(IMPORT_ARR[:, COL_FDEN], WINDOWSIZE)
FDEN0 = FDEN[0]  # SCALAR
VSTRN = -np.log(FDEN0 / FDEN)  # POSITIVE IN COMPRESSION
DELTA_VSTRN = np.gradient(VSTRN)
DELTA_SEC = np.gradient(DURATION_SEC)
VSTRN_RATE = DELTA_VSTRN / DELTA_SEC


PCON = IMPORT_ARR[TRIM:-TRIM, COL_PCON]
PPOR = IMPORT_ARR[TRIM:-TRIM, COL_PPOR]
PTER = PCON - PPOR  # Terzahi pressure
PSOL = (PCON - PPOR * (1 - FDEN)) / FDEN


FS = 16  # FONT SIZE FOR PLOTTING
NUM_SUBPLOT = 3
FIG1, AXARR = plt.subplots(NUM_SUBPLOT, figsize=(12, 10), sharex=True)
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
#################################
AXARR[0].plot(DURATION_DAY, FDEN, 'b-', lw=3)
# AXARR[0].plot(DURATION_DAY, FDEN_NOAVG, 'r-', lw=3)
AXARR[0].grid(True)
AXARR[0].set_ylabel("Fractional Density", fontsize=FS)
AXARR[0].set_ylim(ymin=FDEN0)
YMIN, YMAX = AXARR[0].get_ylim()
YMIN = -np.log(FDEN0 / YMIN)
YMAX = -np.log(FDEN0 / YMAX)
AX2A = AXARR[0].twinx()
AX2A.plot(DURATION_DAY, VSTRN, 'r-', lw=3)
AX2A.yaxis.set_minor_formatter(FormatStrFormatter("%.2f"))
AX2A.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
AX2A.set_ylabel("Approx. Volumetric Strain", fontsize=FS)
AX2A.tick_params(labelsize=FS)
AX2A.set_ylim(ymin=YMIN, ymax=YMAX)
AX2A.lines[0].remove()
AXARR[0].tick_params(labelsize=FS)
AXARR[0].tick_params(labelsize=FS, pad=10)
#################################

print()

lbl_fden = ["Strain Rate", "Sample Interval"]
AXARR[1].semilogy(DURATION_DAY, VSTRN_RATE, 'b-', lw=3)
# AXARR[1].semilogy(DURATION_DAYNOAVG[1:], VSTRN_RATENOAVG, 'r-', lw=3)
AXARR[1].grid(True)
AXARR[1].set_ylabel(r'Strain Rate (sec$^{-1}$)', fontsize=FS)
AXARR[1].legend(lbl_fden, frameon=1, framealpha=1, loc=0, fontsize=FS)

AX2B = AXARR[1].twinx()
AX2B.semilogy(DURATION_DAY, DELTA_SEC, 'r-', lw=3)
AX2B.set_ylabel("Sample Interval (sec)", fontsize=FS)
AX2B.tick_params(labelsize=FS)

AXARR[1].tick_params(labelsize=FS)
AXARR[1].tick_params(labelsize=FS, pad=10)
#################################
lbl_strs = ["Confining Pressure", "Pore Pressure", "Terzaghi Pressure",
            "Solid Pressure"]
AXARR[2].plot(DURATION_DAY, PCON, 'b-', lw=3)
AXARR[2].plot(DURATION_DAY, PPOR, 'g-', lw=3)
AXARR[2].plot(DURATION_DAY, PTER, 'r-', lw=3)
AXARR[2].plot(DURATION_DAY, PSOL, 'c-', lw=3)
AXARR[2].yaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x),
                                                                     ',')))
AXARR[2].grid(True)
AXARR[2].set_ylabel("Stress", fontsize=FS)
AXARR[2].legend(lbl_strs, frameon=1, framealpha=1, loc=0, fontsize=FS)
AXARR[2].tick_params(labelsize=FS)
AXARR[2].tick_params(labelsize=FS, pad=10)
#################################
LOWEST_CHART = NUM_SUBPLOT - 1
AXARR[LOWEST_CHART].set_xlabel("Test Duration [days]", fontsize=FS,
                               labelpad=10)
majorFormatter = FormatStrFormatter('%2.1f')
AXARR[LOWEST_CHART].xaxis.set_major_formatter(majorFormatter)
AXARR[LOWEST_CHART].tick_params(labelsize=FS, pad=10)

# FIG1.tight_layout()
FIG1_NAME = "PLOTS_" + TESTNAME + '.pdf'
PATH = REPO_DIR + '/' + FOLDER_DIR + '/'
#################################
if SAVEFIG != 0:
    FIG1.savefig(PATH + FIG1_NAME)
if PLOT != 0:
    plt.show()
if SAVECSV != 0:
    # SAVE RESULTS TO .CSV FILE
    OUT_FILENAME = PATH + TEST_NAME + '_OUT.csv'
    COMMENTS = """RESULTS FROM, XX, RUN BY, XX, ON, XX
               """
    HEADER = ('INC,TIME_SEC,ASTRNRATE,LSTRNRATE,ZETARATE,ASTRN,LSTRN,ZETA,\
                VSTRN,FDEN,RHO,MDCREEP,SPCREEP,SSCREEP,FTRN,MSTRS,\
                DSTRS,SEQ,SEQF,F2A,F2L,ASTRS,LSTRS,TEMPC,DSZ,WATER')
    np.savetxt(OUT_FILENAME, OUT, fmt='%.8e', delimiter=',', newline='\n',
               header=HEADER, comments=COMMENTS)
