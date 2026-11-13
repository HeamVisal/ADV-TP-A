# CER Lab — Group 9 demo

A browser-only Character Error Rate demo for the classroom presentation.
No API keys, server, package installation, build step, or GPU is needed.

## Open the demo

Open `index.html` directly in your browser. All assets are local, so the
calculator also works offline. The source links need internet access.

You can also serve this folder locally:

```bash
python -m http.server 8000 --directory Course/12A-Nov26-Activity/cer-demo
```

Then visit <http://localhost:8000>.

## What visitors can do

- Compare a reference and prediction, with up to 2,000 Unicode code points each.
- Update the score, error counts, and alignment automatically while typing or pasting.
- See CER, substitutions, deletions, insertions, and a minimum-edit alignment.
- Try examples including Khmer, CER over 100%, and a one-digit factual error.
- Download their current result as JSON.
- Read a short explanation and follow primary source links.

No input is uploaded. The calculator uses no analytics, external fonts, AI
services, or remote scripts. Example texts are teaching examples, not additional
LLM experiment results. The app does not automatically import notebook results.

## Comparison rules

Matches the notebook's strict default: keep spaces, capitalization, punctuation,
and code points without cleanup or Unicode normalization. Reject empty references;
allow empty predictions. JavaScript `Array.from()` counts code points, unlike
ordinary JavaScript string `.length`, which counts UTF-16 code units.
HTML text boxes use browser-standard line endings. Calculations operate on the
values in the text boxes. A visible symbol can contain several code points.

The algorithm stores two rows of edit costs and a compact traceback grid so it
can display an alignment. Time and traceback memory grow with the product of
the two text lengths. Multiple optimal alignments can have different individual
S/D/I counts but the same total distance and CER. Ties prefer a diagonal step,
then deletion, then insertion.

## Check the calculation

With Node.js installed:

```bash
node --test Course/12A-Nov26-Activity/cer-demo/cer.test.cjs
```

The checks cover the notebook examples, Unicode, empty predictions, invalid inputs,
the length limit, and alignment reconstruction.

## Host for free with GitHub Pages

GitHub Free supports Pages for public repositories. See
[GitHub's explanation](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages).

The prepared repository workflow is `.github/workflows/cer-demo-pages.yml`.
It runs **only when manually started** and uploads **only this demo folder**,
not the course PDFs, notebooks, or report. Publishing requires committing and
pushing the site and workflow, enabling Pages, and starting the workflow.
Creating these files locally does not publish the site.

After reviewing the local demo:

1. Commit and push the demo files and workflow to the chosen GitHub repository.
2. In repository **Settings → Pages → Source**, select **GitHub Actions**.
3. The workflow must exist on the repository's default branch for its manual
   Run workflow button to appear. If working on an activity branch, merge the
   reviewed workflow to the default branch first, then choose the desired branch
   when manually running it. The selected branch must contain the demo folder.
4. In **Actions → Publish CER demo → Run workflow**, choose the reviewed branch.
5. Approve the `github-pages` environment if your repository requires it.
   Environment branch rules must allow the selected branch.
6. Open the site URL shown by the deployment job.

If the course repository should stay private on GitHub Free, use a separate
public repository containing only these website files. Put the website at that
repository's root and change the workflow's artifact path to `.` (or use the
root-folder branch publishing option). Do not change the visibility of the
course repository just to host this demo.

Publishing replaces this repository's existing GitHub Pages site, if it has one.
Choose a separate demo repository if an existing site must be preserved.

Official setup:
[Custom GitHub Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
