# Python-draw-of-the-3D-EEM

Draw **3D / 2D-contour EEM** (Excitation-Emission Matrix) fluorescence plots
from plain `.TXT` data files — no Origin required.

---

## What is EEM?

Excitation-Emission Matrix (EEM) spectroscopy is widely used in environmental
science to characterise dissolved organic matter, water quality, and other
fluorescent substances.  A typical EEM dataset records fluorescence intensity
at a grid of excitation × emission wavelength pairs.

---

## Requirements

```
Python ≥ 3.8
matplotlib ≥ 3.5
numpy ≥ 1.21
scipy ≥ 1.7
```

Install all dependencies at once:

```bash
pip install -r requirements.txt
```

---

## TXT File Format

The script accepts tab- **or** comma-separated files with the following layout:

| Ex/Em | 250 | 255 | 260 | … |
|-------|-----|-----|-----|---|
| 200   | 0.0 | 1.2 | 3.4 | … |
| 205   | 0.0 | 2.1 | 5.6 | … |
| …     | …   | …   | …   | … |

* **First row** — emission wavelengths (nm), with an arbitrary label in the
  top-left cell (e.g. `Ex/Em`, `Ex\Em`, or blank).
* **First column** — excitation wavelengths (nm).
* **Remaining cells** — fluorescence intensity values.

A ready-to-use example file is included: [`sample_eem.txt`](sample_eem.txt).

---

## Usage

```
python draw_3d_eem.py [options] <file1.txt> [file2.txt ...]
```

### Options

| Flag | Description |
|------|-------------|
| `-o DIR` / `--output DIR` | Directory to save images (default: current directory) |
| `--cmap CMAP` | Matplotlib colormap (default: `jet`) |
| `--vmax VMAX` | Maximum value for the colour scale (auto-detected if omitted) |
| `--contour` | Draw a 2-D filled-contour plot instead of a 3-D surface |
| `--no-save` | Show the plot interactively instead of saving to disk |
| `--dpi DPI` | Image resolution in DPI (default: 150) |

### Examples

```bash
# 3-D surface plot (default)
python draw_3d_eem.py sample_eem.txt

# 2-D contour plot
python draw_3d_eem.py sample_eem.txt --contour

# Process multiple files and save to a specific folder
python draw_3d_eem.py *.txt -o results/

# Custom colour scale and map
python draw_3d_eem.py sample_eem.txt --cmap hot --vmax 400
```

Output images are named `<basename>_3d.png` or `<basename>_contour.png`.

---

## Example Output

### 3-D Surface Plot
![3D EEM surface plot](https://github.com/user-attachments/assets/58ff9614-ca35-4664-9bb1-8a8a6aa25156)

### 2-D Contour Plot
![2D EEM contour plot](https://github.com/user-attachments/assets/e6dd2e61-1087-4608-8932-f2f40b0f071e)

