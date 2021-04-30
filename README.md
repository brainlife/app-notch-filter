# app-notch-filter

This is the repository of a Brainlife App that notch filters MEG signals using the MNE function 
[`mne.io.Raw.notch_filter`](https://mne.tools/stable/generated/mne.io.Raw.html#mne.io.Raw.notch_filter).

# app-notch-filter documentation

1) Filter MEG signals
2) Apply a notch filter 
3) Input file is:
    * a MEG file in `.fif` format,
    * an optional fine calibration file in `.dat`,
    * an optional crosstalk compensation file in `.fif`,
    * an optional head position file in `.pos`,
    * an optional destination file in `.fif`,
    * an optional event file in `.tsv`.
4) Input parameters are:
    * `param_freqs_specific_or_start`: `float`, optional, frequency to notch filter in Hz. Default is 50.
    * `param_freqs_end`: `float`, optional, end of the interval of frequencies to filter out in Hz. This value is excluded. Default is 251. 
    * `param_freqs_step`: `float`, optional, the step in Hz to filter out specific frequencies (for instance the power lines harmonics) 
between param_freqs_start and param_freqs_end. Default is 50.
    * `param_picks_by_channel_types_or_names`: `str` or list of `str`, optional, channels to include. In lists, channel type strings (e.g., ["meg", "eeg"]) will pick channels of those types, channel name strings (e.g., ["MEG0111", "MEG2623"]) will pick the given channels. Can also be the string values “all” 
to pick all channels, or “data” to pick data channels. None (default) will pick all data channels. Note 
that channels in info['bads'] will be included if their names or indices are explicitly provided.
    * `param_picks_by_channel_indices`: list of `integers` or `slice`, optional, channels to include. Slices (e.g., "0, 10, 2" or "0, 10" if you don't want a step) and lists of integers are interpreted as channel indices. None (default) will pick all data channels. This parameter must be set to None if `param_picks_by_channel_types_or_names` is not `None`.
    * `param_filter_length`: `str` or `int`, length of the FIR filter to use in human-readable time units. Default is `auto`.  If int, specified length in samples. For fir_design=”firwin”, this should not be used.
    * `param_notch_widths`: `float`, optional, width of the stop band in Hz. Default is None.
    * `param_trans_bandwidth`: `float`, width of the transition band in Hz. Default is 1.0.
    * `param_n_jobs`: `int` or `str`, number of jobs to run in parallel. Can be 'cuda' if cupy is installed properly and method=’fir’. Default is 1.
    * `param_method`: `str`, 'fir' will use overlap-add FIR filtering, 'iir' will use IIR forwar-backward filtering. Default is 'fir'.
    * `param_iir_params`: `dict`, optional, dictionary of parameters to use for IIR filtering. To know how to define the dictionary go 
[there](https://mne.tools/stable/generated/mne.filter.construct_iir_filter.html#mne.filter.construct_iir_filter). Default is `None`. 
    * `param_mt_bandwidth`: `float`, optional, the bandwidth of the multitaper windowing function in Hz. Default is `None`.
    * `param_p_value`: `float`, p-value to use in F-test thresholding to determine significant sinusoidal components. Default is 0.05.
    * `param_phase`: `str`, phase of the filter, only used if method='fir'. Default is 'zero'.
    * `param_fir_window`: `str`, the window to use in FIR design. Default is 'hamming'.
    * `param_fir_design`: `str`. Default is 'firwin'.
    * `param_pad`: `str`, the type of padding to use. Default is 'reflect_limited'.

This list along with the parameters' default values correspond to the 0.22.0 version of MNE Python.

5) Ouput files are:
    * a `.fif` MEG file after notch filtering,
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

This App is still private on Brainlife.io.

### Running Locally (on your machine)

1. git clone this repo
2. Inside the cloned directory, create `config.json` with the same keys as in `config.json.example` but with paths to your input 
   files and values of the input parameters. For instance:

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

