import numpy as np
from photutils.aperture import CircularAperture, CircularAnnulus, aperture_photometry
from astropy.table import Table, vstack
import config
fwhm = config.FWHM


# functie pentru a filtra sursele cu flux negativ inainte de calcule
def filtreaza_surse(surse_dao):
    surse_valide = surse_dao[surse_dao['flux'] > 0]
    return surse_valide

# calculul SNR dar si fotometria de apertura pentru sursele detectate
def calculeaza_snr(date_imagine, surse_dao):
    # extragerea pozitiilor surselor din tabelul DAO
    surse_reale = filtreaza_surse(surse_dao)
    pozitii = np.transpose((surse_reale['xcentroid'], surse_reale['ycentroid']))

    # definire a aperturii circulare pentru masurarea fluxului
    aperturi = CircularAperture(pozitii, r=fwhm)
    tabel_apertura = aperture_photometry(date_imagine, aperturi)
    
    # inelul de background in jurul fiecarei surse
    inel_bkg = CircularAnnulus(pozitii, r_in=fwhm + 20, r_out=fwhm + 50)
    tabel_inel_bkg = aperture_photometry(date_imagine, inel_bkg)
    
    # estimare a background-ului per fiecare pixel din inel_bkg
    # bkg_per_pixel = np.abs(tabel_inel_bkg['aperture_sum'] / inel_bkg.area)
    bkg_per_pixel = np.clip(tabel_inel_bkg['aperture_sum'] / inel_bkg.area, 0, None)
    
    # calcularea fluxului net prin scaderea contributiei backgroud-ului per fiecare pixel care a fost estimat
    nr_pixeli = aperturi.area
    flux_net = tabel_apertura['aperture_sum'] - bkg_per_pixel * nr_pixeli
    
    # calculare SNR (raport semnal-zgomot)
    snr = flux_net / (np.sqrt(nr_pixeli) * np.sqrt(bkg_per_pixel) + 1e-12)
    
    return surse_reale, tabel_apertura['aperture_sum'], flux_net, snr

def exporta_csv(date_imagine, surse_dao, surse_noi, nume_fisier="catalog_surse.csv"):
    # calculul fotometriei si SNR pe sursele filtrate
    surse_reale, apertura, flux_net, snr = calculeaza_snr(date_imagine, surse_dao)
    
    # construirea tabelului final
    tabel_final = Table()
    tabel_final['xcentroid'] = surse_reale['xcentroid']
    tabel_final['ycentroid'] = surse_reale['ycentroid']
    tabel_final['peak'] = surse_reale['peak']
    tabel_final['flux'] = surse_reale['flux']
    tabel_final['mag'] = surse_reale['mag']
    tabel_final['aperture_sum'] = apertura
    tabel_final['flux_net'] = flux_net
    tabel_final['snr'] = snr
    
    # raman doar valorile cu parametri pentru cele cu flux pozitiv 
    tabel_final = tabel_final[tabel_final['flux_net'] > 0]
    
    # export CSV
    tabel_final.write(nume_fisier, format='csv', overwrite=True)
    print(f"Catalog exportat: {nume_fisier} ({len(tabel_final)} surse)")
    
    return tabel_final