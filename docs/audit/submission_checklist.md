# Submission Checklist

## For SSRN (Immediate)
- [ ] **PDF Generation**: Compile `paper.tex` to PDF. Ensure no compilation errors.
- [ ] **Metadata**:
    - [ ] Title: The Tax Wedge: High-Frequency Identification of Indirect Tax Shocks and Price Rigidity in Europe
    - [ ] Abstract: Copied from `paper.tex`.
    - [ ] Keywords: VAT, Inflation, Tax Pass-through, Price Rigidity.
    - [ ] JEL Codes: E31, H22, H25.
- [ ] **Author Info**: Ensure all author affiliations are current.
- [ ] **Cover Letter**: Use `COVER_LETTER.md` content.

## For Journal Submission (AEJ: Policy / JPubE)
- [ ] **Formatting**:
    - [ ] Check specific margin/font requirements (AEJ usually flexible for initial sub).
    - [ ] Ensure bibliography style matches (Author-Year usually).
- [ ] **Anonymization**:
    - [ ] Create a version of the PDF *without* author names and acknowledgments.
- [ ] **Data Availability**:
    - [ ] Prepare a "Replication Package" (code + readme). You already have `replication/README.md`. Ensure `output/` can be reproduced.
    - [ ] Note: Eurostat data is public, which is a plus.
- [ ] **Online Appendix**:
    - [ ] Move "Robustness" details (like full tables for placebo tests, specific country results) to an Appendix if the main paper exceeds 40 pages.
    - [ ] Include the "Event List" (sample of identified tax shocks) to validate the method.

## Materials to Zip for SSRN
- `paper.tex`
- `references.bib`
- `figures/` (all .png files)
- `tables/` (all .tex files)
- `aeastyle.bst` (if using specific style, otherwise standard bibtex)
