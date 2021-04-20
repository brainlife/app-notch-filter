#!/usr/local/bin/python3

import json
import mne
import numpy as np
import os
import shutil


def notch_filter(raw, param_freqs_specific_or_start, param_freqs_end, param_freqs_step, 
                 param_picks_by_channel_types_or_names, param_picks_by_channel_indices,
                 param_filter_length, param_widths, param_trans_bandwidth, param_n_jobs,
                 param_method, param_iir_parameters, param_mt_bandwidth, param_p_value,
                 param_phase, param_fir_window, param_fir_design, param_pad):
    """Apply a notch filter using MNE Python and save the file once filtered.

    Parameters
    ----------
    raw: instance of mne.io.Raw
        Data to be filtered.
    param_freqs_specific_or_start: float or None
        Specific frequency to filter out in Hz or the start of the frequencies to filter out in Hz.
    param_freqs_end: float or None
        End of the interval of frequencies to filter out in Hz. This value is excluded. 
    param_freqs_step: float or None
        The step in Hz to filter out specific frequencies (for instance the power lines harmonics) 
        between param_freqs_start and param_freqs_end.
    param_picks_by_channel_types_or_names: str, list of str, or None 
        Channels to include. In lists, channel type strings (e.g., ['meg', 'eeg']) will pick channels of those types, channel name 
        strings (e.g., ['MEG0111', 'MEG2623']) will pick the given channels. Can also be the string values “all” 
        to pick all channels, or “data” to pick data channels. None (default) will pick all data channels. Note 
        that channels in info['bads'] will be included if their names are explicitly provided.
    param_picks_by_channel_indices: list of int, slice, or None
        Channels to include. Slices (e.g., "0, 10, None" and lists of integers are interpreted as channel indices. 
        None (default) will pick all data channels. This parameter must be set to None if param_picks_by_channel_types_or_names 
        is not None. Note that channels in info['bads'] will be included if their indices are explicitly provided.
    param_filter_length: str
        Length of the FIR filter to use (if applicable). Can be ‘auto’ (default) : the filter length is chosen based 
        on the size of the transition regions, or an other str (human-readable time in units of “s” or “ms”: 
        e.g., “10s” or “5500ms”. 
    param_widths: float or None
        Width of the stop band in Hz. If None, freqs / 200 is used. Default is None.
    param_trans_bandwidth: float
        Width of the transition band in Hz. Default is 1.
    param_n_jobs: int
        Number of jobs to run in parallel. Default is 1.
    param_method: str
        ‘fir’ (default) will use overlap-add FIR filtering, ‘iir’ will use IIR forward-backward filtering (via filtfilt).
        Can be ‘spectrum_fit’. 
    param_iir_parameters: dict or None
        Dictionary of parameters to use for IIR filtering. If iir_params is None and method=”iir”, 
        4th order Butterworth will be used. Default is None.
    param_mt_bandwidth: float or None
        The bandwidth of the multitaper windowing function in Hz. Default is None.
    param_p_value: float
        P-value to use in F-test thresholding to determine significant sinusoidal components 
        to remove when method=’spectrum_fit’ and freqs=None. Default is 0.05.
    param_phase: str
        Phase of the filter, only used if method='fir'. Either 'zero' (default) or 'zero-double'.
    param_fir_window: str
        The window to use in FIR design, can be “hamming” (default), “hann”, or “blackman”.
    param_fir_design: str
        Can be “firwin” (default) or “firwin2”.
    param_pad: str
        The type of padding to use. Supports all numpy.pad() mode options. Can also be “reflect_limited” (default).

    Returns
    -------
    raw_filtered: instance of mne.io.Raw
        The raw data after filtering.
    """

    raw.load_data()

    # Raise error if both param picks are not None
    if param_picks_by_channel_types_or_names is not None and param_picks_by_channel_indices is not None:
        value_error_message = f"You can't provide values for both " \
                              f"param_picks_by_channel_types_or_names and " \
                              f"param_picks_by_channel_indices. One of them must be " \
                              f"set to None."
        raise ValueError(value_error_message)
    # Define param_picks
    elif param_picks_by_channel_types_or_names is None and param_picks_by_channel_indices is not None:
        param_picks = param_picks_by_channel_indices
    elif param_picks_by_channel_types_or_names is not None and param_picks_by_channel_indices is None:
        param_picks = param_picks_by_channel_types_or_names
    else:
        param_picks = None       

    # Notch between two frequencies
    if param_freqs_end is not None:
        freqs = np.arange(param_freqs_specific_or_start, param_freqs_end, param_freqs_step)
    # Notch one frequency
    else:
        freqs = param_freqs_specific_or_start

    raw_notch_filtered = raw.notch_filter(freqs=freqs, picks=param_picks,
                                          filter_length=param_filter_length, notch_widths=param_widths,
                                          trans_bandwidth=param_trans_bandwidth, n_jobs=param_n_jobs,
                                          method=param_method, iir_params=param_iir_parameters,
                                          mt_bandwidth=param_mt_bandwidth, p_value=param_p_value,
                                          phase=param_phase, fir_window=param_fir_window,
                                          fir_design=param_fir_design, pad=param_pad)

    # Save file
    raw_notch_filtered.save("out_dir_notch_filter/meg.fif", overwrite=True)

    return raw_notch_filtered


def _compute_snr(meg_file):
    # Compute the SNR

    # select only MEG channels and exclude the bad channels
    meg_file = meg_file.pick_types(meg=True, exclude='bads')

    # create fixed length events
    array_events = mne.make_fixed_length_events(meg_file, duration=10)

    # create epochs
    epochs = mne.Epochs(meg_file, array_events)

    # mean signal amplitude on each epoch
    epochs_data = epochs.get_data()
    mean_signal_amplitude_per_epoch = epochs_data.mean(axis=(1, 2))  # mean on channels and times

    # mean across all epochs and its std error
    mean_final = mean_signal_amplitude_per_epoch.mean()
    std_error_final = np.std(mean_signal_amplitude_per_epoch, ddof=1) / np.sqrt(
        np.size(mean_signal_amplitude_per_epoch))

    # compute SNR
    snr = mean_final / std_error_final

    return snr


def _generate_report(data_file_before, raw_before_preprocessing, raw_after_preprocessing, bad_channels,
                     comments_about_filtering, notch_freqs_start, snr_before, snr_after):
    # Generate a report

    # Instance of mne.Report
    report = mne.Report(title='Results of filtering ', verbose=True)

    # Plot MEG signals in temporal domain
    fig_raw = raw_before_preprocessing.pick(['meg'], exclude='bads').plot(duration=10, scalings='auto', butterfly=False,
                                                                          show_scrollbars=False, proj=False)
    fig_raw_maxfilter = raw_after_preprocessing.pick(['meg'], exclude='bads').plot(duration=10, scalings='auto',
                                                                                   butterfly=False,
                                                                                   show_scrollbars=False, proj=False)

    # Plot power spectral density
    fig_raw_psd = raw_before_preprocessing.plot_psd()
    fig_raw_maxfilter_psd = raw_after_preprocessing.plot_psd()

    # Add figures to report
    report.add_figs_to_section(fig_raw, captions='MEG signals before filtering', section='Temporal domain')
    report.add_figs_to_section(fig_raw_maxfilter, captions='MEG signals after filtering',
                               comments=comments_about_filtering,
                               section='Temporal domain')
    report.add_figs_to_section(fig_raw_psd, captions='Power spectral density before filtering',
                               section='Frequency domain')
    report.add_figs_to_section(fig_raw_maxfilter_psd, captions='Power spectral density after filtering',
                               comments=comments_about_filtering,
                               section='Frequency domain')

    # Check if MaxFilter was already applied on the data
    if raw_before_preprocessing.info['proc_history']:
        sss_info = raw_before_preprocessing.info['proc_history'][0]['max_info']['sss_info']
        tsss_info = raw_before_preprocessing.info['proc_history'][0]['max_info']['max_st']
        if bool(sss_info) or bool(tsss_info) is True:
            message_channels = f'Bad channels have been interpolated during MaxFilter'
        else:
            message_channels = bad_channels
    else:
        message_channels = bad_channels

    # Put this info in html format
    # Give some info about the file before preprocessing
    sampling_frequency = raw_before_preprocessing.info['sfreq']
    highpass = raw_before_preprocessing.info['highpass']
    lowpass = raw_before_preprocessing.info['lowpass']

    # Put this info in html format
    # Info on data
    html_text_info = f"""<html>

        <head>
            <style type="text/css">
                table {{ border-collapse: collapse;}}
                td {{ text-align: center; border: 1px solid #000000; border-style: dashed; font-size: 15px; }}
            </style>
        </head>

        <body>
            <table width="50%" height="80%" border="2px">
                <tr>
                    <td>Input file: {data_file_before}</td>
                </tr>
                <tr>
                    <td>Bad channels: {message_channels}</td>
                </tr>
                <tr>
                    <td>Sampling frequency before preprocessing: {sampling_frequency}Hz</td>
                </tr>
                <tr>
                    <td>Highpass before preprocessing: {highpass}Hz</td>
                </tr>
                <tr>
                    <td>Lowpass before preprocessing: {lowpass}Hz</td>
                </tr>
            </table>
        </body>

        </html>"""

    # Info on SNR
    html_text_snr = f"""<html>

    <head>
        <style type="text/css">
            table {{ border-collapse: collapse;}}
            td {{ text-align: center; border: 1px solid #000000; border-style: dashed; font-size: 15px; }}
        </style>
    </head>

    <body>
        <table width="50%" height="80%" border="2px">
            <tr>
                <td>SNR before filtering: {snr_before}</td>
            </tr>
            <tr>
                <td>SNR after filtering: {snr_after}</td>
            </tr>
        </table>
    </body>

    </html>"""

    # Info on SNR
    html_text_summary_filtering = f"""<html>

    <head>
        <style type="text/css">
            table {{ border-collapse: collapse;}}
            td {{ text-align: center; border: 1px solid #000000; border-style: dashed; font-size: 15px; }}
        </style>
    </head>

    <body>
        <table width="50%" height="80%" border="2px">
            <tr>
                <td>Temporal filtering: {comments_about_filtering}</td>
            </tr>
            <tr>
                <td>Notch: {notch_freqs_start}</td>
            </tr>
        </table>
    </body>

    </html>"""

    # Add html to reports
    report.add_htmls_to_section(html_text_info, captions='MEG recording features', section='Data info', replace=False)
    report.add_htmls_to_section(html_text_summary_filtering, captions='Summary filtering applied',
                                section='Filtering info', replace=False)
    report.add_htmls_to_section(html_text_snr, captions='Signal to noise ratio', section='Signal to noise ratio',
                                replace=False)

    # Save report
    report.save('out_dir_report/report_filtering.html', overwrite=True)


def main():

    # Generate a json.product to display messages on Brainlife UI
    dict_json_product = {'brainlife': []}

    # Load inputs from config.json
    with open('config.json') as config_json:
        config = json.load(config_json)

    # Read the files
    data_file = config.pop('fif')
    raw = mne.io.read_raw_fif(data_file, allow_maxshield=True)

    # Read the crosstalk file
    cross_talk_file = config.pop('crosstalk')
    if os.path.exists(cross_talk_file) is True:
        shutil.copy2(cross_talk_file, 'out_dir_notch_filter/crosstalk_meg.fif')  # required to run a pipeline on BL

    # Read the calibration file
    calibration_file = config.pop('calibration')
    if os.path.exists(calibration_file) is True:
        shutil.copy2(calibration_file, 'out_dir_notch_filter/calibration_meg.dat')  # required to run a pipeline on BL

    # Read destination file 
    destination_file = config.pop('destination')
    if os.path.exists(destination_file) is True:
        shutil.copy2(destination_file, 'out_dir_notch_filter/destination.fif')  # required to run a pipeline on BL

    # Read head pos file
    head_pos = config.pop('headshape')
    if os.path.exists(head_pos) is True:
        shutil.copy2(head_pos, 'out_dir_notch_filter/headshape.pos')  # required to run a pipeline on BL

    # Read events file 
    events_file = config.pop('events')
    if os.path.exists(events_file) is True:
        shutil.copy2(events_file, 'out_dir_notch_filter/events.tsv')  # required to run a pipeline on BL

    # Check for None parameters 

    # freqs specific or start
    if config['param_freqs_specific_or_start'] == "":
        config['param_freqs_specific_or_starts'] = None  # when App is run on Bl, no value for this parameter corresponds to ''
        if config['param_method'] != 'spectrum_fit':
            value_error_message = f'This frequency can only be None when method is spectrum_fit.' 
            # Raise exception
            raise ValueError(value_error_message)

    # freqs end
    if config['param_freqs_end'] == "":
        config['param_freqs_end'] = None  # when App is run on Bl, no value for this parameter corresponds to ''

    # freqs step
    if config['param_freqs_step'] == "":
        config['param_freqs_step'] = None  # when App is run on Bl, no value for this parameter corresponds to '' 

    # picks notch by channel types or names
    if config['param_picks_by_channel_types_or_names'] == "":
        config['param_picks_by_channel_types_or_names'] = None  # when App is run on Bl, no value for this parameter corresponds to ''

    # picks notch by channel indices
    if config['param_picks_by_channel_indices'] == "":
        config['param_picks_by_channel_indices'] = None  # when App is run on Bl, no value for this parameter corresponds to ''

    # notch widths
    if config['param_widths'] == "":
        config['param_widths'] = None  # when App is run on Bl, no value for this parameter corresponds to ''  

    # iir parameters
    if config['param_iir_parameters'] == "":
        config['param_iir_parameters'] = None  # when App is run on Bl, no value for this parameter corresponds to ''  

    # mt bandwidth
    if config['param_mt_bandwidth'] == "":
        config['param_mt_bandwidth'] = None  # when App is run on Bl, no value for this parameter corresponds to ''    

    # Deal with param_picks_by_channel_indices parameter

    # When the App is run locally
    picks = config['param_picks_by_channel_indices']

    # In case of a slice
    if isinstance(picks, str) and picks.find(",") != -1 and picks is not None:
        picks = list(map(int, picks.split(', ')))
        if len(picks) == 2:
            config['param_picks_by_channel_indices'] = slice(picks[0], picks[1])
        elif len(picks) == 3:
            config['param_picks_by_channel_indices'] = slice(picks[0], picks[1], picks[2])
        else:
            value_error_message = f"If you want to select channels using a slice, you must give two or three elements."
            raise ValueError(value_error_message)

    # Comments messages
    if config['param_freqs_specific_or_start'] is not None and config['param_freqs_end'] is None:
        comments_notch = f"{config['param_freqs_specific_or_start']}Hz" 
    elif config['param_freqs_specific_or_start'] is not None and config['param_freqs_end'] is not None:  
        comments_notch = f"Between {config['param_freqs_specific_or_start']} and {config['param_freqs_end']}Hz"
        if config['param_freqs_step'] is not None:  
            comments_notch = f"Between {config['param_freqs_specific_or_start']} and " \
                             f"{config['param_freqs_end']}Hz every {config['param_freqs_step']}Hz"

    # Keep bad channels in memory
    bad_channels = raw.info['bads']

    # Define kwargs
    # Delete keys values in config.json when this app is executed on Brainlife
    if '_app' and '_tid' and '_inputs' and '_outputs' in config.keys():
        del config['_app'], config['_tid'], config['_inputs'], config['_outputs'] 
    kwargs = config  

    # Apply temporal filtering
    raw_copy = raw.copy()
    raw_notch_filtered = notch_filter(raw_copy, **kwargs)
    del raw_copy

    # Success message in product.json    
    dict_json_product['brainlife'].append({'type': 'success', 'msg': 'Notch filter was applied successfully.'})

    # Compute SNR
    # snr_before = _compute_snr(raw)
    # snr_after = _compute_snr(raw_filtered)

    # Generate a report
    # _generate_report(data_file, raw, raw_filtered, bad_channels, comments_about_filtering,
    #                  comments_notch, snr_before, snr_after)

    # Save the dict_json_product in a json file
    with open('product.json', 'w') as outfile:
        json.dump(dict_json_product, outfile)


if __name__ == '__main__':
    main()
