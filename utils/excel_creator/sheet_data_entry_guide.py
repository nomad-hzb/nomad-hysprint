# Method for adding a sheet with information on how to fill up the columns
def add_guide_sheet(workbook):
    guide_ws = workbook.create_sheet(title='Data Entry Guide')
    row = 1

    # 1. Introduction (multi-line text)
    intro_lines = [
        'Perovskite Solar Cell Fabrication Sequence',
        'Data Entry Guide',
        '',
        '1. Introduction',
        'This guide provides instructions for filling out the spreadsheet that tracks the fabrication sequence of perovskite solar cells, supporting automated data upload to NOMAD.',
        '• Note: This guide is a reference. For specific questions or custom spreadsheet requests, please contact a Data Steward.',
        '• Customization: Each scientist may follow different fabrication steps. Data Stewards can provide a tailored spreadsheet for your workflow.',
        '• Coverage: Most Hysprint and IRIS lab processes are included. If you need to track additional information, contact a Data Steward.',
        '• Important: Do not add columns to the spreadsheet, as they will not be parsed.',
        '',
        'Example Fabrication Sequence:',
        '• Cleaning: 4 steps, UV-Ozone (ITO substrates)',
        '• Spin Coating: 1 solvent, 1 solute, 1 step (SAM)',
        '• Spin Coating: 2 solvents, 5 solutes, 2 steps, with antisolvent (Perovskite)',
        '• Evaporation: C60, BCP, Copper',
        '',
        '2. Detailed Field Descriptions',
        'Upload Name: Choose a descriptive upload name (e.g., project name + batch).',
        '',
    ]
    for line in intro_lines:
        guide_ws.cell(row=row, column=1, value=line)
        row += 1

    # Helper to write a table
    def write_table(ws, start_row, title, table_data):
        ws.cell(row=start_row, column=1, value=title)
        start_row += 1
        headers = ['Field Name', 'Description', 'Data Format', 'Units', 'Example']
        for col, header in enumerate(headers, 1):
            ws.cell(row=start_row, column=col, value=header)
        for r, entry in enumerate(table_data, start_row + 1):
            for c, val in enumerate(entry, 1):
                ws.cell(row=r, column=c, value=val)
        return start_row + len(table_data) + 2  # leave a blank row after table

    # Experiment Info Table
    experiment_info = [
        ['Date', 'Date of experiment', 'DD-MM-YYYY', '', '26-02-2025'],
        ['Project_Name', 'Scientist initials/project name', 'Text', '', 'FiNa'],
        ['Batch', 'General experiment batch number', 'Number', '', '1'],
        ['Subbatch', 'Subset for variations', 'Number', '', '2'],
        ['Sample', 'Sample serial number', 'Number', '', '1'],
        ['Nomad ID', 'Auto-generated sample ID', 'Alphanumeric', '', ''],
        ['Variation', 'Subbatch variation', 'Alphanumeric', '', '1000 rpm'],
        ['Sample Dimension', 'Sample size', 'Number', 'cm', '1 cm x 1 cm'],
        ['Sample area', 'Active area (e.g., ITO/Cu overlap)', 'Number', 'cm²', '0.16'],
        ['Number of pixels', 'Number of pixels', 'Number', '', '6'],
        ['Pixel area', 'Area per pixel', 'Number', 'cm²', '0.16'],
        ['Substrate Material', 'Substrate material', 'Alphanumeric', '', 'Soda Lime Glass'],
        ['Substrate Conductive Layer', 'Conductive layer material', 'Alphanumeric', '', 'ITO'],
        ['Number of Junctions', 'Number of junctions', 'Number', '', '1'],
        ['Notes', 'Additional notes or methods', 'Alphanumeric', '', ''],
    ]
    row = write_table(guide_ws, row, 'Experiment Info', experiment_info)

    # Step 1: Cleaning (UV-Ozone)
    cleaning = [
        ['Solvent', 'Cleaning solvent', 'Text', '', 'Hellmanex'],
        ['Time', 'Ultrasonic bath time', 'Number', 's', '31'],
        ['Temperature', 'Bath temperature', 'Number', '°C', '61'],
        ['UV-Ozone Time', 'UV-Ozone duration', 'Number', 's', '900'],
    ]
    row = write_table(guide_ws, row, 'Step 1: Cleaning (UV-Ozone)', cleaning)

    # Step 2: Spin Coating
    spin_coating = [
        [
            'Material Name',
            'Coated material',
            'Alphanumeric',
            '',
            'Cs0.05(MA0.17FA0.83)0.95Pb(I0.83Br0.17)3',
        ],
        ['Layer Type', 'Type of layer', 'Text', '', 'Absorber'],
        ['Tool/GB name', 'Tool used', 'Text', '', 'HZB-HySprintBox'],
        ['Solvent 1 name', 'First solvent', 'Text', '', 'DMF'],
        ['Solvent 1 volume', 'Volume of solvent 1', 'Number', 'µL', '10'],
        ['Solvent 1 relative amt.', 'Relative amount of solvent 1', 'Number', '', '1.5'],
        ['Solute 1 name', 'First solute', 'Text', '', 'PbI2'],
        ['Solute 1 Concentration', 'Concentration of solute 1', 'Number', 'mM', '1.42'],
        ['Solution volume', 'Total solution volume', 'Number', 'µL', '100'],
        ['Spin Delay', 'Delay before spinning', 'Number', 's', '0.5'],
        ['Rotation Speed 1', 'First spin speed', 'Number', 'rpm', '3001'],
        ['Rotation time 1', 'First spin time', 'Number', 's', '31'],
        ['Acceleration 1', 'First acceleration', 'Number', 'rpm/s', '1001'],
        ['Rotation speed 2', 'Second spin speed', 'Number', 'rpm', '3002'],
        ['Rotation time 2', 'Second spin time', 'Number', 's', '32'],
        ['Acceleration 2', 'Second acceleration', 'Number', 'rpm/s', '1002'],
        ['Annealing Time', 'Annealing duration', 'Number', 'min', '30'],
        ['Annealing Temperature', 'Annealing temperature', 'Number', '°C', '120'],
        ['Annealing Atmosphere', 'Annealing atmosphere', 'Text', '', 'Nitrogen'],
        ['Notes', 'Additional notes', 'Alphanumeric', '', ''],
    ]
    row = write_table(guide_ws, row, 'Step 2: Spin Coating', spin_coating)

    # Step 3: Evaporation
    evaporation = [
        ['Material Name', 'Evaporated material', 'Alphanumeric', '', 'PCBM'],
        ['Layer Type', 'Type of layer', 'Text', '', 'Electron Transport Layer'],
        ['Tool/GB name', 'Tool used', 'Text', '', 'Hysprint Evap'],
        ['Organic', 'Is the layer organic?', 'Boolean', '', 'True'],
        ['Base Pressure', 'Base pressure', 'Number', 'bar', '0.00001'],
        ['Pressure start', 'Start pressure', 'Number', 'bar', '0.00005'],
        ['Pressure end', 'End pressure', 'Number', 'bar', '0.00003'],
        ['Source temp. start', 'Source temp. (start)', 'Number', '°C', '150'],
        ['Source temp. end', 'Source temp. (end)', 'Number', '°C', '150'],
        ['Substrate temperature', 'Substrate temp.', 'Number', '°C', '25'],
        ['Thickness', 'Layer thickness', 'Number', 'nm', '100'],
        ['Rate start', 'Start deposition rate', 'Number', 'Å/s', '0.5'],
        ['Rate target', 'Target deposition rate', 'Number', 'Å/s', '1'],
        ['Tooling factor', 'Tooling factor', 'Number', '', '1.5'],
        ['Notes', 'Additional notes', 'Alphanumeric', '', ''],
    ]
    row = write_table(guide_ws, row, 'Step 3: Evaporation', evaporation)

    # Step 4: ALD (Atomic Layer Deposition)
    ald = [
        ['Material Name', 'Deposited material', 'Alphanumeric', '', 'PCBM'],
        ['Layer Type', 'Type of layer', 'Text', '', 'Electron Transport Layer'],
        ['Tool/GB name', 'Tool used', 'Text', '', 'IRIS ALD'],
        ['Source', 'Precursor source', 'Alphanumeric', '', 'TMA'],
        ['Thickness', 'Film thickness', 'Number', 'nm', '25'],
        ['Temperature', 'Deposition temperature', 'Number', '°C', '150'],
        ['Rate', 'Deposition rate', 'Number', 'Å/s', '0.1'],
        ['Time', 'Deposition time', 'Number', 's', '1800'],
        ['Number of cycles', 'Number of ALD cycles', 'Number', '', '250'],
        ['Precursor 1', 'First precursor', 'Alphanumeric', '', 'TMA'],
        ['Pulse Duration 1', 'Pulse duration (precursor 1)', 'Number', 's', '0.2'],
        ['Manifold temp. 1', 'Manifold temp. (precursor 1)', 'Number', '°C', '80'],
        ['Bottle temp. 1', 'Bottle temp. (precursor 1)', 'Number', '°C', '25'],
        ['Precursor 2', 'Second precursor', 'Alphanumeric', '', 'H2O'],
        ['Pulse Duration 2', 'Pulse duration (precursor 2)', 'Number', 's', '0.1'],
        ['Manifold temp. 2', 'Manifold temp. (precursor 2)', 'Number', '°C', '70'],
    ]
    row = write_table(guide_ws, row, 'Step 4: ALD (Atomic Layer Deposition)', ald)

    # Step 5: Sputtering
    sputtering = [
        ['Material Name', 'Sputtered material', 'Alphanumeric', '', 'TiO2'],
        ['Layer Type', 'Type of layer', 'Text', '', 'Electron Transport Layer'],
        ['Tool/GB name', 'Tool used', 'Text', '', 'Hysprint tool'],
        ['Gas', 'Sputtering gas', 'Text', '', 'Argon'],
        ['Temperature', 'Deposition temperature', 'Number', '°C', '150'],
        ['Pressure', 'Chamber pressure', 'Number', 'mbar', '0.01'],
        ['Deposition Time', 'Deposition time', 'Number', 's', '300'],
        ['Burn in time', 'Burn-in time', 'Number', 's', '60'],
        ['Power', 'Sputtering power', 'Number', 'W', '150'],
        ['Rotation rate', 'Substrate rotation rate', 'Number', 'rpm', '30'],
        ['Thickness', 'Film thickness', 'Number', 'nm', '50'],
        ['Gas flow rate', 'Gas flow rate', 'Number', 'cm³/min', '20'],
        ['Notes', 'Additional notes', 'Alphanumeric', '', ''],
    ]
    row = write_table(guide_ws, row, 'Step 5: Sputtering', sputtering)

    # 3. Data Entry Best Practices
    best_practices = [
        '',
        '3. Data Entry Best Practices',
        '• Decimal Points: Use a dot or comma as appropriate for your Excel/language settings.',
        '• Consistency: Use consistent names for materials, processes, and equipment.',
        '• Completeness: Record as many parameters as possible for each step.',
        '',
        '4. File Naming Conventions',
        '• Standard Format: Each measurement file should be saved as Nomad_id.comment.measurement_type.file_format',
        '  Example: DG_MMB_24_0_C-19.jv.txt',
    ]
    for line in best_practices:
        guide_ws.cell(row=row, column=1, value=line)
        row += 1

    # Add hyperlinks for Voila Dashboard and How-to-guide
    voila_row = row  # current row for Voila Dashboard
    guide_row = row + 1  # next row for How-to-guide

    guide_ws.cell(row=voila_row, column=1, value='• File Uploader Voila Dashboard')
    guide_ws.cell(row=voila_row, column=1).hyperlink = 'https://nomad-hzb-se.de/nomad-oasis/gui/search/voila'
    guide_ws.cell(row=voila_row, column=1).style = 'Hyperlink'

    guide_ws.cell(
        row=guide_row,
        column=1,
        value='The Voila notebook automatically formats measurement files, so manual renaming is not required. We recommend using this method from now on. For how-to-guide, click here',
    )
    guide_ws.cell(
        row=guide_row, column=1
    ).hyperlink = 'https://scribehow.com/viewer/How_to_Work_on_the_HZB_Nomad_Oasis__bRbhHOaCR2S3dBIeQLYw8A'
    guide_ws.cell(row=guide_row, column=1).style = 'Hyperlink'

    # Set column widths for readability
    for col in 'ABCDE':
        guide_ws.column_dimensions[col].width = 28
