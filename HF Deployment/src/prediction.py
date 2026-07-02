import streamlit as st
from utils.inference import predict_theme

EXAMPLES = {
    "Broken on arrival": "barang sampai dalam keadaan pecah, packing asal asalan",
    "Slow delivery": "pengiriman lama banget, sudah seminggu barang belum sampai juga",
    "Happy customer": "barangnya bagus banget, pengiriman cepat, seller ramah, recommended",
    "Wrong item": "warna yang dikirim tidak sesuai dengan yang saya pesan",
}


@st.cache_resource(show_spinner=False)
def _warm():
    predict_theme("warm up")   # load the model once so the first real prediction is fast
    return True


def run():
    st.header("🔮 Predict a Review's Theme")
    st.write(
        "Paste an Indonesian product review. The model embeds it, finds the closest theme among "
        "the topics it learned from Tokopedia reviews, and tells you whether it reads as "
        "**praise** or a **complaint**."
    )

    with st.spinner("Loading the language model..."):
        _warm()

    pick = st.selectbox("Try an example (optional)", ["-- type my own --", *EXAMPLES.keys()])
    default = "" if pick == "-- type my own --" else EXAMPLES[pick]
    text = st.text_area("Customer review", value=default, height=130,
                        placeholder="contoh: barang sampai pecah, packing asal-asalan...")

    if st.button("Predict theme", type="primary"):
        if not text.strip():
            st.warning("Please paste a review first.")
            return
        with st.spinner("Analyzing..."):
            cleaned, ranked = predict_theme(text)

        if not ranked:
            st.error("No usable text after cleaning - try a longer review.")
            return

        side, theme, sim = ranked[0]
        if side == "Positive":
            st.success(f"👍 **{theme}**  -  reads as a positive review")
        else:
            st.error(f"👎 **{theme}**  -  reads as a negative review")
        st.caption(f"Confidence (cosine similarity): {sim:.2f}")

        if len(ranked) > 1:
            st.markdown("**Other close themes:**")
            for s, th, sm in ranked[1:]:
                tag = "praise" if s == "Positive" else "complaint"
                st.write(f"- {th}  *({tag}, {sm:.2f})*")

        with st.expander("What the model actually read (after cleaning)"):
            st.code(cleaned or "(empty)")

    st.caption(
        "Themes were learned separately for positive and negative reviews; the app picks the "
        "single closest theme across both. Mixed Indonesian-English terms (e.g. 'fast charging') "
        "can occasionally be matched to a delivery/speed theme."
    )
