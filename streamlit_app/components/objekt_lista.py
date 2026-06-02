# Object listing components
# Three sub-functions that match the UX sidebar and recommended-listings design

import streamlit as st
import pandas as pd
from utils.helpers import (
    load_all, load_visningar, format_sek,
    get_anvandare, is_inloggad,
    load_sparade_for_user, spara_bostad, ta_bort_sparad, is_sparad,
)
from utils.constants import COL_SPARAD

_MANAD = ["", "JAN", "FEB", "MAR", "APR", "MAJ", "JUN",
          "JUL", "AUG", "SEP", "OKT", "NOV", "DEC"]

# Image URLs grouped by listing type
# Unsplash URLs are used as fallback
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
    "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=600",
]


def _bild_url(typ: str, index: int) -> str:
    """Return an image URL matching the listing type, indexed by position."""
    lista = _BILDER.get(str(typ).lower(), _FALLBACK)
    return lista[index % len(lista)]


def render_sparade() -> None:
    """Show listings saved by the logged-in user."""
    st.markdown("### Mina sparade")

    if not is_inloggad():
        st.caption("Logga in för att spara bostäder.")
        return

    anvandare = get_anvandare()
    sparade_ids = load_sparade_for_user(anvandare)

    if not sparade_ids:
        st.caption("Du har inte sparat några bostäder ännu.")
        return

    df = load_all()
    sparade = df[df["id"].isin(sparade_ids)].head(3)

    for i, (_, rad) in enumerate(sparade.iterrows()):
        with st.container(border=True):
            st.image(_bild_url(rad["typ"], i), use_container_width=True)
            st.markdown(f"**{format_sek(rad['pris'])}**")
            st.caption(f"{rad['adress']}, {rad['område']}")
            c1, c2, c3 = st.columns(3)
            c1.caption(f"{int(rad['rum'])} rum")
            c2.caption(f"{int(rad['boyta'])} m2")
            c3.caption(str(rad["typ"]).capitalize())
            if st.button("Ta bort", key=f"tabort_{rad['id']}", use_container_width=True):
                ta_bort_sparad(anvandare, int(rad["id"]))
                st.rerun()


def render_visningar() -> None:
    """Show upcoming viewings from visningar.csv."""
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
    Show up to 5 recommended listings with an image matched to the listing type.
    Sorted by lowest price per 'kvm' as a "best value" proxy.
    """
    st.markdown("### Rekommenderade för dig")

    if df.empty:
        st.info("Inga bostäder matchar ditt filter.")
        return

    anvandare  = get_anvandare() if is_inloggad() else None
    top        = df.sort_values("pris_per_kvm").head(5)

    for i, (_, rad) in enumerate(top.iterrows()):
        bostad_id = int(rad["id"])
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
                    st.caption(f"{int(rad['avgift']):,} kr/man".replace(",", " "))

                if anvandare:
                    sparad = is_sparad(anvandare, bostad_id)
                    label  = "Sparad" if sparad else "Spara"
                    if st.button(label, key=f"spara_{bostad_id}", use_container_width=True):
                        if sparad:
                            ta_bort_sparad(anvandare, bostad_id)
                        else:
                            spara_bostad(anvandare, bostad_id)
                        st.rerun()