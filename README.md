# Detecția automată a obiectelor în imagini fotometrice

Modul software în Python pentru identificarea automată a surselor 
astronomice în imagini fotometrice obținute în astrometrie. Lucrare de 

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
├── genereaza_sintetic.py  # Script auxiliar (generare imagine
│                            sintetică pentru evaluare cantitativă)
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

Catalogul exportat conține pentru fiecare sursă:
- coordonatele pixel (x, y)
- valoarea maximă a pixelului central
- fluxul brut DAO și magnitudinea instrumentală
- suma în apertură și fluxul net (după scăderea fondului local)
- raportul semnal-zgomot (SNR)
