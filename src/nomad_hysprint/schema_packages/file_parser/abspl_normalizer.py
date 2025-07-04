def parse_abspl_data(data_file, archive, logger):
    """Parses the AbsPL data file and returns extracted settings and spectral arrays."""
    with archive.m_context.raw_file(data_file, mode='rb') as f:
        raw_bytes = f.read()
    text = raw_bytes.decode('cp1252', errors='replace')
    lines = text.splitlines()
    logger.debug('Read data file lines', file=data_file, total_lines=len(lines))

    settings_vals, result_vals, data_start_idx = parse_header(lines, logger)
    wavelengths, lum_flux, raw_counts, dark_counts = parse_numeric_data(lines, data_start_idx, logger)

    return settings_vals, result_vals, wavelengths, lum_flux, raw_counts, dark_counts


def parse_header(lines, logger):
    header_map_settings = {
        'Laser intensity (suns)': 'laser_intensity_suns',
        'Bias Voltage (V)': 'bias_voltage',
        'SMU current density (mA/cm2)': 'smu_current_density',
        'Integration Time (ms)': 'integration_time',
        'Delay time (s)': 'delay_time',
        'EQE @ laser wavelength': 'eqe_laser_wavelength',
        'Laser spot size (cm²)': 'laser_spot_size',
        'Laser spot size (cm�)': 'laser_spot_size',
        'Subcell area (cm²)': 'subcell_area',
        'Subcell area (cm�)': 'subcell_area',
        'Subcell': 'subcell_description',
    }
    header_map_result = {
        'LuQY (%)': 'luminescence_quantum_yield',
        'QFLS (eV)': 'quasi_fermi_level_splitting',
        'iVoc (V) HET': 'quasi_fermi_level_splitting',
        'iVoc (V)': 'i_voc',
        'Bandgap (eV)': 'bandgap',
        'Jsc (mA/cm2)': 'derived_jsc',
    }

    settings_vals = {}
    result_vals = {}
    header_done = False
    data_start_idx = None

    for idx, line in enumerate(lines):
        line_stripped = line.strip()
        if line_stripped.startswith('---'):
            data_start_idx = idx + 2  # skip dashed line and header line
            header_done = True
            break
        if '\t' in line:
            parts = line.split('\t', 1)
            if len(parts) == 2:  # noqa: PLR2004
                key = parts[0].strip()
                val_str = parts[1].strip()
                if key in header_map_settings:
                    if key == 'Subcell':
                        settings_vals[header_map_settings[key]] = val_str
                    else:
                        try:
                            settings_vals[header_map_settings[key]] = float(val_str)
                        except ValueError:
                            logger.debug(
                                'Could not convert header to float',
                                key=key,
                                val=val_str,
                            )
                elif key in header_map_result:
                    try:
                        result_vals[header_map_result[key]] = float(val_str)
                    except ValueError:
                        logger.debug('Could not convert result to float', key=key, val=val_str)

    logger.debug('Header parsed', header_done=header_done, data_start=data_start_idx)
    return settings_vals, result_vals, data_start_idx


def parse_numeric_data(lines, data_start_idx, logger):
    wavelengths = []
    lum_flux = []
    raw_counts = []
    dark_counts = []

    if data_start_idx is not None and data_start_idx < len(lines):
        MIN_PARTS_COUNT = 3
        for line in lines[data_start_idx:]:
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) < MIN_PARTS_COUNT:
                continue
            try:
                wavelengths.append(float(parts[0]))
                lum_flux.append(float(parts[1]))
                raw_counts.append(float(parts[2]))
                if len(parts) == 3:
                    continue  # Some files may not have dark counts
                dark_counts.append(float(parts[3]))
            except ValueError:
                logger.debug('Could not parse numeric row', row=line)

    logger.debug(
        'Parsed numeric data',
        w_count=len(wavelengths),
        lf_count=len(lum_flux),
        rc_count=len(raw_counts),
        dc_count=len(dark_counts),
    )

    return wavelengths, lum_flux, raw_counts, dark_counts
