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
from math import factorial
import sys

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


def fit_fden(fden_interp, dur_day_interp, which_mod, whole_domain):
    # fit the fractional density using the LMFIT package, combine 2 models
    # ref: https://lmfit.github.io/lmfit-py/builtin_models.html

    if which_mod == 1:
        # class StepModel,logistic = f(x; A, mu, sigma) = A{1-1/(1+exp(alpha))}
        #                   where: alpha = (x - mu)/sigma
        # logistic = 'ainf + (azero-ainf)/(1+(x/c)**b)**g'
        # linear = 'slope * x'
        # exponential = 'aexp * x ** kexp'
        # comb_mod = (logistic + linear + exponential)
        print("Logistic Fit Chosen")
        # asym_mod = lmfit.models.ExpressionModel('(low_bnd + (up_bnd-low_bnd)/(1+(x/center)**b)**g)')
        asym_mod = lmfit.models.ExpressionModel('(low_bnd+(up_bnd-low_bnd)/(1+exp(slope*(x-center)))**(1/nu))')
        # define initial guess values for parameters for each model
        parms = asym_mod.make_params(up_bnd=0.87, low_bnd=0.8, center=2.092,
                                     b=27.0, g=0.05)
        parms = asym_mod.make_params(up_bnd=0.99, low_bnd=0.7,
                                     slope=27.0, nu=1e-4, center=2.092)
        parms['nu'].set(0.5, min=1e-6)  # must be greater than zero

        model_result = asym_mod.fit(fden_interp, parms, x=dur_day_interp)
        parm_result = model_result.best_values
        fden_fit_interp = model_result.eval(x=whole_domain,
                                            center=parm_result["center"],
                                            slope=parm_result["slope"],
                                            nu=parm_result["nu"],
                                            low_bnd=parm_result["low_bnd"],
                                            up_bnd=parm_result["up_bnd"])

        # fden_fit_interp = model_result.eval(x=whole_domain,
        #                                     c=parm_result["center"],
        #                                     b=parm_result["b"],
        #                                     g=parm_result["g"],
        #                                     azero=parm_result["azero"],
        #                                     ainf=parm_result["ainf"])


    if which_mod == 2:
        print("Exponential Fit Chosen")
        # class LinearModel = f(x; m,b)= mx + b
        # STEP_MOD = lmfit.models.StepModel(form='logistic', prefix='step_')
        line_mod = lmfit.models.LinearModel(prefix='line_')
        powr_mod = lmfit.models.PowerLawModel(prefix='powr_')

        # parms = line_mod.make_params(intercept=fden_interp.min(), slope=0.1)
        parms = powr_mod.make_params(powr_amplitude=0.25, powr_exponent=0.1)

        line_powr_mod = line_mod + powr_mod  # COMBINE THE TWO MODELS

        model_result = powr_mod.fit(fden_interp, parms, x=dur_day_interp)
        parm_result = model_result.best_values

        fden_fit_interp = model_result.eval(x=whole_domain,
                                            powr_amplitude=parm_result["powr_amplitude"],
                                            powr_exponent=parm_result["powr_exponent"])
    if which_mod == 3:
        print("Logist-Exponential Fit Chosen")
        # class LinearModel = f(x; m,b)= mx + b
        step_mod = lmfit.models.StepModel(form='logistic', prefix='step_')
        # line_mod = lmfit.models.LinearModel(prefix='line_')
        powr_mod = lmfit.models.PowerLawModel(prefix='powr_')

        # parms = line_mod.make_params(intercept=fden_interp.min(), slope=0.1)
        parms = powr_mod.make_params(powr_amplitude=0.05, powr_exponent=0.1)
        parms += step_mod.make_params(step_center=2.09, step_amplitude=0.1,
                                      step_sigma=1e-4)
        # parms += step_mod.guess(fden_interp, x=dur_day_interp,
        #                         step_center=2.09, step_amplitude=0.7)
        powrStep_mod = step_mod + powr_mod  # COMBINE THE TWO MODELS

        model_result = powrStep_mod.fit(fden_interp, parms, x=dur_day_interp)
        parm_result = model_result.best_values

        fden_fit_interp = model_result.eval(x=whole_domain,
                                            step_amplitude=parm_result["step_amplitude"],
                                            step_center=parm_result["step_center"],
                                            step_sigma=parm_result["step_sigma"],
                                            powr_amplitude=parm_result["powr_amplitude"],
                                            powr_exponent=parm_result["powr_exponent"])
    if which_mod == 4:
        print("Logist (3 param) Fit Chosen")
        # class LinearModel = f(x; m,b)= mx + b
        step_mod = lmfit.models.StepModel(form='logistic', prefix='step_')
        # line_mod = lmfit.models.LinearModel(prefix='line_')
        # powr_mod = lmfit.models.PowerLawModel(prefix='powr_')

        # parms = line_mod.make_params(intercept=fden_interp.min(), slope=0.1)
        # parms = powr_mod.make_params(powr_amplitude=0.4, powr_exponent=1.0)
        parms = step_mod.make_params(step_center=2.09, step_sigma=0.001,
                                     step_amplitude=0.91)

        model_result = step_mod.fit(fden_interp, parms, x=dur_day_interp)
        parm_result = model_result.best_values

        fden_fit_interp = model_result.eval(x=whole_domain,
                                            step_amplitude=parm_result["step_amplitude"],
                                            step_center=parm_result["step_center"],
                                            step_sigma=parm_result["step_sigma"])

    if which_mod == 5:
        # Schnute's equation
        print("Schnute's equation was chosen")
        schnute_mod = lmfit.models.ExpressionModel('(c**b + (d**b-c**b)*(1-exp(-a*(x-start)))/(1-exp(-a*(end-start))))**(1/b)')
        # define initial guess values for parameters for each model
        parms = schnute_mod.make_params()
        parms['start'].set(value=dur_day_interp.min(), vary=False)
        parms['end'].set(value=dur_day_interp.max(), vary=False)
        parms['c'].set(value=fden_interp.min() * 0.95, vary=True)
        parms['d'].set(value=fden_interp.max() * 1.05, vary=True)
        parms['a'].set(value=0.1, vary=True)
        parms['b'].set(value=5.0, vary=True)

        model_result = schnute_mod.fit(fden_interp, parms, x=dur_day_interp)
        parm_result = model_result.best_values
        fden_fit_interp = model_result.eval(x=whole_domain,
                                            start=parm_result["start"],
                                            end=parm_result["end"],
                                            c=parm_result["c"],
                                            d=parm_result["d"],
                                            a=parm_result["a"],
                                            b=parm_result["b"])
    return fden_fit_interp, model_result


def model_fden(xday, parm):
    """
    xday = duration time in days
    parm = parameter set for fit
    """
    slope, c, b, g, kexp, aexp, azero, ainf = parm
    out = ainf + (azero - ainf) / (1 + (xday / c)**b)**g +\
        slope * xday + aexp * xday**kexp
    return out


def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    r"""Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
    The Savitzky-Golay filter removes high frequency noise from data.
    It has the advantage of preserving the original shape and
    features of the signal better than other types of filtering
    approaches, such as moving averages techniques.
    Parameters
    ----------
    y : array_like, shape (N,)
        the values of the time history of the signal.
    window_size : int
        the length of the window. Must be an odd integer number.
    order : int
        the order of the polynomial used in the filtering.
        Must be less then `window_size` - 1.
    deriv: int
        the order of the derivative to compute (default = 0 means only smoothing)
    Returns
    -------
    ys : ndarray, shape (N)
        the smoothed signal (or it's n-th derivative).
    Notes
    -----
    The Savitzky-Golay is a type of low-pass filter, particularly
    suited for smoothing noisy data. The main idea behind this
    approach is to make for each point a least-square fit with a
    polynomial of high order over a odd-sized window centered at
    the point.
    Examples
    --------
    t = np.linspace(-4, 4, 500)
    y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
    ysg = savitzky_golay(y, window_size=31, order=4)
    import matplotlib.pyplot as plt
    plt.plot(t, y, label='Noisy signal')
    plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
    plt.plot(t, ysg, 'r', label='Filtered signal')
    plt.legend()
    plt.show()
    References
    ----------
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688
    """

    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError, msg:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order + 1)
    half_window = (window_size - 1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window,
                                                           half_window + 1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs(y[1:half_window + 1][::-1] - y[0])
    lastvals = y[-1] + np.abs(y[-half_window - 1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve(m[::-1], y, mode='valid')


def column_idx(testname_str):
    """ identifies which columns were pulled from the .csv file
      - the .csv file is a direct copy of the "FmtData" worksheet in Excel
    """
    print("Test Name: " + testname_str)
    if testname_str == '175_09':
        col_time = 1  # Excel Time Column (days)
        col_temp = 8
        col_pcon = 2
        col_ppor = 14
        col_fden = 31
    elif testname_str == '175_04':
        col_time = 1  # Excel Time Column (days)
        col_temp = 13
        col_pcon = 3
        col_ppor = 0
        col_fden = 34
    elif testname_str == '175_09_comp':
        col_time = 1
        col_temp = 8
        col_pcon = 2
        col_ppor = 14
        col_fden = 31
    else:
        sys.exit('-- Column IDX not defined for this test --')
    return col_time, col_temp, col_pcon, col_ppor, col_fden
