"""
Script auxiliar pentru generarea unei imagini fotometrice sintetice
folosita la evaluarea cantitativa a modulului de detectie.

Genereaza o imagine 1500x1500 pixeli cu:
- fond zgomot Gaussian aditiv (simuleaza nivelul de fond constant + zgomot Poisson)
- 274 surse stelare cu profile gaussiene 2D
- amplitudini distribuite logaritmic (unele aproape de pragul de detectie, altele clare)
- pozitii aleatorii uniforme in imagine

Salveaza imaginea ca FITS si catalogul-adevar (pozitii, amplitudini, sigma).
"""

import numpy as np
from astropy.io import fits

# parametrii generarii
NR_SURSE = 274
DIM_IMAGINE = 1500
# parametrii fizici
FOND_MEDIU = 200.0       # nivelul mediu al fondului (ADU)
ZGOMOT_FOND = 5.0        # deviatia standard a zgomotului de fond
SIGMA_PSF = 1.5          # latimea profilelor gaussiene (corespunde FWHM~3.5)

# amplitudini distribuite logaritmic intre min si max
AMPL_MIN = 30.0    # surse slabe (aproape de pragul 10*sigma=50)
AMPL_MAX = 2000.0  # surse clare

# margine de evitat (pentru ca sursele sa nu cada la marginea imaginii)
MARGINE = 10

rng = np.random.default_rng(42)

# generez fundalul: nivel constant + zgomot gaussian
imagine = rng.normal(FOND_MEDIU, ZGOMOT_FOND, (DIM_IMAGINE, DIM_IMAGINE)).astype(np.float32)

# generez pozitiile surselor (uniform, evitand marginile)
x_pozitii = rng.uniform(MARGINE, DIM_IMAGINE - MARGINE, NR_SURSE)
y_pozitii = rng.uniform(MARGINE, DIM_IMAGINE - MARGINE, NR_SURSE)

# generez amplitudinile distribuite logaritmic
log_min = np.log10(AMPL_MIN)
log_max = np.log10(AMPL_MAX)
amplitudini = 10 ** rng.uniform(log_min, log_max, NR_SURSE)

# adaug fiecare sursa ca profil gaussian 2D
yy, xx = np.mgrid[0:DIM_IMAGINE, 0:DIM_IMAGINE]
for i in range(NR_SURSE):
    x0 = x_pozitii[i]
    y0 = y_pozitii[i]
    amp = amplitudini[i]
    profil = amp * np.exp(-((xx - x0) ** 2 + (yy - y0) ** 2) / (2 * SIGMA_PSF ** 2))
    imagine += profil.astype(np.float32)

# salvez imaginea FITS
hdu = fits.PrimaryHDU(data=imagine)
hdu.header['OBJECT'] = 'IMAGINE_SINTETICA'
hdu.header['NRSURSE'] = NR_SURSE
hdu.header['BACKGRND'] = FOND_MEDIU
hdu.header['NOISE'] = ZGOMOT_FOND
hdu.writeto('fits_files/imagine_sintetica.fits', overwrite=True)

# salvez catalogul-adevar
catalog_adevar = np.column_stack([
    np.arange(NR_SURSE),
    x_pozitii,
    y_pozitii,
    amplitudini
])
np.savetxt(
    'catalog_adevar.csv',
    catalog_adevar,
    delimiter=',',
    header='id,x_real,y_real,amplitudine_reala',
    fmt=['%d', '%.3f', '%.3f', '%.3f'],
    comments=''
)

print(f"Imagine sintetica generata: {DIM_IMAGINE}x{DIM_IMAGINE} pixeli")
print(f"Surse generate: {NR_SURSE}")
print(f"Amplitudini: min={AMPL_MIN:.1f}, max={AMPL_MAX:.1f} (distribuite logaritmic)")
print(f"Fond: {FOND_MEDIU} ADU, zgomot: {ZGOMOT_FOND} ADU")
print(f"Salvat: fits_files/imagine_sintetica.fits + catalog_adevar.csv")