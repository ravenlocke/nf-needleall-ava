# nf-needleall-ava

Options:
- --infile <infile> : The FASTA file to do all-vs-all needleall on.
- --outdir <directory> : The desired out directory.

optional:
- --threshold <float> : The threshold at which to report identities (default is -1, and therefore will report all).

Example command:

```
nextflow run ravenlocke/nf-needleall-ava --infile <filename> --outdir test --threshold 0.4
```
