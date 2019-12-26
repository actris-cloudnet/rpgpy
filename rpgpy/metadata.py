from collections import namedtuple

Meta= namedtuple('Meta', ('long_name', 'units', 'comment'))
Meta.__new__.__defaults__ = (None,) * len(Meta._fields)

METADATA = {
    'FileCode': Meta(
        long_name='file_code'),
    'HeaderLen': Meta(
        long_name='header_length',
        units='bytes'),
    'StartTime': Meta(
        long_name='start_time',
        comment='time of first sample in file'),
    'StopTime': Meta(
        long_name='stop_time',
        comment='time of last sample in file'),
    'CGProg': Meta(
        long_name='program_number',
        comment='chirp generator program number'),
    'ModelNo': Meta(
        long_name='model_number',
        comment='0=94GHz single polarisation radar, 1=94GHz dual polarisation radar'),
    'ProgName': Meta(
        long_name='program_name'),
    'CustName': Meta(
        long_name='customer_name'),
    'Freq': Meta(
        long_name='radar_frequency',
        units='GHz'),
    'AntSep': Meta(
        long_name='antenna_separation',
        units='m',
        comment='separation of both antenna axis (bistatic configuration)'),
    'AntDia': Meta(
        long_name='antenna_diameter',
        units='m'),
    'AntG': Meta(
        long_name='antenna_gain',
        comment='linear antenna gain'),
    'HPBW': Meta(
        long_name='half_power_beam_width',
        units='degrees'),
    'Cr': Meta(
        long_name='radar_constant'),
    'DualPol': Meta(
        long_name='dual_polarisation',
        comment='0=single polarisation radar, 1=dual polarisation radar in LDR mode, '
                '2=dual polarisation radar in STSR mode'),
    'CompEna': Meta(
        long_name='compression',
        comment='0=not compressed, 1=compressed, 2=compressed and polarimetric variables saved'),
    'AntiAlias': Meta(
        long_name='anti_alias',
        comment='0=spectra not anti-aliased, 1=spectra have been anti-aliased'),
    'SampDur': Meta(
        long_name='sample_duration',
        units='s'),
    'GPSLat': Meta(
        long_name='gps_latitude',
        units='degrees_north'),
    'GPSLong': Meta(
        long_name='gps_longitude',
        units='degrees_east'),
    'CalInt': Meta(
        long_name='calibration_interval',
        comment='period for automatic zero calibrations in number of samples'),
    'RAltN': Meta(
        long_name='n_range_layers',
        comment='number of radar ranging layers'),
    'TAltN': Meta(
        long_name='n_temperature_layers',),
    'HAltN': Meta(
        long_name='n_humidity_layers'),
    'SequN': Meta(
        long_name='n_chirp_sequences'),
    'RAlts': Meta(
        long_name='range_layers'),
    'TAlts': Meta(
        long_name='temperature_layers'),
    'HAlts': Meta(
        long_name='humidity_layers'),
    'Fr': Meta(
        long_name='range_factors'),
    'SpecN': Meta(
        long_name='n_samples_in_chirp'),
    'RngOffs': Meta(
        long_name='chirp_start_indices'),
    'ChirpReps': Meta(
        long_name='n_chirps_in_sequence'),
    'SeqIntTime': Meta(
        long_name='sequence_integration_time'),
    'dR': Meta(
        long_name='range_resolution',
        units='m',
        comment='chirp sequence range resolution'),
    'MaxVel': Meta(
        long_name='max_doppler_velocity',
        units='m/s',
        comment='max. Doppler velocity for each chirp sequence (unambiguous)'),
    'ChanBW': Meta(
        long_name='bandwidth',
        units='Hz',
        comment='bandwidth of individual radar channel in the sequence'),
    'ChirpLowIF': Meta(
        long_name='lowest_IF_frequency',
        units='Hz'),
    'ChirpHighIF': Meta(
        long_name='highest_IF_frequency',
        units='Hz'),
    'RangeMin': Meta(
        long_name='minimum_altitude',
        units='m',
        comment='minimum altitude (range) of the sequence'),
    'RangeMax': Meta(
        long_name='maximum_altitude',
        units='m',
        comment='maximum altitude (range) of the sequence)'),
    'ChirpFFTSize': Meta(
        long_name='fft_size',
        comment='Must be power of 2'),
    'ChirpInvSamples': Meta(
        long_name='n_invalid_samples',
        comment='number of invalid samples at beginning of chirp'),
    'ChirpCenterFr': Meta(
        long_name='chirp_center_frequency',
        units='MHz'),
    'ChirpBWFr': Meta(
        long_name='chirp_bandwidth',
        units='MHz'),
    'FFTStartInd': Meta(
        long_name='fft_start_index'),
    'FFTStopInd': Meta(
        long_name='fft_stop_index'),
    'ChirpFFTNo': Meta(
        long_name='n_chirp_fft',
        comment='number of FFT range layers in one chirp (usually = 1)'),
    'SampRate': Meta(
        long_name='adc_sampling_rate',
        units='Hz'),
    'MaxRange': Meta(
        long_name='maximum_range',
        units='m',
        comment='maximum unambiguous range'),
    'SupPowLev': Meta(
        long_name='power_leveling_flag',
        comment='flag indicating the use of power levelling (0=yes, 1=no)'),
    'SpkFilEna': Meta(
        long_name='spike_filter_flag',
        comment='flag indicating the use of spike/plankton filter (1=yes, 0=no)'),
    'PhaseCorr': Meta(
        long_name='phase_correction_flag',
        comment='flag indicating the use of phase correction (1=yes, 0=no)'),
    'RelPowCorr': Meta(
        long_name='relative_power_correction_flag',
        comment='flag indicating the use of relative power correction (1=yes, 0=no)'),
    'FFTWindow': Meta(
        long_name='fft_window',
        comment='FFT window in use: 0=square, 1=parzen, 2=blackman, 3=welch, 4=slepian2, 5=slepian3'),
    'FFTInputRng': Meta(
        long_name='adc_voltage_range',
        comment='ADC input voltage range (+/-)',
        units='mV'),
    'NoiseFilt': Meta(
        long_name='noise_filter_threshold',
        comment='noise filter threshold factor (multiple of STD in Doppler spectra)'),
    'Time': Meta(
        long_name='time',
        units='s'),
    'MSec': Meta(
        long_name='time_ms',
        units='ms'),
    'QF': Meta(
        long_name='quality_flag',
        comment='Bit 1=ADC saturation, Bit 2=spectral width too high, Bit 3=no transm. power leveling'),
    'RR': Meta(
        long_name='rain_rate',
        units='mm/h'),
    'RelHum': Meta(
        long_name='relative_humidity',
        units='%'),
    'EnvTemp': Meta(
        long_name='temperature',
        units='K',
        comment='environment temperature'),
    'BaroP': Meta(
        long_name='pressure',
        units='hPa',
        comment='barometric pressure'),
    'WS': Meta(
        long_name='wind_speed',
        units='km/h',),
    'WD': Meta(
        long_name='wind_direction',
        units='degrees'),
    'DDVolt': Meta(
        long_name='voltage',
        units='V',
        comment='direct detection channel voltage'),
    'DDTb': Meta(
        long_name='brightness_temperature',
        units='K'),
    'TransPow': Meta(
        long_name='transmitter_power',
        units='W'),
    'TransT': Meta(
        long_name='transmitter_temperature',
        units='K'),
    'RecT': Meta(
        long_name='receiver_temperature',
        units='K'),
    'PCT': Meta(
        long_name='pc_temperature',
        units='K'),
    'LWP': Meta(
        long_name='liquid_water_path',
        units='g/m2'),
    'Elev': Meta(
        long_name='elevation',
        units='degrees'),
    'Azi': Meta(
        long_name='azimuth',
        units='degrees'),
    'Status': Meta(
        long_name='status_flag',
        comment='mitigation status flags: 0/1=heater switch (ON/OFF) 0/10=blower switch (ON/OFF)'),
    'TotSpec': Meta(
        long_name='doppler_spectrum',
        comment='linear Ze'),
    'HSpec': Meta(
        long_name='doppler_spectrum_h',
        comment='horizontal polarisation, linear Ze'),
    'ReVHSpec': Meta(
        long_name='covariance_spectrum_re',
        comment='real part linear Ze'),
    'ImVHSpec': Meta(
        long_name='covariance_spectrum_im',
        comment='imaginary part linear Ze'),
    'RefRat': Meta(
        long_name='differential_reflectivity',
        units='dB'),
    'DiffPh': Meta(
        long_name='differential_phase',
        units='rad'),
    'SLDR': Meta(
        long_name='ldr_slanted',
        units='dB'),
    'CorrCoeff': Meta(
        long_name='correlation_coefficient',),
    'SCorrCoeff': Meta(
        long_name='correlation_coefficient_slanted',),
    'KDP': Meta(
        long_name='differential_phase_shift',
        units='rad/km'),
    'DiffAtt': Meta(
        long_name='differential_attenuation',
        units='db/km'),
    'TotNoisePow': Meta(
        long_name='integrated_noise',
        comment='integrated Doppler spectrum noise power'),
    'HNoisePow': Meta(
        long_name='integrated_noise_h',
        comment='integrated Doppler spectrum noise power in h-pol'),
    'AliasMsk': Meta(
        long_name='anti_alias_correction',
        comment='mask indicating if anti-aliasing has been applied (=1) or not (=0)'),
    'MinVel': Meta(
        long_name='minimum_velocity',
        units='m/s'),
    'PowIF': Meta(
        long_name='IF_power',
        comment='IF power at ADC',
        units='uW'),
    'Ze': Meta(
        long_name='reflectivity',
        comment='linear reflectivity in Ze units for vertical polarisation'),
    'MeanVel': Meta(
        long_name='velocity',
        units='m/s',
        comment='mean velocity for vertical polarisation'),
    'SpecWidth': Meta(
        long_name='width',
        units='m/s',
        comment='spectral width for vertical polarisation'),
    'Skewn': Meta(
        long_name='skewness',
        comment='spectral skewness for vertical polarisation'),
    'Kurt': Meta(
        long_name='kurtosis',),
}
