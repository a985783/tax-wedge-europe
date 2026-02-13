# Submission Checklist (Target: Restat / AEJ:Policy)

## 📄 Main Manuscript
- [x] **Title Page**: Title, Abstract (max 100 words), JEL Codes, Keywords, Author Affiliations (blinded for review?). *Note: Restat is double-blind.* -> **Action: Ensure `paper.tex` has no author names.**
- [x] **Format**: Double-spaced (set to 1.5 currently, check journal specific), 12pt font, wide margins.
- [x] **Abstract**: Concise, focusing on the "Symmetric Pass-through" finding and "Tax Wedge" methodology.
- [x] **References**: Ensure all citations in `paper.tex` are in `references.bib` and formatted correctly (BibTeX generated).

## 📊 Figures & Tables
- [x] **Legibility**: All text in figures must be readable when printed in black & white.
- [x] **Notes**: Each table/figure must have a self-contained note explaining the sample, dependent variable, and significance levels.
- [x] **Placement**: Floats are currently embedded in text. Some journals require them at the end. *Restat allows embedded for initial submission.*

## 📦 Supplementary Materials
- [x] **Online Appendix**:
    - [x] Data Construction Details
    - [x] Robustness Checks (Clustering, Windows)
    - [x] Validation Audit Summary
- [x] **Replication Package**:
    - [x] `data/` (Sample data or instructions to access Eurostat)
    - [x] `src/` (Python scripts for cleaning and analysis)
    - [x] `README.md` (Instructions to reproduce results)

## ✉️ Submission Portal Items
- [ ] **Cover Letter**: See `cover_letter.md`.
- [ ] **Data Availability Statement**: "The data used in this paper are publicly available from Eurostat (PRC_HICP datasets). Code to replicate all findings is provided in the supplementary material."
- [ ] **Disclosure Statement**: Confirm no conflict of interest / funding sources.
- [ ] **Reviewer Suggestions**:
    - Youssef Benzarti (UCSB) - *Cite him heavily, fair reviewer.*
    - Dora Benedek (IMF) - *Expert in VAT pass-through.*
    - Erzo F.P. Luttmer (Dartmouth) - *Public finance expert.*

## 🚨 Final Sanity Check
- [ ] **Spell Check**: Run a final spell check on PDF.
- [ ] **Link Check**: Click all internal links (Figures/Tables/Citations) in the PDF to ensure they work.
- [ ] **Blinding**: Verify no self-identifying footnotes (e.g., "In our previous paper...").
