# Comments For Consolidation Test: 175_01
_Note:_ herein, the phrase "TEST-NUMBER" will imply the insertion of "175_01".  This format will
often be used when describing local directories.

_Fractional Density Measurements:_ Fractional density calculations were made using measured data of
the sample's initial and transient volume.  These volume change measurements were made using a
a combination of Schüler gauges and fluid metering devices (either with Isco pump or dilatometer).
During loading and unloading of a sample, Schüler gauges were exclusively used to calculate volume
changes.  Whereas, during creep deformation a combination of these devices were used.  The exact
combination of Schüler guages and fluid metering devices used is described in column "A" of
worksheet "FmtData" of the TEST-NUMBER.xlsx workbook.  Because measuring devices occasionally quit
working during a test, often the calculated fractional density measurements were made using a
varing combination of three or more devices (e.g., Schüler Gauge 01, Schüler Gauge 02, and Isco).

Following the initial increase in pressure from zero to 19.8 MPa with the Isco Pump,
Schuler gauges did not function during this test; therefore, deformation during initial loading was
calculated based on an approximated fluid compressibility and metered fluid out of the Isco pump.
The initial fractional density (after completing the preconsolidation) was obtained from
"dunk tank" values.

## Test Data
Raw test data is contained in: TEST-NUMBER.xlsx

Additionally, calculated values of fractional density have been calculated in TEST-NUMBER.xlsx and
exported to TEST-NUMBER.csv, where the .csv file format allows for easy cross-platform importing
and analysis.

## Temperature Adjustment
No adjustment for temperature was made during this test

## Fit Types
To allow for the calculation of derivatives from test data, analytical expressions were fit to the
test data.  Unique analytical expressions were fit to the loading, creep, and unloading portions of
the consolidation test.

### Loading
- An analytical expression was fit to the calculated fractional density with respect to confining
pressure.
- A summary of the fit to the loading stage has been in the LOADING_FIT directory, with the file
name: TEST-NUMBER_ LOAD_FITREPORT.csv
- All data of the fit to the loading stage has been in the LOADING_FIT directory, with the file
name: TEST-NUMBER_ LOAD_OUT.csv

### Creep
- A summary of the fit to the creep stage has been in the CREEP_FIT directory, with the file
name: TEST-NUMBER_ CREEP_FITREPORT.csv
- All data of the fit to the creep (constant pressure) stage has been in the CREEP_FIT directory,
with the file name: TEST-NUMBER_ CREEP_OUT.csv

### Unloading
- No unloading data was obtained during this test

## Final Results
- The final fit results, which include the fractional density and strain rate calculations, are
contained in the directory labeled FINAL.  Test results stored in this directory have been developed
such that they may be used to make plotting the data convienent, as the files only contain a couple
thousand measurements.  __Note:__ files ending with _.npy_ are binary Numpy arrays of the data.
- These results have been seperated into the following categories:
    + LOAD
    + CREEP
    + UNLOAD
    + COMB
- The files ending with LOAD, CREEP, and UNLOAD contain the data for the respetive part of the test.
- The files ending with COMB contain the combined data of all tests parts.
