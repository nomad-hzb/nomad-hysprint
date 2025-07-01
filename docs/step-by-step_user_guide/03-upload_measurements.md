# Uploading Measurement Data

In addition to synthesis and process data, the Hysprint plugin supports uploading measurement data and linking it to your samples and processes.
> Note: Measurements get connected to samples via their sample ID and therefore you need to have uploaded or created already a sample.
---

## Supported Measurement File Types
- JV
- EQE
- MPPT
- XRD
- XPS
- SEM
- PL


Unsupported formats can be uploaded within the sample upload for the experiment, but will be available only as raw files.

---

## How to Upload Measurement Files

### Option 1 (Recommended Workflow): Voila Notebook
- Please follow the visual guide for [adding your measurement files](https://scribehow.com/viewer/How_to_Work_on_the_HZB_Nomad_Oasis__bRbhHOaCR2S3dBIeQLYw8A?referrer=documents)

### Option 2: Naming the File Yourself

If you created an experimental plan and samples with IDs (see: [create_experimental_plan.md](../advanced_user_guide/manual_creation_workflow/create_experimental_plan.md)), you can then use these IDs to annotate your measurements.

**File naming convention:**
`<id>.<notes>.<technique>.<file_type>` (note the periods in the name!)

Example:
`HZB_MiGo_20231109_BatchX_3_0.after_3_days.jv.txt`

- The first part is the ID, then you can put some individual note, then the type (e.g. `eqe`, `jv`, `pl`, `hy`, `spv`, `uvvis`, `sem`, `xrd`, `pli`), and finally the file type.

If you drag and drop these files (multiple at once possible) in your upload:

![grafik](https://github.com/RoteKekse/nomad-baseclasses/assets/36420750/495fdb2e-4dad-42f0-853c-fef3a6a4cd03)

It automatically creates the respective NOMAD entry (e.g. `HySprint_JVmeasurement`), links it to the corresponding sample, and puts the note in the comment.

<iframe src="https://scribehow.com/embed/How_to_Work_on_the_HZB_Nomad_Oasis__bRbhHOaCR2S3dBIeQLYw8A" width="100%" height="800" allow="fullscreen" style="aspect-ratio: 1 / 1; border: 0; min-height: 480px"></iframe>

