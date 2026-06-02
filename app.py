"""
Interfata Streamlit pentru modulul de detectie automata a obiectelor
in imagini fotometrice. Rulare:  streamlit run app.py

Foloseste exact aceleasi module ca main.py (preprocesare, filtrare,
detectie, rezultate, config). Afisarea matplotlib din afisare.py este
inlocuita cu echivalente Plotly interactive (zoom / pan / hover).
"""

from pathlib import Path

import numpy as np
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from astropy.visualization import ZScaleInterval
import time
import preprocesare
import filtrare
import detectie
import rezultate
import config

st.set_page_config(page_title="Detectie obiecte astronomice", layout="wide")

interval = ZScaleInterval()
DIRECTOR_FITS = "fits_files"   # folderul scanat pentru imagini salvate (rulare rapida)


# Afisare cu Plotly (echivalentul logicii din afisare.py)
def _limite_zscale(data):
    """Limite vmin/vmax prin ZScaleInterval, ca in afisare.py (doar pixeli pozitivi)."""
    pozitive = data[data > 0]
    if pozitive.size == 0:
        return float(np.min(data)), float(np.max(data))
    return interval.get_limits(pozitive)


def _stil_imagine(fig):
    # imshow are originea sus-stanga -> inversam axa y; pastram pixeli patrati
    fig.update_yaxes(autorange="reversed", scaleanchor="x", constrain="domain")
    fig.update_xaxes(constrain="domain")
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=620,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")


def figura_originala(data):
    """Echivalent imshow(..., norm=LogNorm()): gama dinamica comprimata logaritmic."""
    z = np.log1p(np.clip(data, 0, None))
    fig = go.Figure(go.Heatmap(
        z=z, colorscale="gray", showscale=False,
        hovertemplate="x=%{x}<br>y=%{y}<br>log(1+val)=%{z:.2f}<extra></extra>"))
    _stil_imagine(fig)
    return fig


def figura_zscale(data):
    """Echivalent imshow(..., vmin, vmax) cu limite ZScale."""
    vmin, vmax = _limite_zscale(data)
    fig = go.Figure(go.Heatmap(
        z=data, zmin=vmin, zmax=vmax, colorscale="gray", showscale=False,
        hovertemplate="x=%{x}<br>y=%{y}<br>val=%{z:.1f}<extra></extra>"))
    _stil_imagine(fig)
    return fig


def figura_adnotata(data, surse_dao, surse_noi, raza=None):
    """Imaginea filtrata cu sursele marcate: rosu = DAO, cyan = segmentare."""
    if raza is None:
        raza = config.RAZA_AFISARE
    vmin, vmax = _limite_zscale(data)
    fig = go.Figure(go.Heatmap(
        z=data, zmin=vmin, zmax=vmax, colorscale="gray", showscale=False,
        hovertemplate="x=%{x}<br>y=%{y}<br>val=%{z:.1f}<extra></extra>"))

    if surse_dao is not None and len(surse_dao) > 0:
        fig.add_trace(go.Scatter(
            x=list(surse_dao["xcentroid"]), y=list(surse_dao["ycentroid"]),
            mode="markers",
            marker=dict(symbol="circle-open", size=2 * raza, color="red", line=dict(width=1)),
            name=f"DAO ({len(surse_dao)})",
            hovertemplate="DAO<br>x=%{x:.1f}<br>y=%{y:.1f}<extra></extra>"))

    if surse_noi is not None and len(surse_noi) > 0:
        fig.add_trace(go.Scatter(
            x=list(surse_noi["xcentroid"]), y=list(surse_noi["ycentroid"]),
            mode="markers",
            marker=dict(symbol="circle-open", size=2 * raza, color="cyan", line=dict(width=1)),
            name=f"Segmentare ({len(surse_noi)})",
            hovertemplate="Segmentare<br>x=%{x:.1f}<br>y=%{y:.1f}<extra></extra>"))

    _stil_imagine(fig)
    fig.update_layout(showlegend=True,
                      legend=dict(bgcolor="rgba(0,0,0,0.5)", font=dict(color="white")))
    return fig


# Citire sursa + pipeline (aceeasi logica din main.ruleaza_pipeline)

def gaseste_fisiere_fits(director):
    p = Path(director)
    if not p.exists():
        return []
    return sorted(str(f) for f in p.rglob("*") if f.suffix.lower() in (".fits", ".fit"))


def citeste_sursa(mod_key, uploaded, cale_preset):
    """Returneaza un HDUList proaspat de fiecare data (upload sau fisier de pe disc)."""
    if mod_key == "upload":
        if uploaded is None:
            return None
        return preprocesare.citeste_din_memorie(uploaded)
    if cale_preset:
        return preprocesare.citeste_fisier(cale_preset)
    return None


def ruleaza_pipeline(hdul):
    data_originala = hdul[0].data.copy()

    rezultat = preprocesare.estimeaza_si_elimina_background(hdul)
    if rezultat[0] is None:        # datele nu sunt 2D
        return None
    data_finala, rms_median, rms = rezultat

    data_filtrata = filtrare.filtrare_completa(data_finala)
    surse_dao, surse_noi = detectie.detecteaza(data_filtrata, rms)

    tabel_final = None
    if surse_dao is not None and len(surse_dao) > 0:
        tabel_final = rezultate.exporta_csv(data_filtrata, surse_dao, surse_noi)

    return {
        "data_originala": data_originala,
        "data_finala": data_finala,
        "data_filtrata": data_filtrata,
        "rms_median": rms_median,
        "surse_dao": surse_dao,
        "surse_noi": surse_noi,
        "tabel_final": tabel_final,
    }


# ----------------------------------------------------------------------
# Componente UI
# ----------------------------------------------------------------------

def afiseaza_validare(hdul):
    data = hdul[0].data
    if data is None:
        st.error("HDU primar nu contine date de imagine (data = None).")
        return False

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Dimensiuni", f"{data.shape}")
    c2.metric("Tip date", str(data.dtype))
    c3.metric("Dimensionalitate", f"{data.ndim}D")
    valid_2d = data.ndim == 2
    c4.metric("Valid pentru pipeline", "Da" if valid_2d else "Nu")

    if not valid_2d:
        st.error(f"Datele au {data.ndim} dimensiuni. Pipeline-ul necesita o imagine 2D.")

    with st.expander("Header FITS (primele chei)"):
        hdr = hdul[0].header
        chei = [k for k in list(hdr.keys())[:20] if k]
        st.write({k: hdr[k] for k in chei})

    return valid_2d


def afiseaza_rezultate(r):
    n_dao = len(r["surse_dao"]) if r["surse_dao"] is not None else 0
    n_noi = len(r["surse_noi"]) if r["surse_noi"] is not None else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Surse DAO", n_dao)
    c2.metric("Surse noi (segmentare)", n_noi)
    c3.metric("Fond RMS median", f"{r['rms_median']:.2f} ADU")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["1. Originala", "2. Background scazut", "3. Filtrata", "4. Adnotata"])
    with tab1:
        st.plotly_chart(figura_originala(r["data_originala"]), use_container_width=True)
        st.caption("Imaginea bruta din fisierul FITS (scalare logaritmica).")
    with tab2:
        st.plotly_chart(figura_zscale(r["data_finala"]), use_container_width=True)
        st.caption("Dupa estimarea si scaderea background-ului (Background2D).")
    with tab3:
        st.plotly_chart(figura_zscale(r["data_filtrata"]), use_container_width=True)
        st.caption("Dupa filtrarea gaussiana.")
    with tab4:
        st.plotly_chart(
            figura_adnotata(r["data_filtrata"], r["surse_dao"], r["surse_noi"]),
            use_container_width=True)
        st.caption("Surse detectate: rosu = DAOStarFinder, cyan = segmentare complementara.")

    st.subheader("Catalog surse")
    if r["tabel_final"] is not None and len(r["tabel_final"]) > 0:
        df = r["tabel_final"].to_pandas()
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Descarca catalog CSV", data=csv,
                           file_name="catalog_surse.csv", mime="text/csv")
    else:
        st.warning("Nu s-au detectat surse cu flux pozitiv pentru export.")


# Aplicatia

st.title("Detecție a obiectelor în imagini fotometrice")
st.caption("Modul de astrometrie — pipeline complet: background, filtrare, detecție, fotometrie.")

st.sidebar.title("Sursa imagine")
mod = st.sidebar.radio("Mod", ["Imagine salvată", "Incarcă fișier"], index=0)

uploaded = None
cale_preset = None
if mod == "Incarcă fișier":
    mod_key = "upload"
    uploaded = st.sidebar.file_uploader("Fișier FITS", type=["fits", "fit"])
else:
    mod_key = "preset"
    fisiere = gaseste_fisiere_fits(DIRECTOR_FITS)
    if fisiere:
        cale_preset = st.sidebar.selectbox("Imagini disponibile", fisiere)
    else:
        st.sidebar.warning(f"Nu am gasit fișiere FITS in '{DIRECTOR_FITS}/'.")

ruleaza = st.sidebar.button("Rulează detecția completă", type="primary")

with st.sidebar.expander("Parametri configurați (config.py)"):
    st.write({
        "SIGMA_CLIP": config.SIGMA_CLIP,
        "BOX_SIZE": config.BOX_SIZE,
        "GAUSSIAN_SIGMA": config.GAUSSIAN_SIGMA,
        "FWHM": config.FWHM,
        "THRESHOLD": config.THRESHOLD,
        "MIN_PIXELI": config.MIN_PIXELI,
        "DISTANTA_MAX": config.DISTANTA_MAX,
    })

# resetam rezultatele daca s-a schimbat sursa selectata
semnatura = f"{mod_key}:{cale_preset or (uploaded.name if uploaded else None)}"
if st.session_state.get("sursa_curenta") != semnatura:
    st.session_state.pop("rezultat", None)
    st.session_state["sursa_curenta"] = semnatura

hdul = citeste_sursa(mod_key, uploaded, cale_preset)

if hdul is None:
    st.info("Selectează o imagine salvată sau încarcă un fișier FITS pentru a incepe.")
else:
    st.subheader("Validare fișier")
    valid = afiseaza_validare(hdul)
    hdul.close()

    if ruleaza and valid:
        with st.spinner("Rulez pipeline-ul: background -> filtrare -> detecție -> fotometrie..."):
            timp_start = time.time()
            hdul2 = citeste_sursa(mod_key, uploaded, cale_preset)
            rezultat = ruleaza_pipeline(hdul2)
            hdul2.close()
            timp_total = time.time() - timp_start
        st.success(f"Pipeline rulat în {timp_total:.2f} secunde")
        if rezultat is None:
            st.error("Pipeline-ul s-a oprit (datele nu sunt 2D).")
        else:
            st.session_state["rezultat"] = rezultat

    if "rezultat" in st.session_state:
        afiseaza_rezultate(st.session_state["rezultat"])