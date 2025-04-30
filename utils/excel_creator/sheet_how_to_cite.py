# Method to add extra sheet for the how to cite info
def add_citation_sheet(workbook):
    ws = workbook.create_sheet(title='How to Cite')
    lines = [
        '5. How to Cite',
        '• NOMAD: How to cite NOMAD (link to https://nomad-lab.eu/nomad-lab/cite.html)',
        '• Code/Voila Notebooks: How to cite code from nomad-hzb-se OASIS (link to https://github.com/nomad-hzb/nomad-hysprint)',
        '',
        'If you use code or Voila notebooks for scientific analysis from the nomad-hzb repository, please cite as follows (unless the journal that you wish to publish requires a different format):',
        '',
        'Citation Fields:',
        "Title: NOMAD Hysprint: NOMAD's schema for HZB perovskite research",
        'Author(s): NOMAD-HZB contributors',
        'Date of Publication: [Year of use or latest commit]',
        'Publisher: GitHub',
        'DOI or URL: https://github.com/nomad-hzb/nomad-hysprint',
        'Version or Date Downloaded: [Version, release tag, or date you accessed/downloaded the code]',
        '• (Optional) Commit Hash: [Specific commit hash, for reproducibility]',
        '• License: Code: Apache-2.0; Voila Notebooks: CC BY 4.0',
        '',
        'Example Citation:',
        # "NOMAD Hysprint: NOMAD's schema for HZB perovskite research. NOMAD-HZB contributors. 2025. GitHub. https://github.com/nomad-hzb/nomad-hysprint. Accessed: 2025-04-25. Version: main branch, commit [commit-hash]. Code licensed under Apache-2.0; Voila notebooks licensed under CC BY 4.0.",
    ]
    for i, line in enumerate(lines, 1):
        ws.cell(row=i, column=1, value=line)
    # Add hyperlinks for NOMAD and GitHub
    ws.cell(row=2, column=1).hyperlink = 'https://nomad-lab.eu/nomad-lab/cite.html'
    ws.cell(row=3, column=1).hyperlink = 'https://github.com/nomad-hzb/nomad-hysprint'
    ws.column_dimensions['A'].width = 120
