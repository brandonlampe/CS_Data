# Comments for test: 175_04
Following the initial increase in pressure from zero to 20 MPa, the Schuler gauges stopped working.
Therefore, volume deformation was measured using an Isco pump.  However, fluid temperature
and system tightness influence the volume deformation measurements made with the Isco pump.
Because of these influences, corrections have been made to account for variation of the
confining fluid temperature and for observed leaks in the system.

## Temperature Adjustment
A modification factor was applied to the fractional density.
This was applied by applying a ```MOD_FACT = 0.0016``` to the interpreted
fractional density.

```FDEN_INTERP = FDEN_INTERP + np.cumsum(DELTA_TEMP) * MOD_FACT```

```MOD_FACT``` is 0.0016 per degree Celsius.


## Fit Types

Stage 1
- From 2.09 to 2.9 days
- Logistic + Exponential

Stage 2
- From 2.9 through 19.9 days
- Exponential
