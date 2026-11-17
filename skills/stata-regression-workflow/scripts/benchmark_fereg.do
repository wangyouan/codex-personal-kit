version 18.0
clear all
set more off
args mode
local repeats = cond("`mode'" == "accuracy",0,6)
set seed 481735
set sortseed 481735
local cores = min(4,c(processors))
set processors `cores'
display "STATA=" c(stata_version) " MP=" c(MP) " PROCESSORS=" c(processors)
which reghdfe
which ppmlhdfe
which fereg
which feppml

* Simulated unbalanced firm-year panel with persistent firm-level disturbances.
set obs 30000
generate long firm = _n
generate int industry = ceil(60*runiform())
generate double firm_fe = rnormal(0,.4)
expand 20
bysort firm: generate int year = 2005 + _n - 1
drop if runiform() < .15
egen int industry_year = group(industry year)
bysort industry_year (firm): generate double cell_fe = rnormal(0,.3) if _n == 1
by industry_year: replace cell_fe = cell_fe[1]
sort firm year
generate double x1 = .6*firm_fe + .4*cell_fe + rnormal()
generate double x2 = -.3*firm_fe + rnormal()
generate double x3 = .5*x1 + rnormal()
by firm: generate double disturbance = rnormal() if _n == 1
by firm: replace disturbance = .55*disturbance[_n-1] + rnormal() if _n > 1
generate double y_linear = .3*x1 - .2*x2 + .1*x3 + firm_fe + cell_fe + disturbance
generate long y_count = rpoisson(exp(-.4 + .3*x1 - .2*x2 + .1*x3 + firm_fe + cell_fe))
isid firm year
generate long rowid = _n
quietly count if y_count == 0
display "ROWS=" _N " ZERO_COUNTS=" r(N)

tempfile fits timings
tempname pf pt bv vv
postfile `pf' str6 model str10 command str2 term double coef double se long N double df_r long clusters using `fits'
postfile `pt' str6 model str10 command int repetition double seconds using `timings'

foreach model in linear count {
    if "`model'" == "linear" {
        local baseline reghdfe
        local candidate fereg
    }
    else {
        local baseline ppmlhdfe
        local candidate feppml
    }
    foreach cmd in `baseline' `candidate' {
        sort rowid
        local threadopt
        if "`cmd'" == "`candidate'" local threadopt threads(`cores')
        `cmd' y_`model' x1 x2 x3, absorb(firm industry_year) vce(cluster firm) `threadopt'
        generate byte sample_`cmd' = e(sample)
        matrix `bv' = e(b)
        matrix `vv' = e(V)
        foreach x in x1 x2 x3 {
            local j = colnumb(`bv',"`x'")
            post `pf' ("`model'") ("`cmd'") ("`x'") (`bv'[1,`j']) (sqrt(`vv'[`j',`j'])) (e(N)) (e(df_r)) (e(N_clust))
        }
    }
    quietly count if sample_`baseline' != sample_`candidate'
    display "SAMPLE_DIFFERENCES `model'=" r(N)
    if "`model'" == "count" {
        bysort firm: egen long firm_count_total = total(y_count)
        quietly count if sample_`baseline' != (firm_count_total > 0)
        display "PPML_SAMPLE_VS_ALL_ZERO_FIRM_EXCLUSION=" r(N)
    }
    forvalues rep = 1/`repeats' {
        local order `baseline' `candidate'
        if mod(`rep',2)==0 local order `candidate' `baseline'
        foreach cmd of local order {
            sort rowid
            local threadopt
            if "`cmd'" == "`candidate'" local threadopt threads(`cores')
            timer clear 1
            timer on 1
            quietly `cmd' y_`model' x1 x2 x3, absorb(firm industry_year) vce(cluster firm) `threadopt'
            timer off 1
            quietly timer list 1
            post `pt' ("`model'") ("`cmd'") (`rep') (r(t1))
        }
    }
}
postclose `pf'
postclose `pt'

use `fits', clear
format coef se %24.16e
export delimited using "coefficients.csv", datafmt replace
if !`repeats' {
    display "ACCURACY_COMPLETE"
    exit
}
use `timings', clear
export delimited using "timings.csv", replace
collapse (p50) median_s=seconds (min) min_s=seconds (max) max_s=seconds, by(model command)
export delimited using "timing_summary.csv", replace
list, noobs
display "BENCHMARK_COMPLETE"
exit
