# Documentation in English
# Automatic Object Detection in Photometric Images

A Python software module for the automatic detection and measurement of astronomical sources in photometric images used in astrometry.

## Overview

The module implements a complete source-detection pipeline for pre-calibrated FITS images, organized into seven stages:

1. FITS file reading and validation
2. Background estimation and subtraction using `Background2D` with sigma clipping
3. Gaussian filtering to reduce residual noise
4. Point-source detection using the `DAOStarFinder` algorithm
5. Complementary source detection using image segmentation and connected regions
6. Aperture photometry with SNR calculation for detected sources
7. Export of the results to a CSV catalog and generation of annotated visualizations

The module provides two equivalent entry points:

* **Command-line execution** with Matplotlib visualizations
* **Interactive web interface** built with Streamlit and Plotly

## Installation

### Requirements

* Python 3.13 (recommended) or a compatible Python version

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/BogdanCozma14/detectie_fotometrica
cd detectie_fotometrica
pip install -r requirements.txt
```

All library versions are pinned in `requirements.txt` to improve reproducibility.

## Usage

### Command-line interface

Run:

```bash
python main.py
```

The script processes the FITS file specified by the `fisier_ales` variable in `main.py` and displays the processing stages using Matplotlib.

The resulting source catalog is exported as:

```text
catalog_surse.csv
```

### Interactive web interface

Run:

```bash
streamlit run app.py
```

The application opens in a browser at:

```text
http://localhost:8501
```

The Streamlit interface allows users to:

* Select a FITS image from the `fits_files/` directory
* Upload a FITS image from disk
* View the different stages of the processing pipeline
* Interactively inspect results using zoom, pan, and hover functionality
* View the processing results in separate tabs

## Project Structure

```text
detectie_fotometrica/
├── config.py              # Global parameters (FWHM, detection threshold, etc.)
├── preprocesare.py        # FITS reading and background estimation
├── filtrare.py            # Gaussian filtering and optional Fourier filtering
├── detectie.py            # DAOStarFinder and image segmentation
├── rezultate.py           # Aperture photometry and CSV export
├── afisare.py             # Matplotlib visualization for CLI execution
├── main.py                # CLI pipeline orchestrator
├── app.py                 # Streamlit web interface
├── requirements.txt       # Pinned Python dependencies
├── crop_imagine.py        # Utility for extracting regions from large images
├── genereaza_sintetic.py  # Synthetic image generation for quantitative evaluation
├── evalueaza_sintetic.py  # Source matching, completeness, and false-positive evaluation
├── .streamlit/
│   └── config.toml        # Streamlit configuration (upload limit up to 500 MB)
└── fits_files/            # FITS images used for testing
```

## Input Data

The module accepts standard 2D FITS files with either `.fits` or `.fit` extensions.

The input images are expected to contain pre-calibrated photometric data, corrected for:

* Bias
* Dark current
* Flat-field effects

The module automatically validates the input format. Both the file extension and FITS contents are checked when the file is opened. Invalid files are rejected with an explicit error message instead of causing an uncontrolled program failure.

## Test Data

Two types of data were used for testing.

### Real Astronomical Data

**Palomar 1** — a real image obtained using the Advanced Camera for Surveys (ACS) aboard the Hubble Space Telescope as part of the ACS Survey of Galactic Globular Clusters (Sarajedini et al. 2007, GO-10775).

The data are available through the MAST archive.

### Synthetic Data

A synthetic image is generated locally using `genereaza_sintetic.py`.

The generated image contains:

* 1,500 × 1,500 pixels
* 274 synthetic astronomical sources
* 2D Gaussian source profiles
* A noisy background
* Precisely known source positions and brightness values

Because the ground-truth source positions are known, the synthetic dataset can be used for quantitative evaluation of the detection pipeline.

## Results

On the synthetic 1,500 × 1,500 pixel test image containing 274 generated sources, the module correctly detected **254 sources**, with **zero false positives**.

This corresponds to a **92.7% completeness rate**.

The majority of missed sources were below the effective detection threshold configured at approximately 10σ above the background level.

These results provide a quantitative measure of the detection performance rather than relying solely on visual inspection.

## Output

For each source detected by the DAOStarFinder-based pipeline, the exported catalog contains:

* Pixel coordinates `(x, y)`
* Maximum central pixel value
* Raw DAO flux
* Instrumental magnitude
* Aperture sum
* Background-subtracted net flux
* Signal-to-noise ratio (SNR)

The results are exported as a CSV catalog for further analysis.

## Technologies

* **Python**
* **Astropy**
* **Photutils**
* **NumPy**
* **SciPy**
* **Matplotlib**
* **Streamlit**
* **Plotly**
* **Pandas**

## Pipeline

The overall processing flow can be summarized as:

```text
FITS Image
    │
    ▼
Input Validation
    │
    ▼
Background Estimation
    │
    ▼
Background Subtraction
    │
    ▼
Gaussian Filtering
    │
    ▼
Source Detection
 ┌──┴───────────────┐
 ▼                  ▼
DAOStarFinder    Segmentation
 └──┬───────────────┘
    ▼
Source Matching / Analysis
    │
    ▼
Aperture Photometry
    │
    ▼
SNR Calculation
    │
    ▼
CSV Catalog + Visualization
```

## Purpose

The project was developed as a software module for automated astronomical source detection and photometric analysis. Its primary goal is to provide a reproducible and measurable processing pipeline capable of transforming raw astronomical image data into a structured catalog of detected sources and their photometric properties.



# Documentație în română
# Detecția automată a obiectelor în imagini fotometrice

Modul software în Python pentru identificarea automată a surselor 
astronomice în imagini fotometrice obținute în astrometrie.

## Descriere

Modulul implementează un pipeline complet de detecție pentru imagini FITS 
pre-calibrate, organizat în șapte etape:

1. Citirea și validarea fișierelor FITS
2. Estimarea și scăderea background-ului prin metoda Background2D 
   cu sigma clipping
3. Filtrarea gaussiană pentru atenuarea zgomotului rezidual
4. Detecția surselor punctuale prin algoritmul DAOStarFinder
5. Detecția complementară prin segmentare (regiuni conectate)
6. Fotometria de apertură cu calcul SNR pe sursele identificate
7. Exportul rezultatelor în catalog CSV și vizualizarea adnotată

Modulul oferă două puncte de intrare echivalente: rulare prin linia de 
comandă cu vizualizare Matplotlib, sau interfață grafică interactivă 
bazată pe Streamlit cu vizualizări Plotly.

## Instalare

Necesar: Python 3.13 (recomandat) sau compatibil.

```bash
git clone https://github.com/BogdanCozma14/detectie_fotometrica
cd detectie_fotometrica
pip install -r requirements.txt
```

Versiunile bibliotecilor sunt fixate exact în `requirements.txt` pentru 
reproductibilitatea rezultatelor.

## Utilizare
```bash
python main.py
```
### Dacă se rulează fișierul main.py, se vor vedea rezultatele in Matplotlib
### Procesează fișierul setat în variabila `fisier_ales` din `main.py` și 
### afișează cele patru etape ale procesării prin Matplotlib, exportând 
### catalogul în `catalog_surse.csv`.

### Interfață grafică

```bash
streamlit run app.py
```

### Deschide automat aplicația în browser pe `localhost:8501`. Permite 
### selectarea unui fișier salvat din directorul `fits_files/` sau încărcarea 
### unui fișier FITS de pe disc. Rezultatele celor patru etape sunt afișate 
### interactiv, cu zoom, pan și hover, în taburi separate.

## Structura proiectului
```
proiect/
├── config.py              # Parametri globali (FWHM, prag detecție, etc.)
├── preprocesare.py        # Citire FITS + estimare background
├── filtrare.py            # Filtrare gaussiană (și Fourier opțional)
├── detectie.py            # DAOStarFinder + segmentare
├── rezultate.py           # Fotometrie apertură + export CSV
├── afisare.py             # Vizualizare Matplotlib pentru CLI
├── main.py                # Orchestrator CLI
├── app.py                 # Interfață grafică Streamlit
├── requirements.txt       # Dependențe Python fixate exact
├── crop_imagine.py        # Script auxiliar (cutout regiuni din imagini mari)
├── genereaza_sintetic.py  # Script auxiliar (generare imagine sintetică pentru evaluare cantitativă)
├── evalueaza_sintetic.py  # Script auxiliar (matching +  completeness + rata false pozitive)
├── .streamlit/
│   └── config.toml        # Configurare upload până la 500 MB
└── fits_files/            # Director cu imagini FITS pentru testare
```
## Date de intrare

Modulul acceptă fișiere FITS standard 2D (extensii `.fits` sau `.fit`) 
care conțin imagini fotometrice pre-calibrate (corectate de bias, dark 
current și flat-field). Validarea formatului se face automat: extensia 
și conținutul FITS sunt verificate la deschidere, iar fișierele invalide 
sunt respinse controlat cu mesaj de eroare explicit, fără a opri 
programul în mod necontrolat.

## Date de testare

Pentru testare au fost utilizate:

- **Palomar 1** — imagine reală obținută cu instrumentul Advanced Camera 
  for Surveys (ACS) al telescopului spațial Hubble, în cadrul programului 
  ACS Survey of Galactic Globular Clusters (Sarajedini et al. 2007, 
  GO-10775). Disponibilă în arhiva MAST: 
  https://archive.stsci.edu/pub/hlsp/acsggct/
  
- **Imagine sintetică** — generată local prin scriptul auxiliar 
  `genereaza_sintetic.py`, conține 274 de surse cu profile gaussiene 2D 
  pe fond zgomotos, cu poziții și luminozități cunoscute exact pentru 
  evaluarea cantitativă a modulului.

## Rezultate

Pe imaginea sintetică (1500x1500 pixeli, 274 surse generate), modulul 
identifică 254 de surse corect, cu zero false pozitive, rezultând o rată 
de detecție completă (completeness) de 92.7%. Sursele ratate sunt în 
majoritate sub pragul efectiv de detecție configurat la 10σ peste fond.

Catalogul exportat conține pentru fiecare sursă identificată de algoritmul DAO:
- coordonatele pixel (x, y)
- valoarea maximă a pixelului central
- fluxul brut DAO și magnitudinea instrumentală
- suma în apertură și fluxul net (după scăderea fondului local)
- raportul semnal-zgomot (SNR)
