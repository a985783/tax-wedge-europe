# Overleaf Submission Instructions

1.  **Upload**: Upload all files in this folder (including the `figures` and `tables` subfolders) to your Overleaf project.
2.  **Compiler**: Set the compiler to **pdfLaTeX** (Menu -> Compiler).
3.  **Main File**: Ensure `paper.tex` is set as the main document.
4.  **Dependencies**: The project uses standard packages (`natbib`, `graphicx`, etc.) which are pre-installed on Overleaf.

## Files
- `paper.tex`: The main source code.
- `references.bib`: Bibliography file.
- `figures/`: Folder containing all plots.
- `tables/`: Folder containing regression tables.

## Troubleshooting
- If tables look weird, check `tables/*.tex`. Some might be raw text outputs from Python; you may need to wrap them in `\begin{tabular}...\end{tabular}` if they aren't already formatted.
