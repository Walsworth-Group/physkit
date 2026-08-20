# report assets

Templates and styles the `report` skill copies into a fresh report directory. All compile with no
package-install approvals: the non-base classes and styles are vendored in this folder.

| file | what it is | status |
|---|---|---|
| `report_skeleton.tex` | REVTeX (`revtex4-2`, APS/PRX) **capstone** skeleton — the full section arc, pre-stubbed, with a `ruledtabular` parameter table. | ✅ compiles clean (reprint + preprint), citations via `apsrev4-2.bst` |
| `draft_article.tex` | plain `article` one-column **draft** template — base packages only. | ✅ compiles anywhere |
| `report-macros.sty` | portable physics macros (units / bra-ket / derivatives), deliberately **siunitx/physics/braket-free**. | ✅ |
| `refs.bib` | bibliography stub. Fill only with `cite-check`-verified entries. | — |

### Vendored REVTeX files (no installs needed — already here)
The REVTeX class is not in a minimal TeX install, so the minimal set needed for `aps,prx` is vendored
directly in this folder. The set was verified by compiling the skeleton and pruning to the files that load:
`revtex4-2.cls`, `aps4-2.rtx`, `aps10pt4-2.rtx`, `aps11pt4-2.rtx`, `aps12pt4-2.rtx` (point-size configs;
10pt = `reprint`, 12pt = `preprint`), `revsymb4-2.sty`, `ltxgrid.sty`, `ltxutil.sty`, and `apsrev4-2.bst`.
`natbib.sty` and `url.sty` are base-install and not vendored. Source: APS author kit / CTAN `revtex`.

## Usage
1. Copy this whole folder into a fresh report dir, outside any working tree.
2. Choose the template: `report_skeleton.tex` for a shareable or capstone physics report; `draft_article.tex`
   for a fast internal draft or when REVTeX is unavailable.
3. Set `\graphicspath` to your figure dir, fill the sections, populate `refs.bib`.
4. Compile: `latexmk -pdf -interaction=nonstopmode -halt-on-error <template>.tex`. Read the `.log` and fix
   until it builds clean: no errors, no `??`, no missing-figure warnings.

## Re-vendoring (only if the set ever needs refreshing)
The REVTeX files are already vendored (see the table above) and verified. To refresh them from a newer
TeX Live, copy the same set from `.../texmf-dist/tex/latex/revtex/` (the `.cls`, `aps4-2.rtx`, the three
`aps*pt4-2.rtx`, `revsymb4-2.sty`, `ltxgrid.sty`, `ltxutil.sty`) plus `apsrev4-2.bst` from
`.../texmf-dist/bibtex/bst/revtex/`, then re-compile the skeleton and prune to the files that load.
Source: APS author kit — <https://journals.aps.org/revtex>, or CTAN <https://ctan.org/pkg/revtex>.

## No local compiler? Overleaf fallback
Zip the self-contained report dir (`.tex`, vendored `.cls`/`.bst`/`.sty`, `refs.bib`, `figs/`) and upload to
Overleaf: full TeX, no installs. The report is not finished until it has either compiled locally or been
packaged this way.
