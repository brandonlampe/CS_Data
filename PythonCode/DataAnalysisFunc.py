"""
    Module containing functions for importing and analysing creep tests

    function list:
    1) xldate_to_datetime: converts Excel date (numeric) to Python datetime
"""

import numpy as np
import datetime


def xldate_to_datetime(xldate):
    """ function converts Excel date (numeric) to an actual "date time"
        input: xldate = numeric value
        outupt: list of python datetime (string)
    """
    out = []
    temp = datetime.datetime(1900, 1, 1)

    for i in xrange(len(xldate)):
        delta = datetime.timedelta(days=xldate[i])
        out.append(temp + delta)
    return out

def duration(xldate):
    start = xldate[0]
    delta = xldate - start
    return delta

def col_lbl(colnum):
    column_lbl = ["Sample ID",
                  "Date Time",
                  "Confining Pressure (psi)",
                  "Lower Vessel Temp. (C)",
                  "Upper Vessel Temp. (C)",
                  "Piston Temp. (C)",
                  "Load Cell Temp. (C)",
                  "Ambient Temp. (C)",
                  "Confining Fluid Temp. (C)",
                  "Dilatometer Volume (mL)",
                  "Isco Pump Volume (mL)",
                  "Downstream Flow Rate (SCC/Min.)",
                  "Schuler 01 Raw Value (inch)",
                  "Schuler 02 Raw Value (inch)",
                  "Pore Pressure (psi)",
                  "Cumulative Change of Schuler 01 Diameter (cm)",
                  "Cumulative Change of Schuler 02 Diameter (cm)",
                  "Specimen Diameter, Schuler 01 (cm)",
                  "Specimen Diameter, Schuler 02 (cm)",
                  "Specimen Diamater, Schuler Avg. (cm)",
                  "Volume Change, Confining Fluid Raw Value (cm3)",
                  "Volume Change, Confining Fluid w/Comp. Offset (cm3)",
                  "Volume Change, Schuler 01 (cm3)",
                  "Volume Change, Schuler 02 (cm3)",
                  "Volume Change, Schuler Avg. (cm3)",
                  "Volume Change, Manual Edit (cm3)",
                  "Fractional Density, Confining Fluid",
                  "Fractional Density, Confining Fluid and Schuler Avg.",
                  "Fractional Density, Schuler 01",
                  "Fractional Density, Schuler 02",
                  "Fractional Density, Schuler Avg.",
                  "Fractional Density, Manual Edit"]

    # print("Number of columns labels: " + str(len(COLUMN_LBL)))
    return column_lbl[colnum]


def moving_avg(interval, window_size):
    """ calculates a running average over a window of data"""
    window = np.ones(int(window_size)) / float(window_size)
    avg = np.convolve(interval, window, 'same')
    trim = int(window_size / 2)
    return avg[trim:-trim]

