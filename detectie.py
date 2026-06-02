import config
from astropy.stats import sigma_clipped_stats
from astropy.table import vstack, Table
from photutils.detection import DAOStarFinder
from photutils.segmentation import make_2dgaussian_kernel, detect_sources, SourceCatalog
from astropy.convolution import convolve
import numpy as np


def detectie_dao(data):
    mean, median, std = sigma_clipped_stats(data, sigma=config.SIGMA_CLIP)
    # afisare a valorilor pentru moment
    '''print(mean, median, std)'''
    daofind = DAOStarFinder(fwhm=config.FWHM, threshold=config.THRESHOLD * std)
    sources = daofind(data-median) # identificarea surselor
    # print(sources)
    return sources

def segmentare(data, rms):
    # definirea thresholdului peste background
    threshold_peste_background = config.THRESHOLD * rms
    kernel = make_2dgaussian_kernel(fwhm=config.FWHM, size=5)
    # convolutie pe date si kernel gaussian
    convolved_data = convolve(data, kernel)
    harta_segmentata = detect_sources(convolved_data, threshold=threshold_peste_background, npixels=config.MIN_PIXELI)
    # print(harta_segmentata)
    # extragerea parametrilor surselor din harta segmentata
    catalog = SourceCatalog(data, harta_segmentata)
    # print(f'Surse detectate prin segmentare: {len(catalog)}')
    return catalog.to_table()

def combina_rezultate(surse_dao, surse_segmentare):
    # daca segmentarea nu a gasit surse, nu exista surse noi
    if surse_segmentare is None or len(surse_segmentare) == 0:
        return surse_dao, []
    if surse_dao is None or len(surse_dao) == 0:
        return surse_dao, list(surse_segmentare)
    
    # coordonatele surselor dao
    x_dao = np.array(surse_dao['xcentroid'])
    y_dao = np.array(surse_dao['ycentroid'])
    # coordonatele din segmentare
    x_seg = np.array(surse_segmentare['xcentroid'])
    y_seg = np.array(surse_segmentare['ycentroid'])

    # se cauta daca exista o sursa din dao la distanta < distanta maxima (DISTANTA_MAX din config)
    surse_noi = []
    for i in range(len(surse_segmentare)):
        distante = np.sqrt((x_dao - x_seg[i])**2 + (y_dao - y_seg[i]) ** 2)
        distanta_minima = np.min(distante)
        if distanta_minima > config.DISTANTA_MAX:
            # s-a gasit sursa din segmentare care nu e deja corespondenta in dao
            surse_noi.append(surse_segmentare[i])
    print(f"Surse noi din segmentare: {len(surse_noi)}")

    return surse_dao, surse_noi
    

def detecteaza(data, rms_map):
    surse_dao = detectie_dao(data)
    surse_segmentare = segmentare(data, rms_map)
    
    # sursele finale
    surse_finale, surse_noi = combina_rezultate(surse_dao, surse_segmentare)
    print(f"Total surse detectate: {len(surse_finale)} + {len(surse_noi)} = {len(surse_finale) + len(surse_noi)}")
    
    if len(surse_noi) > 0:
        # convertesc lista in tabel astropy pentru fisierul rezultate
        tabel_surse_noi = vstack(surse_noi)
        return surse_dao, tabel_surse_noi
    else:
        return surse_dao, Table()