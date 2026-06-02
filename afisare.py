import config
import numpy as np
from astropy.visualization import ZScaleInterval
from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt
from photutils.aperture import CircularAperture

figure_size = config.FIGURE_SIZE
interval = ZScaleInterval()
fig, axes = plt.subplots(1,4, figsize=figure_size)

def afiseaza_imagine_bruta(data_originala):
    axes[0].imshow(data_originala, cmap="gray", norm=LogNorm())
    axes[0].set_title("Imaginea originală")
    axes[0].axis("off")


def afiseaza_imagine_procesata(data_finala):
    vmin, vmax = interval.get_limits(data_finala[data_finala > 0])
    axes[1].imshow(data_finala, cmap="gray", vmin=vmin, vmax=vmax)
    axes[1].set_title("După scăderea background-ului")
    axes[1].axis("off")
    plt.tight_layout() # pentru ajustare automata a spatierii pentru titlurile subploturilor pentru a nu fi suprapuneri


def afiseaza_imagine_filtrata(data_filtrata):
    vmin, vmax = interval.get_limits(data_filtrata[data_filtrata > 0])
    axes[2].imshow(data_filtrata, cmap="gray", vmin=vmin, vmax=vmax)
    axes[2].set_title("Dupa filtrare gaussiana")
    axes[2].axis("off")


def afiseaza_imagine_adnotata(imagine_finala, surse_dao, surse_noi, raza_apertura=None):
    if raza_apertura is None:
        raza_apertura = config.RAZA_AFISARE
    vmin, vmax = interval.get_limits(imagine_finala[imagine_finala > 0])
    axes[3].imshow(imagine_finala, cmap="gray", vmin=vmin, vmax=vmax)
    axes[3].set_title(f"Surse detectate: {len(surse_dao)} + {len(surse_noi)}")
    axes[3].axis("off")

    if surse_dao is not None and len(surse_dao) > 0:
        positions_dao = np.transpose((surse_dao['xcentroid'], surse_dao['ycentroid']))
        apertures_dao = CircularAperture(positions_dao, r=raza_apertura)
        apertures_dao.plot(axes=axes[3], color='red', lw=0.5)
    
    if surse_noi is not None and len(surse_noi) > 0: 
        positions_noi = np.transpose((surse_noi['xcentroid'], surse_noi['ycentroid']))
        apertures_noi = CircularAperture(positions_noi, r=raza_apertura)
        apertures_noi.plot(axes=axes[3], color='cyan', lw=0.5)
    plt.tight_layout()