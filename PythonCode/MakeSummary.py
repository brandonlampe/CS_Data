import sys
import numpy as np
import csv
import itertools
import os
import pickle

# relative path to module
sys.path.append(sys.path[0])
import DataAnalysisFunc as daf
REPO_DIR = os.path.dirname(sys.path[0])  # PATH TO REPOSITORY DIRECTORY


FOLDER_DIR = 'UNM_WP_HY_175_09'
BUILD_SUMMARY = 0  # 0=> SUMMARY IS READ FROM FILE, 1=> SUMMARY IS BUILT
# STAGE_DIR = '/' + STAGE_ID[1:]

# load tests data - .csv file that has been exported directly from .xlsx
TEST_NAME = FOLDER_DIR[10:]  # + '_comp'
DIR_NAME = REPO_DIR + '/' + FOLDER_DIR
SUMMARY_PATH = os.path.join(DIR_NAME, 'SUMMARY.bin')
SUMMARY_CSV_PATH = os.path.join(DIR_NAME, 'SUMMARY.csv')

if  BUILD_SUMMARY == 1:
    SUMMARY = np.zeros((22, 11))
    INC = 0
    # DISECT CREEP FIT REPORTS
    for stage_name in os.listdir(DIR_NAME):
        if stage_name[0:5] == 'STAGE':
            stage_dir = os.path.join(DIR_NAME, stage_name)
            for root, fit_name, files in os.walk(stage_dir, topdown=True):
                if fit_name != []:
                    if fit_name[0] == 'CREEP_FIT':
                        # print(str(INC + 1))
                        # print(fit_name[0])
                        fit_dir = os.path.join(root, 'CREEP_FIT')
                        for filename in os.listdir(fit_dir):
                            # if filename[-13:] == 'FITREPORT.csv':
                            if filename[-7:] == 'OUT.csv':
                                file_dir = os.path.join(fit_dir, filename)
                                data = np.loadtxt(file_dir, delimiter=',',
                                                  skiprows=3)
                                SUMMARY[INC, 0] = int(INC + 1)  # STAGE NUMBER
                                SUMMARY[INC, 1] = data[0, 1]  # TIME,START[DAY]
                                SUMMARY[INC, 2] = data[-1, 1]  # TIME,END [DAY]
                                SUMMARY[INC, 3] = data[-1, 3]  # DURATION [DAY]
                                SUMMARY[INC, 4] = data[0, 5]  # FITFDEN,START
                                SUMMARY[INC, 5] = data[-1, 5]  # FITFDEN,END
                                SUMMARY[INC, 6] = data[0, 7]  # STRNRATE,START[1/SEC]
                                SUMMARY[INC, 7] = data[-1, 7]  # STRNRATE,END [1/SEC]
                                SUMMARY[INC, 8] = np.mean(data[:, 8])  # pcon
                                SUMMARY[INC, 9] = np.mean(data[:, 9])  # ppore
                                SUMMARY[INC, 10] = np.mean(data[:, 12])  # temp
                                INC = INC + 1
    with open(SUMMARY_PATH, 'wb') as handle:
        pickle.dump(SUMMARY, handle)
    np.savetxt(SUMMARY_CSV_PATH, SUMMARY, delimiter=',')
else:
    # read parameter values from pickled files
    with open(SUMMARY_PATH, 'rb') as handle:
        SUMMARY = pickle.loads(handle.read())


# print(SUMMARY)

import matplotlib.pyplot as plt
from matplotlib import cm

LBND = 0.25  # lower bound on color map
UBND = 1.0  # upper bound on color map

LINE_NUM = SUMMARY.shape[0]
COLORMAP_SUB = np.linspace(LBND, UBND, LINE_NUM)

COLORMAP = [cm.cool(x) for x in COLORMAP_SUB]

FS = 16
FIG1 = plt.figure()
AX = FIG1.add_subplot(111)

LINES = []
for idx, color in enumerate(COLORMAP):
    XVAL = SUMMARY[idx, 4:6]
    YVAL = SUMMARY[idx, 6:8]
    LBL = "Stage: " + str(int(SUMMARY[idx, 0]))
    current_line, = AX.semilogy(XVAL, YVAL, color=color, label=LBL,
                                linestyle='-',
                                linewidth=2, marker='o', markersize=3,
                                alpha=1)
    LINES.append(current_line)

handles, labels = AX.get_legend_handles_labels()
AX.legend(handles, labels, loc='lower left', ncol=2,
          fontsize=10)

AX.set_xlim(xmin=0.8, xmax=.96)
AX.set_ylabel(r'Strain Rate ($\frac{1}{sec}$)', fontsize=FS)
AX.set_xlabel("Fractional Density", fontsize=FS)
AX.grid()
plt.show()

# ##################################
# FS = 14  # FONT SIZE FOR PLOTTING
# ##################################
# # # # print color list
# # for name, hex in matplotlib.colors.cnames.iteritems():
# #     print(name, hex)

# ######################################################################
# # PLOTTING DURING LOAD UP ONLY BELOW
# ######################################################################
# FIG1 = plt.figure(figsize=(13, 10))

# AX1 = FIG1.add_subplot(311)
# AX1.set_title("Test: " + FOLDER_DIR, fontsize=18)

# LBL_FDEN = ["Fractional Density: Loading"]
# LBL_STRN = ["Volumetric Strain"]
# LBL_PRES = ["Pressure: Confining"]
# AX1.plot(LOAD_TIME_SEC, LOAD_FDEN, linestyle='-', linewidth=2,
#          marker='s', markersize=4, color='cyan', alpha=1)
# AX1.grid(True)

# AX1A = AX1.twinx()
# AX1A.plot(LOAD_TIME_SEC, LOAD_PCON, linestyle='-',
#           linewidth=1, marker='.', markersize=8, color='r',
#           alpha=1)
# # AX1A.plot(LOAD_TIME_SEC, LOAD_PSOL, linestyle='-',
# #           linewidth=1, marker='s', markersize=4, color='m',
# #           alpha=1)
# AX1A.tick_params(labelsize=FS)
# AX1.tick_params(labelsize=FS, pad=10)

# AX1.legend(LBL_FDEN, frameon=1, framealpha=1, loc=2, fontsize=FS)
# AX1A.legend(LBL_PRES, frameon=1, framealpha=1, loc=4, fontsize=FS)
# AX1.set_ylabel("Fractional Density", fontsize=FS)
# AX1A.set_ylabel("Pressure (MPa)", fontsize=FS)
# AX1.set_xlabel("Loading Time (sec)",
#                fontsize=FS, labelpad=0)

# #################################
