import preprocesare, afisare, filtrare, detectie, rezultate
import matplotlib.pyplot as plt
# pentru verificare
from photutils.datasets import load_star_image
from astropy.io import fits
import os

fisier_ales = "fits_files/ic4499/hlsp_acsggct_hst_acs-wfc_ic4499_f606w_v1_img.fits"
# functia care orchestreaza si ruleaza tot pipeline-ul
def ruleaza_pipeline(fisier_ales):
    fisier = preprocesare.citeste_fisier(fisier_ales)
    if fisier is None:
        print("Preprocesarea s-a oprit.")
    else:
        data_originala = fisier[0].data.copy()
        data_finala, rms_median, rms = preprocesare.estimeaza_si_elimina_background(fisier)
        print(f"Fond mediu: {rms_median:.2f} ADU")
        fisier.close()
        # se aplica filtrarea la data_finala, rezultata dupa eliminarea background-ului
        data_filtrata = filtrare.filtrare_completa(data_finala)
        print(f"Filtrare gaussiana aplicata. forma: {data_filtrata.shape}")
        afisare.afiseaza_imagine_bruta(data_originala)
        afisare.afiseaza_imagine_procesata(data_finala)
        afisare.afiseaza_imagine_filtrata(data_filtrata)

        # se face detectia prin DAOStarFinder din detectie.py pe ultimele date (rezultate din filtrare)
        # surse_seg = detectie.segmentare(data_filtrata, rms)
        surse_dao, surse_noi = detectie.detecteaza(data_filtrata, rms)

        # se afiseaza numarul de surse detectate
        print(f"Total surse detectate: {len(surse_dao)} DAO + {len(surse_noi)} noi")
        
        # verificam surse cu flux negativ, adica false pozitive care trebuie eliminate in rezultate.py
        print(f"surse cu flux negativ: {surse_dao[surse_dao['flux'] < 0]}")
        
        # afisarea imaginii adnotate
        afisare.afiseaza_imagine_adnotata(data_filtrata, surse_dao, surse_noi)

        # exportarea rezultatelor
        rezultate.exporta_csv(data_filtrata, surse_dao, surse_noi)
        plt.show()

# import pandas as pd
# import numpy as np

# df = pd.read_csv("catalog_surse.csv")
# bins = [0, 50000, 100000, 150000, 200000, 250000, 300000]
# labels = ["0-50k", "50-100k", "100-150k", "150-200k", "200-250k", ">250k"]
# counts, _ = np.histogram(df['flux_net'], bins=bins)
# for label, count in zip(labels, counts):
#     print(f"{label}: {count}")

if __name__ == "__main__":
    ruleaza_pipeline(fisier_ales)