from typing import NamedTuple, Optional


class Meta(NamedTuple):
    name: str
    long_name: str
    standard_name: Optional[str] = None
    units: Optional[str] = None
    comment: Optional[str] = None


METADATA = {
    "FileCode": Meta(name="file_code", long_name="File Code"),
    "HeaderLen": Meta(name="header_length", long_name="Header Length", units="bytes"),
    "StartTime": Meta(
        name="start_time", long_name="Start Time", comment="time of first sample in file"
    ),
    "StopTime": Meta(
        name="stop_time", long_name="Stop Time", comment="time of last sample in file"
    ),
    "CGProg": Meta(
        name="program_number", long_name="Program Number", comment="chirp generator program number"
    ),
    "ModelNo": Meta(
        name="model_number",
        long_name="Model Number",
        comment="0=94GHz single polarisation radar, 1=94GHz dual polarisation radar",
    ),
    "ProgName": Meta(name="program_name", long_name="Program Name"),
    "CustName": Meta(name="customer_name", long_name="Customer Name"),
    "Freq": Meta(name="radar_frequency", long_name="Radar Frequency", units="GHz"),
    "AntSep": Meta(
        name="antenna_separation",
        long_name="Antenna Separation",
        units="m",
        comment="separation of both antenna axis (bistatic configuration)",
    ),
    "AntDia": Meta(name="antenna_diameter", long_name="Antenna Diameter", units="m"),
    "AntG": Meta(name="antenna_gain", long_name="Antenna Gain", comment="linear antenna gain"),
    "HPBW": Meta(name="half_power_beam_width", long_name="Half Power Beam Width", units="degrees"),
    "Cr": Meta(name="radar_constant", long_name="Radar Constant"),
    "DualPol": Meta(
        name="dual_polarisation",
        long_name="Dual Polarisation",
        comment="0=single polarisation radar, 1=dual polarisation radar in LDR mode, "
        "2=dual polarisation radar in STSR mode",
    ),
    "CompEna": Meta(
        name="compression",
        long_name="Compression",
        comment="0=not compressed, 1=compressed, 2=compressed and polarimetric variables saved",
    ),
    "AntiAlias": Meta(
        name="anti_alias",
        long_name="Anti Alias",
        comment="0=spectra not anti-aliased, 1=spectra have been anti-aliased",
    ),
    "SampDur": Meta(name="sample_duration", long_name="Sample Duration", units="s"),
    "GPSLat": Meta(name="gps_latitude", long_name="GPS Latitude", units="degrees_north"),
    "GPSLong": Meta(name="gps_longitude", long_name="GPS Longitude", units="degrees_east"),
    "CalInt": Meta(
        name="calibration_interval",
        long_name="Calibration Interval",
        comment="period for automatic zero calibrations in number of samples",
    ),
    "RAltN": Meta(
        name="n_range_layers",
        long_name="Number of Range Layers",
        comment="number of radar ranging layers",
    ),
    "TAltN": Meta(
        name="n_temperature_layers",
        long_name="Number of Temperature Layers",
    ),
    "HAltN": Meta(
        name="n_humidity_layers",
        long_name="Number of Humidity Layers",
    ),
    "SequN": Meta(
        name="n_chirp_sequences",
        long_name="Number of Chirp Sequences",
    ),
    "RAlts": Meta(name="range_layers", long_name="Range Layers"),
    "TAlts": Meta(name="temperature_layers", long_name="Temperature Layers"),
    "HAlts": Meta(name="humidity_layers", long_name="Humidity Layers"),
    "Fr": Meta(name="range_factors", long_name="Range Factors"),
    "SpecN": Meta(
        name="n_samples_in_chirp", long_name="Number of Spectral Samples in Each Chirp Sequence"
    ),
    "RngOffs": Meta(name="chirp_start_indices", long_name="Chirp Sequence Start Indices"),
    "ChirpReps": Meta(
        name="n_chirps_in_sequence", long_name="Number of Averaged Chirps in Each Sequence"
    ),
    "SeqIntTime": Meta(name="integration_time", long_name="Effective Sequence Integration Time"),
    "dR": Meta(name="range_resolution", long_name="Chirp Sequence Range Resolution", units="m"),
    "MaxVel": Meta(name="nyquist_velocity", long_name="Nyquist velocity", units="m/s"),
    "ChanBW": Meta(name="bandwidth", long_name="Bandwidth of Individual Radar Channel", units="Hz"),
    "ChirpLowIF": Meta(name="lowest_IF_frequency", long_name="Lowest IF Frequency", units="Hz"),
    "ChirpHighIF": Meta(name="highest_IF_frequency", long_name="Highest IF Frequency", units="Hz"),
    "RangeMin": Meta(
        name="minimum_altitude",
        long_name="Minimum Altitude",
        units="m",
        comment="minimum altitude (range) of the sequence",
    ),
    "RangeMax": Meta(
        name="maximum_altitude",
        long_name="Maximum Altitude",
        units="m",
        comment="maximum altitude (range) of the sequence)",
    ),
    "ChirpFFTSize": Meta(name="fft_size", long_name="FFT Size", comment="Must be power of 2"),
    "ChirpInvSamples": Meta(
        name="n_invalid_samples",
        long_name="Number of Invalid Samples",
    ),
    "ChirpCenterFr": Meta(
        name="chirp_center_frequency", long_name="Chirp Center Frequency", units="MHz"
    ),
    "ChirpBWFr": Meta(name="chirp_bandwidth", long_name="Chirp Bandwidth", units="MHz"),
    "FFTStartInd": Meta(name="fft_start_index", long_name="FFT Start Index"),
    "FFTStopInd": Meta(name="fft_stop_index", long_name="FFT Stop Index"),
    "ChirpFFTNo": Meta(
        name="n_chirp_fft", long_name="Number of FFT Range Layers in Chirp", comment="Usually = 1"
    ),
    "SampRate": Meta(name="adc_sampling_rate", long_name="ADC Sampling Rate", units="Hz"),
    "MaxRange": Meta(
        name="maximum_range",
        long_name="Maximum Range",
        units="m",
        comment="maximum unambiguous range",
    ),
    "SupPowLev": Meta(
        name="power_leveling_flag",
        long_name="Power Leveling Flag",
        comment="flag indicating the use of power levelling (0=yes, 1=no)",
    ),
    "SpkFilEna": Meta(
        name="spike_filter_flag",
        long_name="Spike Filter Flag",
        comment="flag indicating the use of spike/plankton filter (1=yes, 0=no)",
    ),
    "PhaseCorr": Meta(
        name="phase_correction_flag",
        long_name="Phase Correction Flag",
        comment="flag indicating the use of phase correction (1=yes, 0=no)",
    ),
    "RelPowCorr": Meta(
        name="relative_power_correction_flag",
        long_name="Relative Power Correction Flag",
        comment="flag indicating the use of relative power correction (1=yes, 0=no)",
    ),
    "FFTWindow": Meta(
        name="fft_window",
        long_name="FFT Window",
        comment="FFT window in use: 0=square, 1=parzen, 2=blackman, 3=welch, 4=slepian2, "
        "5=slepian3",
    ),
    "FFTInputRng": Meta(
        name="adc_voltage_range",
        long_name="ADC Voltage Range",
        comment="ADC input voltage range (+/-)",
        units="mV",
    ),
    "NoiseFilt": Meta(
        name="noise_filter_threshold",
        long_name="Noise Filter Threshold",
        comment="noise filter threshold factor (multiple of STD in Doppler spectra)",
    ),
    "Time": Meta(name="time", long_name="Time of Sample", comment="since 1.1.2001", units="s"),
    "MSec": Meta(name="time_ms", long_name="Milliseconds of Sample", units="ms"),
    "QF": Meta(
        name="quality_flag",
        long_name="Quality Flag",
        comment="Bit 1=ADC saturation, Bit 2=spectral width too high, Bit 3=no transm. power "
        "leveling",
    ),
    "RR": Meta(name="rain_rate", long_name="Rain Rate", units="mm/h"),
    "RelHum": Meta(name="relative_humidity", long_name="Relative Humidity", units="%"),
    "EnvTemp": Meta(name="temperature", long_name="Environment Temperature", units="K"),
    "BaroP": Meta(name="pressure", long_name="Barometric Pressure", units="hPa"),
    "WS": Meta(name="wind_speed", long_name="Wind Speed", units="km/h"),
    "WD": Meta(name="wind_direction", long_name="Wind Direction", units="degrees"),
    "DDVolt": Meta(name="voltage", long_name="Direct Detection Channel Voltage", units="V"),
    "DDTb": Meta(name="brightness_temperature", long_name="Brightness Temperature", units="K"),
    "TransPow": Meta(name="transmitter_power", long_name="Transmitter Power", units="W"),
    "TransT": Meta(name="transmitter_temperature", long_name="Transmitter Temperature", units="K"),
    "RecT": Meta(name="receiver_temperature", long_name="Receiver Temperature", units="K"),
    "PCT": Meta(name="pc_temperature", long_name="PC Temperature", units="K"),
    "LWP": Meta(name="lwp", long_name="Liquid Water Path", units="g/m2"),
    "Elev": Meta(name="elevation", long_name="Elevation Angle", units="degrees"),
    "Azi": Meta(name="azimuth", long_name="Azimuth Angle", units="degrees"),
    "Status": Meta(
        name="status_flag",
        long_name="Status Flag",
        comment="mitigation status flags: 0/1=heater switch (ON/OFF) 0/10=blower switch (ON/OFF)",
    ),
    "TotSpec": Meta(name="doppler_spectrum", long_name="Doppler Spectrum", comment="linear Ze"),
    "HSpec": Meta(
        name="doppler_spectrum_h",
        long_name="Doppler Spectrum H",
        comment="horizontal polarisation, linear Ze",
    ),
    "ReVHSpec": Meta(
        name="covariance_spectrum_re",
        long_name="Covariance Spectrum Re",
        comment="real part, linear Ze",
    ),
    "LDRSpec": Meta(
        name="LDR spectrum", long_name="linear depolarisation ratio Doppler spectra", units="dB"
    ),
    "ImVHSpec": Meta(
        name="covariance_spectrum_im",
        long_name="Covariance Spectrum Im",
        comment="imaginary part, linear Ze",
    ),
    "RefRat": Meta(name="ldr", long_name="Linear Depolarisation Ratio", units="dB"),
    "DiffPh": Meta(name="differential_phase", long_name="Differential Phase", units="rad"),
    "SLDR": Meta(name="ldr_slanted", long_name="LDR Slanted", units="dB"),
    "CorrCoeff": Meta(name="correlation_coefficient", long_name="Correlation Coefficient"),
    "SCorrCoeff": Meta(
        name="correlation_coefficient_slanted",
        long_name="Correlation Coefficient Slanted",
    ),
    "KDP": Meta(
        name="differential_phase_shift", long_name="Differential Phase Shift", units="rad/km"
    ),
    "SLv": Meta(
        name="sensitivity_limit_v",
        long_name="Sensitivity limit for vertical polarization",
        units="linear units",
    ),
    "SLh": Meta(
        name="sensitivity_limit_h",
        long_name="Sensitivity limit for horizontal polarization",
        comment="linear units",
    ),
    "DiffAtt": Meta(
        name="differential_attenuation", long_name="Differential Attenuation", units="db/km"
    ),
    "TotNoisePow": Meta(
        name="integrated_noise",
        long_name="Integrated Noise",
        comment="integrated Doppler spectrum noise power",
    ),
    "HNoisePow": Meta(
        name="integrated_noise_h",
        long_name="Integrated Noise H",
        comment="integrated Doppler spectrum noise power in horizontal polarisation",
    ),
    "AliasMsk": Meta(
        name="anti_alias_correction",
        long_name="Anti Alias Correction",
        comment="mask indicating if anti-aliasing has been applied (=1) or not (=0)",
    ),
    "MinVel": Meta(name="minimum_velocity", long_name="Minimum Velocity", units="m/s"),
    "PowIF": Meta(name="IF_power", long_name="Intermediate Frequency Power", units="uW"),
    "Ze": Meta(name="Ze", long_name="Reflectivity", comment="vertical polarisation, linear units"),
    "MeanVel": Meta(
        name="v", long_name="Doppler Velocity", units="m/s", comment="vertical polarisation"
    ),
    "SpecWidth": Meta(
        name="width", long_name="Spectral Width", units="m/s", comment="vertical polarisation"
    ),
    "Skewn": Meta(name="skewness", long_name="Spectral Skewness", comment="vertical polarisation"),
    "Kurt": Meta(name="kurtosis", long_name="Spectral Kurtosis", comment="vertical polarisation"),
    "velocity_vectors": Meta(
        name="velocity_vectors", long_name="Doppler velocity bins", comment="for each chirp"
    ),
    "InstCalPar": Meta(name="Cal_period", units="s", long_name="Calibration period"),
    "SWVersion": Meta(
        name="software_version", long_name="Software version", comment="Multiplied by 100"
    ),
}
