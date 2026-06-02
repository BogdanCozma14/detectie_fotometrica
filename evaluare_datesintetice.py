"""
Script auxiliar pentru evaluarea cantitativa a modulului de detectie
pe imaginea sintetica.

Ruleaza pipeline-ul complet pe imaginea sintetica generata anterior si
realizeaza matching-ul intre sursele detectate de DAOStarFinder si
sursele reale din catalogul-adevar. Calculeaza:
- completeness (rata de detectie)
- rata de false pozitive
- distributia detectarii pe amplitudine
"""

import numpy as np
import pandas as pd

import preprocesare, filtrare, detectie, rezultate
import config

TOLERANTA_MATCH = 3.0  # pixeli (= FWHM, conform config)


# rulez pipeline-ul pe imaginea sintetica
print("Rulez pipeline-ul pe imaginea sintetica...")
hdul = preprocesare.citeste_fisier("fits_files/imagine_sintetica.fits")
data_originala = hdul[0].data.copy()
data_finala, rms_median, rms = preprocesare.estimeaza_si_elimina_background(hdul)
hdul.close()
data_filtrata = filtrare.filtrare_completa(data_finala)
surse_dao, surse_noi = detectie.detecteaza(data_filtrata, rms)
tabel_final = rezultate.exporta_csv(data_filtrata, surse_dao, surse_noi,
                                     nume_fisier="catalog_sintetic.csv")

print(f"\nRezultate detectie:")
print(f"  Surse DAO: {len(surse_dao)}")
print(f"  Surse segmentare: {len(surse_noi)}")
print(f"  Surse exportate (flux_net>0): {len(tabel_final)}")
print(f"  RMS fond: {rms_median:.2f} ADU")


# matching cu catalogul-adevar
print(f"\nMatching cu toleranta {TOLERANTA_MATCH} pixeli...")
adevar = pd.read_csv('catalog_adevar.csv')
x_real = adevar['x_real'].values
y_real = adevar['y_real'].values
ampl_reale = adevar['amplitudine_reala'].values

# pentru matching folosesc sursele DAO (catalogul exportat are sursele filtrate)
x_det = np.array(tabel_final['xcentroid'])
y_det = np.array(tabel_final['ycentroid'])

NR_REAL = len(x_real)
NR_DETECTATE = len(x_det)

# pentru fiecare sursa reala, gasesc cea mai apropiata detectie
sursa_reala_detectata = np.zeros(NR_REAL, dtype=bool)
detectie_atribuita = np.zeros(NR_DETECTATE, dtype=bool)
distante_minime = np.full(NR_REAL, np.inf)

for i in range(NR_REAL):
    distante = np.sqrt((x_det - x_real[i])**2 + (y_det - y_real[i])**2)
    idx_min = np.argmin(distante)
    if distante[idx_min] < TOLERANTA_MATCH and not detectie_atribuita[idx_min]:
        sursa_reala_detectata[i] = True
        detectie_atribuita[idx_min] = True
        distante_minime[i] = distante[idx_min]

nr_detectate_corect = np.sum(sursa_reala_detectata)
nr_ratate = NR_REAL - nr_detectate_corect
nr_false_pozitive = NR_DETECTATE - nr_detectate_corect

completeness = 100.0 * nr_detectate_corect / NR_REAL
rata_false = 100.0 * nr_false_pozitive / NR_DETECTATE if NR_DETECTATE > 0 else 0.0

print(f"\n=== REZULTATE EVALUARE ===")
print(f"Surse reale (adevar):          {NR_REAL}")
print(f"Surse detectate (export CSV):  {NR_DETECTATE}")
print(f"Surse detectate corect (TP):   {nr_detectate_corect}")
print(f"Surse ratate (FN):             {nr_ratate}")
print(f"False pozitive (FP):           {nr_false_pozitive}")
print(f"Completeness (TP/real):        {completeness:.1f}%")
print(f"Rata false pozitive (FP/det):  {rata_false:.1f}%")

# distributia detectiei in functie de amplitudine
print(f"\n=== Distributia detectiei pe amplitudine ===")
binuri = [0, 50, 100, 200, 500, 1000, 2500]
for i in range(len(binuri)-1):
    mask = (ampl_reale >= binuri[i]) & (ampl_reale < binuri[i+1])
    nr_total = np.sum(mask)
    nr_det = np.sum(mask & sursa_reala_detectata)
    if nr_total > 0:
        rata = 100.0 * nr_det / nr_total
        print(f"  Amplitudine [{binuri[i]:4d}-{binuri[i+1]:4d}]: {nr_det:3d}/{nr_total:3d} = {rata:5.1f}%")