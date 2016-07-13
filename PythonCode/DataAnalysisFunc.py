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
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from matplotlib.ticker import FuncFormatter


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


def gompertz(x, intercept, start, a, b, c):
    fden = intercept + a * np.exp(-np.exp(b - c * (x - start)))
    return fden


def schnute(x, start, end, a, b, c, d):
    fden = (c**b + (d**b - c**b) * (1 - np.exp(-a * (x - start))) /
                                   (1 - np.exp(-a * (end - start))))**(1 / b)
    return fden


def linear(x, slope, intercept):
    fden = slope * x + intercept
    return fden


def fit_definition_str(which_mod):
    """ provides a string that defines the fitting function
        -   these function defintions (defined via strings)
            will be called by "fit_fden"
    """
    def_str = which_mod - 1

    # model 1
    gompertz_1 = 'def gompertz(x, intercept, start, a, b, c):'
    gompertz_2 = '    fden = intercept + a * exp(-exp(b - c * (x - start)))'
    gompertz_3 = '    return fden'
    str_gompertz = '\n'.join([gompertz_1, gompertz_2, gompertz_3])

    # mode1 2
    schnute_1 = 'def schnute(x, start, end, a, b, c, d):'
    schnute_2a = '    fden = (c**b + (d**b - c**b) * (1 - exp(-a*(x - start)))'
    schnute_2b = '/(1 - exp(-a*(end - start))))**(1 / b)'
    schnute_2 = schnute_2a + schnute_2b
    schnute_3 = '    return fden'
    str_schnute = '\n'.join([schnute_1, schnute_2, schnute_3])

    # model 3
    linear_1 = 'def linear(x, slope, intercept):'
    linear_2 = '    fden = slope * x + intercept'
    linear_3 = '    return fden'
    str_linear = '\n'.join([linear_1, linear_2, linear_3])

    # model 4
    gen_logistic_1 = 'def gen_logistic(x, start, a, b, c, d):'
    gen_logistic_2 = '    fden = a / (d + exp(b - c*(x - start)))'
    gen_logistic_3 = '    return fden'
    str_gen_logistic = '\n'.join([gen_logistic_1, gen_logistic_2,
                                  gen_logistic_3])

    script_all_func = [str_gompertz, str_schnute, str_linear, str_gen_logistic]
    return script_all_func[def_str]


def fit_fden(fden_interp, dur_day_interp, which_mod, whole_domain):
    '''fit the fractional density using the LMFIT package
        Non-Linear Least-Squars Minimizations and Curve Fitting Library
        ref: https://lmfit.github.io/lmfit-py/builtin_models.html
        ref: http://cars9.uchicago.edu/software/python/lmfit/index.html
        CITATION: http://dx.doi.org/10.5281/zenodo.11813
    '''
    #  call function that defines which eqn will be used for the fit
    script = fit_definition_str(which_mod)

    if which_mod == 1:
        print("Gompertz equation was chosen")
        gompertz_mod = lmfit.models.ExpressionModel(
            'gompertz(x,intercept,start,a,b,c)',
            init_script=script,
            independent_vars=['x'])
        # define initial guess values for parameters for each model
        parms = gompertz_mod.make_params()
        parms['intercept'].set(value=0.6, vary=True)
        parms['start'].set(value=dur_day_interp.min(), vary=False)
        parms['a'].set(value=5.0, vary=True)
        parms['b'].set(value=1.0, vary=True)
        parms['c'].set(value=1.0, vary=True)

        model_result = gompertz_mod.fit(fden_interp, parms, x=dur_day_interp)
        parm_result = model_result.best_values
        fden_fit_interp = model_result.eval(x=whole_domain,
                                            start=parm_result["start"],
                                            intercept=parm_result["intercept"],
                                            a=parm_result["a"],
                                            b=parm_result["b"],
                                            c=parm_result["c"])
    if which_mod == 2:
        # Schnute's equation
        print("Schnute's equation was chosen")
        schnute_mod = lmfit.models.ExpressionModel(
            'schnute(x,start,end,a,b,c,d)',
            init_script=script,
            independent_vars=['x'])
        # define initial guess values for parameters for each model
        parms = schnute_mod.make_params()
        parms['start'].set(value=dur_day_interp.min(), vary=False)
        parms['end'].set(value=dur_day_interp.max(), vary=False)
        parms['a'].set(value=0.1, vary=True)
        parms['b'].set(value=5.0, vary=True)
        parms['c'].set(value=fden_interp.min() * 0.95, vary=True)
        parms['d'].set(value=fden_interp.max() * 1.05, vary=True)

        model_result = schnute_mod.fit(fden_interp, parms, x=dur_day_interp)
        parm_result = model_result.best_values
        fden_fit_interp = model_result.eval(x=whole_domain,
                                            start=parm_result["start"],
                                            end=parm_result["end"],
                                            a=parm_result["a"],
                                            b=parm_result["b"],
                                            c=parm_result["c"],
                                            d=parm_result["d"])
    if which_mod == 3:
        # linear function
        print("lienar equation was chosen")
        linear_mod = lmfit.models.ExpressionModel(
            'linear(x,slope,intercept)',
            init_script=script,
            independent_vars=['x'])
        # define initial guess values for parameters for each model
        parms = linear_mod.make_params()
        parms['slope'].set(value=-1.0, vary=True)
        parms['intercept'].set(value=2.0, vary=True)

        model_result = linear_mod.fit(fden_interp, parms,
                                      x=dur_day_interp)
        parm_result = model_result.best_values
        fden_fit_interp = model_result.eval(x=whole_domain,
                                            slope=parm_result["slope"],
                                            int=parm_result["intercept"])
    if which_mod == 4:
        # Generalized logistic function
        print("Generalized logistic equation was chosen")
        gen_logistic_mod = lmfit.models.ExpressionModel(
            'gen_logistic(x,start,a,b,c,d)',
            init_script=script,
            independent_vars=['x'])
        # define initial guess values for parameters for each model
        parms = gen_logistic_mod.make_params()
        parms['start'].set(value=dur_day_interp.min(), vary=True)
        parms['a'].set(value=5.0, vary=True)
        parms['b'].set(value=5.0, vary=True)
        parms['c'].set(value=0.5, vary=True)
        parms['d'].set(value=10, vary=True)

        model_result = gen_logistic_mod.fit(fden_interp, parms,
                                            x=dur_day_interp)
        parm_result = model_result.best_values
        fden_fit_interp = model_result.eval(x=whole_domain,
                                            start=parm_result["start"],
                                            a=parm_result["a"],
                                            b=parm_result["b"],
                                            c=parm_result["c"],
                                            d=parm_result["d"])
    return fden_fit_interp, model_result, script

    # if which_mod == 4:
    #     print("Logist (3 param) Fit Chosen")
    #     # class LinearModel = f(x; m,b)= mx + b
    #     step_mod = lmfit.models.StepModel(form='logistic', prefix='step_')
    #     # line_mod = lmfit.models.LinearModel(prefix='line_')
    #     # powr_mod = lmfit.models.PowerLawModel(prefix='powr_')

    #     # parms = line_mod.make_params(intercept=fden_interp.min(), slope=0.1)
    #     # parms = powr_mod.make_params(powr_amplitude=0.4, powr_exponent=1.0)
    #     parms = step_mod.make_params(step_center=2.09, step_sigma=0.001,
    #                                  step_amplitude=0.91)

    #     model_result = step_mod.fit(fden_interp, parms, x=dur_day_interp)
    #     parm_result = model_result.best_values

    #     fden_fit_interp = model_result.eval(x=whole_domain,
    #                                         step_amplitude=parm_result["step_amplitude"],
    #                                         step_center=parm_result["step_center"],
    #                                         step_sigma=parm_result["step_sigma"])


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
    if testname_str == '175_01':
        col_time = 1  # Excel Time Column (days)
        col_temp = 13  # confining fluid temperature (C)
        col_pcon = 3  # confining pressure (psi)
        col_ppor = 0  # pore pressure - none for this test
        col_fden = 38  # calculated fractional density (no Schuler Gauges)
    elif testname_str == '175_03':
        col_time = 1  # Excel Time Column (days)
        col_temp = 15  # confining fluid temperature (C)
        col_pcon = 5  # confining pressure (psi)
        col_ppor = 0  # pore pressure - none for this test
        col_fden = 37  # calculated fractional density
    elif testname_str == '175_04':
        col_time = 1  # Excel Time Column (days)
        col_temp = 13
        col_pcon = 3
        col_ppor = 0
        col_fden = 34
    elif testname_str == '175_09':
        col_time = 1  # Excel Time Column (days)
        col_temp = 8
        col_pcon = 2
        col_ppor = 14
        col_fden = 31
    elif testname_str == '90_04':
        col_time = 1  # Excel Time Column (days)
        col_temp = 13  # confining fluid temperature (C)
        col_pcon = 3  # confining pressure (psi)
        col_ppor = 0  # pore pressure - none for this test
        col_fden = 38  # calculated fractional density (Schul Avg & Isco)
    elif testname_str == '90_08':
        col_time = 1  # Excel Time Column (days)
        col_temp = 15  # confining fluid temperature (C)
        col_pcon = 5  # confining pressure (psi)
        col_ppor = 0  # pore pressure - none for this test
        col_fden = 39  # calculated fractional density (Schuler Avg)
    else:
        sys.exit('-- Column IDX not defined for this test --')
    return col_time, col_temp, col_pcon, col_ppor, col_fden

# '''
# Table.py

# A module/class for creating LaTeX deluxetable's.  In a nutshell, you create
# a table instance, add columns, set options, then call the pring method.'''

# import numpy
# import sigfig
# import os,string,re,sys
# import types

# float_types = [types.FloatType, numpy.float16, numpy.float32, numpy.float64,
#       numpy.float128]

# class Table:

#    def __init__(self, numcols, justs=None, fontsize=None, rotate=False,
#          tablewidth=None, tablenum=None, caption=None, label=None):

#       self.numcols = numcols
#       self.justs = justs
#       if self.justs is None:
#          self.justs = ['c' for i in range(numcols)]
#       else:
#          self.justs = list(justs)
#          if len(self.justs) != numcols:
#             raise ValueError, "Error, justs must have %d elements" % (numcols)
#       for just in self.justs:
#          if just not in ['c','r','l']:
#             raise ValueError, "Error, invalid character for just: %s" % just
#       self.fontsize = fontsize
#       self.rotate = rotate
#       self.tablewidth = tablewidth
#       self.tablenum = None
#       self.caption = caption
#       self.label = label
#       self.col_justs = []
#       self.headers = []
#       self.header_ids = []
#       # self.data is a list of data.  Each element of the list corresponds
#       #  to a separate "secton" of the table, headed by self.data_labels
#       # Each element of data should be a list of self.numcols items.
#       self.data = []
#       self.data_labels = []
#       self.data_label_types = []
#       self.sigfigs = []
#       self.nrows = []

#    def add_header_row(self, headers, cols=None):
#       '''Add a header row to the table.  [headers] should be a list of the
#       strings that will be in the header.  [cols], if specified, should be a
#       list of column indexes.  If [cols] is None, it is assummed the headers
#       are in order and there are no multicolumns.  If cols is specified, you
#       can indicate the the ith header spans several columns by setting the
#       ith value of cols to a 2-tuple of first and last columns for the span.'''

#       if cols is None:
#          if len(headers) != self.numcols:
#             raise ValueError, "Error, headers must be a list of length %d" %\
#                   self.numcols
#          self.headers.append(headers)
#          self.header_ids.append(range(self.numcols))
#       else:
#          ids = []
#          for item in cols:
#             if type(item) is types.IntType:
#                ids.append(item)
#             elif type(item) is types.TupleType:
#                ids += range(item[0],item[1]+1)

#          ids.sort
#          if ids != range(self.numcols):
#             raise ValueError, "Error, missing columns in cols"
#          self.headers.append(headers)
#          self.header_ids.append(cols)
#       return

#    def add_data(self, data, label="", sigfigs=2, labeltype='cutin'):
#       '''Add a matrix of data.  [data] should be a list with length equal to
#       the number of columns of the table.  Each item of [data] should be a
#       list or numpy array.  A list of strings will be inserved as is.  If
#       a column is a 1-D array of float type, the number of significant
#       figures will be set to [sigfigs].  If a column is 2D with shape
#       (N,2), it is treated as a value with uncertainty and the uncertainty
#       will be rounded to [sigfigs] and value will be rounded accordingly,
#       and both will be printed with parenthetical errors.  If a label is
#       given, it will be printed in the table with \cutinhead if labeltype
#       is 'cutin' or \sidehead if labeltype is 'side'.'''

#       if type(data) is not types.ListType:
#          raise ValueError, "data should be a list"
#       if len(data) != self.numcols:
#          raise ValueError, \
#                "Error, length of data mush match number of table columns"

#       for datum in data:
#          if type(datum) not in [types.ListType, numpy.ndarray]:
#             raise ValueError, "data must be list of lists and numpy arrays"
#          if len(numpy.shape(datum)) not in [1,2]:
#             raise ValueError, "data items must be 1D or 2D"

#       nrows = numpy.shape(data[0])[0]
#       for datum in data[1:]:
#          if numpy.shape(datum)[0] != nrows:
#             raise ValueError, "each data item must have same first dimension"
#       self.nrows.append(nrows)
#       if len(numpy.shape(sigfigs)) == 0:
#          self.sigfigs.append([sigfigs for i in range(self.numcols)])
#       else:
#          if len(numpy.shape(sigfigs)) != 1:
#             raise ValueError, \
#                "sigfigs must be scalar or have same length as number of columns"
#          self.sigfigs.append(sigfigs)
#       self.data_labels.append(label)
#       self.data_label_types.append(labeltype)
#       self.data.append(data)

#    def print_table(self, fp=None):
#       if fp is None:
#          fp = sys.stdout
#       elif type(fp) is type(""):
#          fp = open(fp, 'w')
#          we_open = True
#       else:
#          we_open = False

#       self.print_preamble(fp)
#       self.print_header(fp)
#       self.print_data(fp)
#       self.print_footer(fp)
#       if we_open:
#          fp.close()

#    def print_preamble(self, fp):
#       cols = "".join(self.justs)
#       fp.write("\\begin{deluxetable}{%s}\n" % cols)
#       if self.fontsize: fp.write("\\tabletypesize{%s}\n" % str(self.fontsize))
#       if self.rotate: fp.write("\\rotate\n")
#       if self.tablewidth is not None:
#          fp.write("\\tablewidth{%s}\n" % str(self.tablewidth))
#       else:
#          fp.write("\\tablewidth{0pc}\n")
#       if self.tablenum:  fp.write("\\tablenum{%s}\n" % str(self.tablenum))
#       fp.write("\\tablecolumns{%d}\n" % self.numcols)
#       if self.caption:
#          if self.label:
#             lab = "\\label{%s}" % (self.label)
#             fp.write("\\tablecaption{%s}\n" % (str(self.caption)+lab))

#    def print_header(self,fp):
#       fp.write("\\tablehead{\n")

#       for i,headers in enumerate(self.headers):
#          end = ['\\\\\n',''][i == len(self.headers)-1]
#          for j,header in enumerate(headers):
#             sep = [end,'&'][j < len(headers)-1]
#             if len(numpy.shape(self.header_ids[i][j])) == 1:
#                length = self.header_ids[i][j][1] - self.header_ids[i][j][0] + 1
#                fp.write("\\multicolumn{%d}{c}{%s} %s " % (length, header,sep))
#             else:
#                fp.write("\\colhead{%s} %s " % (header,sep))
#       fp.write("}\n")

#    def print_data(self,fp):
#       fp.write("\\startdata\n")

#       for i,data in enumerate(self.data):
#          if self.data_labels[i] != '':
#             if self.data_label_types == "cutin":
#                fp.write("\\cutinhead{%s}\n" % self.data_labels[i])
#             else:
#                fp.write("\\sidehead{%s}\n" % self.data_labels[i])

#          rows = []
#          for j in range(numpy.shape(data[0])[0]):
#             rows.append([])
#             for k in range(len(data)):
#                sf = self.sigfigs[i][k]
#                if len(numpy.shape(data[k])) == 1:
#                   if type(data[k][j]) in float_types:
#                      if numpy.isnan(data[k][j]):
#                         rows[-1].append('\\ldots')
#                      else:
#                         rows[-1].append(sigfig.round_sig(data[k][j], sf))
#                   else:
#                      rows[-1].append(str(data[k][j]))
#                else:
#                   print data[k]
#                   if numpy.isnan(data[k][j,0]):
#                      val = "\\ldots"
#                   else:
#                      val = sigfig.round_sig_error(data[k][j,0],data[k][j,1],sf,
#                             paren=True)
#                   rows[-1].append(val)

#          for row in rows:
#             fp.write(" & ".join(row))
#             fp.write("\\\\\n")

#       fp.write("\\enddata\n")

#    def print_footer(self, fp):
#       fp.write("\\end{deluxetable}\n")
