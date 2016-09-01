import sys
import numpy as np
import os
import pickle
import matplotlib.pyplot as plt
from matplotlib import cm
import Table

# relative path to module
sys.path.append(sys.path[0])
import DataAnalysisFunc as daf
REPO_DIR = os.path.dirname(sys.path[0])  # PATH TO REPOSITORY DIRECTORY


FOLDER_DIR = 'UNM_WP_HY_175_09'
BUILD_SUMMARY = 0  # 0=> SUMMARY IS READ FROM FILE, 1=> SUMMARY IS BUILT
WRITE_TABLE = 0
SHOW_PLOT = 1
# STAGE_DIR = '/' + STAGE_ID[1:]

# load tests data - .csv file that has been exported directly from .xlsx
TEST_NAME = FOLDER_DIR[10:]  # + '_comp'
DIR_NAME = REPO_DIR + '/' + FOLDER_DIR
SUMMARY_PATH = os.path.join(DIR_NAME, 'SUMMARY.bin')
SUMMARY_CSV_PATH = os.path.join(DIR_NAME, 'SUMMARY.csv')

if BUILD_SUMMARY == 1:
    SUMMARY = np.zeros((22, 11))
    INC = 0
    # DISECT CREEP FIT REPORTS
    for stage_name in os.listdir(DIR_NAME):
        if stage_name[0:5] == 'STAGE':
            stage_dir = os.path.join(DIR_NAME, stage_name)
            for root, fit_name, files in os.walk(stage_dir, topdown=True):
                if fit_name != []:
                    if fit_name[0] == 'CREEP_FIT':
                        fit_dir = os.path.join(root, 'CREEP_FIT')
                        for filename in os.listdir(fit_dir):
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
                                SUMMARY[INC, 6] = data[0, 7]  # STRNRATE,START
                                SUMMARY[INC, 7] = data[-1, 7]  # STRNRATE,END
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


################################################
# write latex table
################################################

if WRITE_TABLE == 1:
    TABLE_OUT = open('mytable.tex', 'w')
    t = Table.Table(
        numcols=11,
        justs='lrccccccccc',
        caption='Summary of results from',
        label="tab:results")
    t.add_header_row(['Stage', 'Time Start', 'Time End', 'Duration',
                      'Initial $\\rho_f$', 'Final $\\rho_f$',
                      'Initial $\\dot{e}$', 'Final $\\dot{e}$',
                      '$P_{con}$', '$P_{por}$', 'Temperature'])
    COL1 = SUMMARY[:, 0]
    COL2 = SUMMARY[:, 1]
    COL3 = SUMMARY[:, 2]
    COL4 = SUMMARY[:, 3]
    COL5 = SUMMARY[:, 4]
    COL6 = SUMMARY[:, 5]
    COL7 = SUMMARY[:, 6]
    COL8 = SUMMARY[:, 7]
    COL9 = SUMMARY[:, 8]
    COL10 = SUMMARY[:, 9]
    COL11 = SUMMARY[:, 10]

    t.add_data([COL1, COL2, COL3, COL4, COL5, COL6, COL7, COL8, COL9,
                COL10, COL11], sigfigs=3)
    t.print_table(TABLE_OUT)
    TABLE_OUT.close()
################################################
# PLOTTING
################################################
LBND = 0.0  # lower bound on color map
UBND = 1.0  # upper bound on color map

LINE_NUM = SUMMARY.shape[0]
COLORMAP_SUB = np.linspace(LBND, UBND, LINE_NUM)

COLORMAP = [cm.Set1(x) for x in COLORMAP_SUB]

FS = 16
FIG1 = plt.figure(figsize=(13, 10))
AX1 = FIG1.add_subplot(211)
AX2 = FIG1.add_subplot(212, sharex=AX1)
# FIG1.subplot(sharex=True)
# subplot(rows, columns, plot number)
# AX1A = AX1.twinx()

STRNRATE_LINES = []
PCON_LINES = []
for idx, color in enumerate(COLORMAP):
    FDEN = SUMMARY[idx, 4:6]
    PCON = np.array((SUMMARY[idx, 8], SUMMARY[idx, 8]))
    PPOR = np.array((SUMMARY[idx, 9], SUMMARY[idx, 9]))
    PTER = PCON - PPOR
    STRNRATE = SUMMARY[idx, 6:8]
    LBL_STRNRATE = "Stage: " + str(int(SUMMARY[idx, 0]))
    if idx == 0:
        LBL_PCON = 'Confining Pressure'
        LBL_PPOR = 'Pore Pressure'
        LBL_PTER = 'Terzaghi Pressure'
    else:
        LBL_PCON = '_nolegend_'
        LBL_PPOR = '_nolegend_'
        LBL_PTER = '_nolegend_'
    current_strnrate, = AX1.semilogy(FDEN, STRNRATE, color=color,
                                     label=LBL_STRNRATE,
                                     linestyle='-',
                                     linewidth=3, marker='None', markersize=4,
                                     markerfacecolor='k', fillstyle='bottom',
                                     alpha=1)
    current_pcon = AX2.plot(FDEN, PCON, color='green', label=LBL_PCON,
                            linestyle='-',
                            linewidth=2, marker='o', markersize=6,
                            markerfacecolor='green', fillstyle='none',
                            alpha=1)
    current_pcon = AX2.plot(FDEN, PPOR, color='blue', label=LBL_PPOR,
                            linestyle='-',
                            linewidth=2, marker='o', markersize=6,
                            markerfacecolor='blue', fillstyle='none',
                            alpha=1)
    current_pcon = AX2.plot(FDEN, PTER, color='red', label=LBL_PTER,
                            linestyle='-',
                            linewidth=2, marker='o', markersize=6,
                            markerfacecolor='red', fillstyle='none',
                            alpha=.5)
    STRNRATE_LINES.append(current_strnrate)
    PCON_LINES.append(current_pcon)

AX1.set_title("Test: " + FOLDER_DIR, fontsize=18)
AX2.set_ylim(ymin=0)
# AX1.set_xlim(xmin=0.90, xmax=0.955)
AX1.set_ylabel(r'Strain Rate $\left(\frac{1}{sec}\right)$', fontsize=FS)
AX2.set_xlabel("Fractional Density", fontsize=FS)
AX2.set_ylabel("Pressure (MPa)", fontsize=FS)
AX1.grid()
AX2.grid()
AX1.tick_params(labelsize=FS, pad=10)
AX2.tick_params(labelsize=FS, pad=10)

HANDLES_1, LABELS_1 = AX1.get_legend_handles_labels()
#  bbox_to_anchor(xmin, ymin, xmax, ymax) ro bounding box of legend
LGD1 = AX1.legend(HANDLES_1, LABELS_1, bbox_to_anchor=(0, .65, 1, 1),
                  loc='lower right', borderaxespad=1, ncol=5,
                  fontsize=10)
HANDLES_2, LABELS_2 = AX2.get_legend_handles_labels()
LGD2 = AX2.legend(HANDLES_2, LABELS_2,
                  bbox_to_anchor=(0, 0, 1, 1),
                  loc='upper left', borderaxespad=1, ncol=1,
                  fontsize=10)


FIG1_NAME = 'TestSummary_94.pdf'
FIG1_PATH = os.path.join(DIR_NAME, FIG1_NAME)
FIG1.savefig(FIG1_PATH, bbox_extra_artists=(LGD2,), bbox_inches='tight')

if SHOW_PLOT == 1:
    plt.show()
