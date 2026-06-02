import config
import numpy as np
from astropy.convolution import Gaussian2DKernel, convolve

gaussian_sigma = config.GAUSSIAN_SIGMA

def filtrare_gaussiana(data, sigma=None):
    if sigma is None:
        sigma = gaussian_sigma
    # crearea kernelului gaussian cu deviatia standard aleasa
    kernel = Gaussian2DKernel(x_stddev=sigma)
    # aplicarea convolutiei la imaginea cu kernelul gaussian
    data_filtrata = convolve(data, kernel)
    print("fara erori in filtrare.py")
    return data_filtrata


def filtrare_fourier(data, sigma_filtru=None):
    if sigma_filtru is None:
        sigma_filtru = config.FOURIER_SIGMA
    
    rows, cols = data.shape
    crow, ccol = rows // 2, cols // 2
    
    # Windowing pentru reducerea artefactelor de margine
    fereastra_y = np.hanning(rows)
    fereastra_x = np.hanning(cols)
    fereastra_2d = np.outer(fereastra_y, fereastra_x)
    data_windowed = data * fereastra_2d
    
    # 2. Transformata Fourier 2D
    fft_imagine = np.fft.fft2(data_windowed)
    
    # 3. Mutarea frecventei zero in centru
    fft_shift = np.fft.fftshift(fft_imagine)
    
    # 4. Constructia manuala a filtrului gaussian in domeniul frecventelor
    Y, X = np.ogrid[:rows, :cols]
    distanta = np.sqrt((X - ccol)**2 + (Y - crow)**2)
    filtru_gaussian = np.exp(-(distanta**2) / (2 * sigma_filtru**2))
    
    # 5. Aplicarea filtrului prin inmultire in domeniul frecventelor
    fft_filtrat = fft_shift * filtru_gaussian
    
    # 6. Transformata inversa Fourier
    fft_ishift = np.fft.ifftshift(fft_filtrat)
    imagine_filtrata = np.fft.ifft2(fft_ishift).real
    
    # 7. Normalizare pentru pastrarea scalei valorilor originale
    valoare_max_orig = np.max(data)
    valoare_max_filtrat = np.max(imagine_filtrata)
    if valoare_max_filtrat > 0:
        imagine_filtrata = imagine_filtrata * (valoare_max_orig / valoare_max_filtrat)
    
    # logging
    print(f"Filtrare Fourier aplicata. Sigma filtru: {sigma_filtru}")
    print(f"Frecvente eliminate: {100 * (1 - np.sum(filtru_gaussian) / filtru_gaussian.size):.1f}%")
    
    return imagine_filtrata.astype(data.dtype)


def filtrare_completa(data, aplica_fourier=False):
    # filtrarea gaussiana pe datele imaginii
    data_gaussiana = filtrare_gaussiana(data)
    if aplica_fourier:
        return filtrare_fourier(data_gaussiana)
    # filtrarea Fourier aplicata pe datele rezultate dupa filtrarea gaussiana
    return data_gaussiana