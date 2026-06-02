# fisier folosit pentru croparea fisierelor foarte mari FITS. 
# Interfata web are o limita de 500 MB pentru afisarea rezultatelor. Cu toate astea, imaginile mari vor rula foarte lent
# De asemenea, pe imagini mari exista riscul ca web browser-ul sa nu reziste si sa dea crush. Aceasta nu mai este o limitare a interfatei, ci a browserului
from astropy.io import fits
import os

cale_originala_fisier_mare = "fits_files/palomar1.fits"
cale_crop = "fits_files/palomar1_2000.fits"
DIM_CROP = 2000

with fits.open(cale_originala_fisier_mare) as hdul:
    data = hdul[0].data
    H, W = data.shape
    print(f"Imaginea originala: {H} x {W} pixeli")
    ci, cj = H // 2, W // 2
    jumatate = DIM_CROP // 2
    data_crop = data[ci-jumatate:ci+jumatate, cj-jumatate:cj+jumatate]
    print(f"Imaginea crop-ata: {data_crop.shape}")
    hdu_nou = fits.PrimaryHDU(data=data_crop, header=hdul[0].header)
    hdu_nou.writeto(cale_crop, overwrite=True)
    dim_mb = os.path.getsize(cale_crop) / (1024*1024)
    print(f"Salvat: {cale_crop} ({dim_mb:.1f} MB)")