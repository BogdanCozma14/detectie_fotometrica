# importarea fisierului de configurare cu variabile globale utilizate
import config
sigma_clip_valoare = config.SIGMA_CLIP
box_size = config.BOX_SIZE
filter_size = config.FILTER_SIZE

# modulele utilizate strict in fisierul preprocesare.py
import os
from astropy.io import fits
from astropy.stats import SigmaClip
from photutils.background import Background2D, MedianBackground
import numpy as np
from io import BytesIO

# functie citire fisier fits
def citeste_fisier(fisier_fits):
    # validarea extensiei fisierului
    _, extensie = os.path.splitext(fisier_fits)
    if extensie.lower() not in ['.fits', '.fit']:
        print(f"Eroare: fisierul '{fisier_fits}' nu este un fisier FITS valid")
        return None
    try:
        file = fits.open(fisier_fits)
        print("Nu sunt erori la citire")
        return file
    except Exception as e:
        print(f"Eroare la citire: {e}")
        return None

def citeste_din_memorie(fisier_incarcat):
    # fisier_incarcat este un UploadedFile din Streamlit
    nume = fisier_incarcat.name
    _, extensie = os.path.splitext(nume)
    if extensie.lower() not in ['.fits', '.fit']:
        print(f"Eroare: fisierul {nume} nu este un fisier FITS valid")
        return None
    try:
        file = fits.open(BytesIO(fisier_incarcat.getvalue()))
        print("Nu sunt erori la citire")
        return file
    except Exception as e:
        print(f"Eroare la citire {e}")
        return None


# functie estimare si eliminare a background-ului
def estimeaza_si_elimina_background(fisier_fits):
    data = fisier_fits[0].data.astype(float)
    # validare a datelor in 2D
    if data.ndim != 2:
        print(f"Eroare: datele nu sunt 2D. Dimensiuni detectate: {data.ndim}")
        return None, None, None
    # se continua cu eliminarea valorilor nule
    data[data == 0] = np.nan
    # sigma clipping
    sigma_clip = SigmaClip(sigma=sigma_clip_valoare)
    background_estimat = MedianBackground()
    # estimeaza backgroundul prin Background2D
    background = Background2D(data, box_size=box_size, filter_size=filter_size, sigma_clip=sigma_clip, bkg_estimator=background_estimat)
    # obtine datele reale scazand backgroundul estimat
    data_finala = data - background.background
    # curatare NaN dupa scadere
    data_finala = np.nan_to_num(data_finala, nan=0.0)
    # se returneaza exclusiv data finala rezultata din fisierul initial si eliminarea zgomotului de background
    return data_finala, background.background_rms_median, background.background_rms