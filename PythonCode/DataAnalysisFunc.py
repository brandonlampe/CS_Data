"""
    Module containing functions for importing and analysing creep tests

    function list:
    1) xldate_to_datetime: converts Excel date (numeric) to Python datetime
    2) duration:  calculates duration in days using Excel date as input
    3) col_lbl: provides labels for columns from Excel data
    4) moving_avg:  calculates the moving average over
    5) find_nearest:  finds the index of the nearest value in an array
"""

import numpy as np
import datetime
import lmfit

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
    return avg[trim:-trim]  # trims the ends
    # return avg  # no trim at ends


def find_nearest(array, value):
    """ identifies the index in the array for the nearest value"""
    idx = (np.abs(array - value)).argmin()
    return idx


def fit_fden(fden_interp, dur_day_interp):
    # fit the fractional density using the LMFIT package, combine 2 models
    # ref: https://lmfit.github.io/lmfit-py/builtin_models.html
    # class StepModel, logistic = f(x; A, mu, sigma) = A{1-1/(1+exp(alpha))}
    #                   where: alpha = (x - mu)/sigma
    # class LinearModel = f(x; m,b)= mx + b
    ASYM_MOD = lmfit.models.ExpressionModel('(ainf + (azero-ainf)/(1+(x/c)**b)**g) + (slope * x) + (aexp * x ** kexp)')
    # STEP_MOD = lmfit.models.StepModel(form='logistic', prefix='step_')
    # LINE_MOD = lmfit.models.LinearModel(prefix='line_')
    # POWR_MOD = lmfit.models.ExponentialModel(prefix='powr_')

    # define initial guess values for parameters for each model
    PARMS = ASYM_MOD.make_params(ainf=0.87, azero=0.74, c=0.005,
                                 b=27.0, g=0.05,
                                 slope=0.001, aexp=0.05, kexp=0.1)
    # PARMS += LINE_MOD.guess(FDEN_INTERP, x=DUR_DAY_INTERP)
    # PARMS = LINE_MOD.make_params(intercept=FDEN_INTERP.min(), slope=0)
    # PARMS += POWR_MOD.make_params(amplitude=0.25, exponent=0.1)
    # PARMS += STEP_MOD.guess(FDEN_INTERP, x=DUR_DAY_INTERP, center=0.01)

    MOD = ASYM_MOD
    # MOD = STEP_MOD + LINE_MOD + POWR_MOD  # COMBINE THE TWO MODELS
    # MOD = STEP_MOD + POWR_MOD  # COMBINE THE TWO MODELS
    # MOD = STEP_MOD  # SINGLE MODEL
    out = MOD.fit(fden_interp, PARMS, x=dur_day_interp)
    return out


def model_fden(xday, parm):
    """
    xday = duration time in days
    parm = parameter set for fit
    """
    slope, c, b, g, kexp, aexp, azero, ainf = parm
    out = ainf + (azero - ainf) / (1 + (xday / c)**b)**g +\
        slope * xday + aexp * xday**kexp
    return out
