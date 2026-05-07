# ── components/objekt_lista.py ────────────────────────────────────────────────
# Tre delfunktioner som kommer att matcha UX:arnas sidopanel och rekommenderade lista design

import streamlit as st
import pandas as pd
from utils.helpers import load_all, load_visningar, format_sek
from utils.constants import COL_SPARAD

_MANAD = ["", "JAN", "FEB", "MAR", "APR", "MAJ", "JUN",
          "JUL", "AUG", "SEP", "OKT", "NOV", "DEC"]

# Bilder kategoriserade per bostadstyp
# Unsplash-URL:er som fallback, genererad med hjälp av LLMs
_BILDER = {
    "lägenhet": [
        "https://www.bosthlm.se/image/resize/1920/0/images03/192/400128/1347761/highres/12305821.jpg",
        "https://bilder.hemnet.se/images/7359dd1dfa9eaf1cf903b64e828e683bb8379ae1439e0a870fa09575f23ec8e9/5a/1e/5a1edfe1bcdc406b6d7a7e12289f63b6.jpg?quality=70&width=2048&name=web-prod",
        "https://media.brunnbergoforshed.se/2008/02/Brunnberg-Forshed-Arkitektkontor-AB-Ugglan-12.jpg",
        "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=600",
        "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=600",
        "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=600",
    ],
    "hus": [
        "https://files.boneo.se/target_styles/properties/sizex2/1650x1100/3550358-img-MEDCFB29B4EC0B24E5D85B11A8B7D822A5F.jpeg",
        "https://mp1-s3.quedro.com/skm/P3dpZHRoPQ==8721a-5c695-57001-d76be-397fd-30813-ab426-bbba7.jpg",
        "https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=600",
        "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=600",
        "https://images.unsplash.com/photo-1583608205776-bfd35f0d9f83?w=600",
        "https://images.unsplash.com/photo-1598228723793-52759bba239c?w=600",
    ],
    "radhus": [
        "https://images.unsplash.com/photo-1605276374104-dee2a0ed3cd6?w=600",
        "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600",
        "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=600",
        "https://images.unsplash.com/photo-1600047508788-786f3865b4c7?w=600",
    ],
    "tomt": [
        "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=600",
        "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=600",
        "https://images.unsplash.com/photo-1501854140801-50d01698950b?w=600",
    ],
}

_FALLBACK = [
    "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=600",
]


def _bild_url(typ: str, bostad_id: int) -> str:
    """Returnerar en bild-URL matchad till bostadstyp, roterar baserat på id."""
    lista = _BILDER.get(str(typ).lower(), _FALLBACK)
    return lista[(bostad_id * 13) % len(lista)]


def render_sparade() -> None:
    """Detta visar bostäder där sparad == 1 i sidopanelens - Mina sparade-sektion."""
    df = load_all()
    sparade = df[df[COL_SPARAD] == 1].head(3)

    st.markdown("### Mina sparade")

    if sparade.empty:
        st.caption("Du har inte sparat några bostäder ännu.")
        return

    for _, rad in sparade.iterrows():
        with st.container(border=True):
            st.image(_bild_url(rad["typ"], int(rad["id"])), use_container_width=True)
            st.markdown(f"**{format_sek(rad['pris'])}**")
            st.caption(f"{rad['adress']}, {rad['område']}")
            c1, c2, c3 = st.columns(3)
            c1.caption(f"{int(rad['rum'])} rum")
            c2.caption(f"{int(rad['boyta'])} m2")
            c3.caption(str(rad["typ"]).capitalize())


def render_visningar() -> None:
    """Visar kommande visningar från visningar.csv."""
    vis = load_visningar()

    st.markdown("### Kommande visningar")

    if vis.empty:
        st.caption("Inga visningar inbokade.")
        return

    for _, v in vis.iterrows():
        with st.container(border=True):
            col_datum, col_info = st.columns([1, 3])

            with col_datum:
                datum_str = str(v["visningsdatum"])
                dag       = datum_str.split("-")[2]
                mnad_num  = int(datum_str.split("-")[1])
                st.markdown(f"**{dag}**  \n{_MANAD[mnad_num]}")

            with col_info:
                st.markdown(f"**{v['adress']}**")
                st.caption(f"Kl {v['starttid']} - {v['sluttid']}")


def render_rekommenderade(df: pd.DataFrame) -> None:
    """
    Visar upp till 5 rekommenderade bostäder med bild matchad till bostadstyp.
    Sorterar, lägst pris per kvm, för "bäst värde".
    """
    st.markdown("### Rekommenderade för dig")

    if df.empty:
        st.info("Inga bostäder matchar ditt filter.")
        return

    top = df.sort_values("pris_per_kvm").head(5)

    for i, (_, rad) in enumerate(top.iterrows()):
        with st.container(border=True):
            col_bild, col_info = st.columns([1, 2])

            with col_bild:
                st.image(_bild_url(rad["typ"], i), use_container_width=True)

            with col_info:
                st.markdown(f"**{format_sek(rad['pris'])}**")
                st.markdown(f"**{rad['adress']}, {rad['område']}**")
                c1, c2, c3 = st.columns(3)
                c1.caption(f"{int(rad['rum'])} rum")
                c2.caption(f"{int(rad['boyta'])} m2")
                c3.caption(str(rad["typ"]).capitalize())
                if rad.get("avgift") and rad["avgift"] > 0:
                    st.caption(f"{int(rad['avgift']):,} kr/mån".replace(",", " "))