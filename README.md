# app-notch-filter

This is a draft of a future Brainlife App that notch filters MEG signals using the MNE function 
[`mne.io.Raw.notch_filter`](https://mne.tools/stable/generated/mne.io.Raw.html#mne.io.Raw.notch_filter).

# app-temporal-filtering documentation

1) Filter MEG signals
2) First, apply a bandpass, highpass, or lowpass filter, then optionally apply a notch filter and resample the data  
3) Input file is:
    * a MEG file in `.fif` format,
4) Input parameters are:
    * param_freqs_specific_or_start: `float`, optional, frequency to notch filter in Hz. Default is 50.
    * freqs_end: `float`, optional, end of the interval of frequencies to filter out in Hz. This value is excluded. Default is 251.  
    * freqs_step: `float`, optional, the step in Hz to filter out specific frequencies (for instance the power lines harmonics) 
        between param_freqs_start and param_freqs_end. Default is 50.
    * picks: `str`or `list`, optional, channels to include. Default is `None`. 
    * filter_length: `str`, length of the FIR filter to use in human-readable time units. Default is `auto`. 
    * widths: `float`, optional, width of the stop band in Hz. Default is `None`.
    * trans_bandwidth: `float`, width of the transition band in Hz. Default is 1.0.
    * n_jobs: `int`, number of jobs to run in parallel. Default is 1.
    * method: `str`, 'fir' will use overlap-add FIR filtering, 'iir' will use IIR forwar-backward filtering. Default is 'fir'.
    * iir_params: `dict`, optional, dictionary of parameters to use for IIR filtering. To know how to define the dictionary go 
        [there](https://mne.tools/stable/generated/mne.filter.construct_iir_filter.html#mne.filter.construct_iir_filter). Default is `None`. 
    * mt_bandwidth: `float`, optional, the bandwidth of the multitaper windowing function in Hz. Default is `None`.
    * p_value: `float`, p-value to use in F-test thresholding to determine significant sinusoidal components. Default is 0.05.
    * phase: `str`, phase of the filter, only used if method='fir'. Default is 'zero'.
    * fir_window: `str`, the window to use in FIR design. Default is 'hamming'.
    * fir_design: `str`. Default is 'firwin'.
    * pad: `str`, the type of padding to use. Default is 'reflect_limited'.

This list along with the parameters' default values correspond to the 0.22.0 version of MNE Python.  

5) Ouput files are:
    * a `.fif` MEG file after filtering,
    * an `.html` report containing figures.

### Authors
- [Aurore Bussalb](aurore.bussalb@icm-institute.org)

### Contributors
- [Aurore Bussalb](aurore.bussalb@icm-institute.org)
- [Maximilien Chaumon](maximilien.chaumon@icm-institute.org)

### Funding Acknowledgement
brainlife.io is publicly funded and for the sustainability of the project it is helpful to Acknowledge the use of the platform. We kindly ask that you acknowledge the funding below in your code and publications. Copy and past the following lines into your repository when using this code.

[![NSF-BCS-1734853](https://img.shields.io/badge/NSF_BCS-1734853-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1734853)
[![NSF-BCS-1636893](https://img.shields.io/badge/NSF_BCS-1636893-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1636893)
[![NSF-ACI-1916518](https://img.shields.io/badge/NSF_ACI-1916518-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1916518)
[![NSF-IIS-1912270](https://img.shields.io/badge/NSF_IIS-1912270-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1912270)
[![NIH-NIBIB-R01EB029272](https://img.shields.io/badge/NIH_NIBIB-R01EB029272-green.svg)](https://grantome.com/grant/NIH/R01-EB029272-01)

### Citations
1. Avesani, P., McPherson, B., Hayashi, S. et al. The open diffusion data derivatives, brain data upcycling via integrated publishing of derivatives and reproducible open cloud services. Sci Data 6, 69 (2019). [https://doi.org/10.1038/s41597-019-0073-y](https://doi.org/10.1038/s41597-019-0073-y)

## Running the App 

### On Brainlife.io

This App has not yet been registered in Brainlife.io.

### Running Locally (on your machine)

1. git clone this repo
2. Inside the cloned directory, create `config.json` with something like the following content with paths to your input 
   files and values of the input parameters (see `config.json.example`).

```json
{
  "fif": "rest1-raw.fif"
}
```

3. Launch the App by executing `main`

```bash
./main
```

## Output

The output files are a MEG file in `.fif` format and an `.html` report.

