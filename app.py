import streamlit as st
import pandas as pd

st.set_page_config(page_title="GAIA - Penilaian Presentasi", layout="wide")

st.title("📋 Form Penilaian Presentasi - GAIA v2.1")

# ----------------------------------------------------------------------
# Bagian Informasi Student
# ----------------------------------------------------------------------
st.header("Informasi Peserta")

col1, col2, col3 = st.columns(3)
with col1:
    nama_student = st.text_input("Nama Student")
with col2:
    phase_student = st.selectbox("Phase Tugas", options=["P0M1", "P1M2", "P2M3"])
with col3:
    batch_student = st.text_input("Batch", placeholder="Contoh: HCK-040, RMT-055, dst")

st.divider()

# ----------------------------------------------------------------------
# Definisi Kriteria Penilaian (referensi: GAIA v2.1.html)
# ----------------------------------------------------------------------
criteria = {
    "Verbal Communication": {
        "Grammar & Pronounciation (Kekonsistenan Bahasa)": [
            (1, "Bahasa tidak konsisten; banyak kesalahan gramatikal dan penggunaan yang tidak konsisten dari kata-kata."),
            (2, "Konsistensi bahasa terganggu; ada beberapa kesalahan gramatikal dan variasi yang tidak dijelaskan."),
            (3, "Bahasa cukup konsisten; sedikit kesalahan gramatikal yang dapat diperbaiki dengan revisi."),
            (4, "Bahasa sangat konsisten; hampir tidak ada kesalahan gramatikal yang signifikan, dan penggunaan kata-kata konsisten."),
        ],
        "Articulation (Kejelasan Penyampaian Pesan)": [
            (1, "Pesan sangat tidak jelas; sulit untuk memahami maksud atau tujuan dari komunikasi."),
            (2, "Pesan kurang jelas; beberapa bagian mungkin ambigu atau memerlukan penjelasan tambahan."),
            (3, "Pesan cukup jelas; kebanyakan informasi dapat dipahami tetapi beberapa bagian memerlukan klarifikasi."),
            (4, "Pesan sangat jelas; informasi disampaikan dengan jelas dan mudah dipahami tanpa kebingungan."),
        ],
        "Clarity (Kekuatan Argumen)": [
            (1, "Argumen lemah atau tidak ada argumen yang disajikan; kurangnya dukungan atau logika yang kuat."),
            (2, "Argumen kurang kuat; ada beberapa dukungan tetapi masih ada celah atau kelemahan yang signifikan."),
            (3, "Argumen cukup kuat; ada dukungan yang memadai dan logika yang konsisten."),
            (4, "Argumen sangat kuat; didukung dengan bukti yang jelas dan logika yang kuat."),
        ],
    },
    "Written Communication": {
        "Slide Content": [
            (0.5, "Tidak adanya slide yang dibuat."),
            (1, "Adanya slide yang dibuat. Namun, minim penjelasan atau terlalu banyak hal yang tidak relevan yang dimasukkan atau tampilan visual tidak menarik."),
            (1.5, "Adanya slide yang dibuat. Terdapat chart yang kurang tepat atau kurang detail penjelasannya. Mayoritas informasi memberikan nilai tambah."),
            (2, "Adanya slide yang dibuat. Materi visual digunakan dengan sangat baik; meningkatkan pemahaman dan minat audiens serta memperkuat presentasi secara keseluruhan."),
        ],
        "Demo Content": [
            (0.5, "Tidak adanya demo program yang dibuat."),
            (1, "Melakukan demo program namun dengan minim penjelasan (penjelasan tidak menyeluruh)."),
            (1.5, "Melakukan demo program dengan mayoritas penjelasan dapat dipahami."),
            (2, "Melakukan demo program dengan penjelasan yang detail per bagian yang dibuat."),
        ],
    },
    "Presentation": {
        "Introduction & Problem Statement (Pengenalan)": [
            (1, "Pengenalan tidak mencakup salah satu dari ketiga hal (problem statement, objective, dan dataset) dan dijelaskan dengan minim dan secara cepat."),
            (2, "Pengenalan tidak mencakup salah satu dari ketiga hal (problem statement, objective, dan dataset) dan dijelaskan dengan minim dengan tempo yang masih dapat dimengerti."),
            (3, "Pengenalan mencakup ketiga hal (problem statement, objective, dan dataset). Namun, dijelaskan dengan minim dan atau terlalu cepat."),
            (4, "Pengenalan mencakup ketiga hal (problem statement, objective, dan dataset). Penjelasan yang diberikan memuaskan dengan tempo yang masih dapat dimengerti."),
        ],
        "Flow (Tempo)": [
            (1, "Tempo yang digunakan tidak menentu, terkadang cepat, terkadang lambat. Terdapat banyak momen hening dan penggunaan filler sehingga pesan tidak tersampaikan dengan baik."),
            (2, "Tempo yang digunakan kurang konsisten, terkadang normal, terkadang cepat. Terdapat sedikit momen hening dan penggunaan filler."),
            (3, "Tempo yang digunakan cukup konsisten. Tidak ada momen hening dan terkadang menggunakan filler."),
            (4, "Tempo yang digunakan konsisten dari awal hingga akhir. Tidak ada momen hening dan tidak ada penggunaan filler."),
        ],
        "Conclusion (Kesimpulan)": [
            (1, "Kesimpulan tidak jelas atau tidak mengikat kembali dengan topik secara efektif."),
            (2, "Kesimpulan yang kurang kuat atau terlalu singkat; kurangnya pengikatan kembali dengan elemen-elemen kunci presentasi."),
            (3, "Kesimpulan yang memadai; merangkum poin-poin kunci dengan baik dan memberikan penutup yang memuaskan."),
            (4, "Kesimpulan yang sangat kuat; secara efektif merangkum poin-poin penting dan meninggalkan kesan yang kuat pada pendengar."),
        ],
        "Engagement - Eye Contact": [
            (0, "Student tidak melakukan on cam."),
            (0.5, "Kurangnya kontak mata atau kontak mata yang tidak memadai dengan audiens; mengurangi koneksi interpersonal."),
            (1, "Kontak mata yang kurang konsisten atau terkadang terputus; perlu diperbaiki untuk meningkatkan keterlibatan dengan audiens."),
            (1.5, "Kontak mata yang cukup konsisten; menciptakan koneksi dengan audiens dan menunjukkan kepercayaan diri."),
            (2, "Kontak mata yang sangat baik; menunjukkan ketertarikan dan keterlibatan yang kuat dengan audiens."),
        ],
        "Engagement - Enthusiasm": [
            (0.5, "Pembicara menjelaskan dengan intonasi dan volume suara tidak bervariasi, monoton, dan sulit untuk mempertahankan minat pendengar."),
            (1, "Pembicara menjelaskan dengan intonasi dan volume suara kadang-kadang bervariasi tetapi kurang konsisten; tidak selalu menarik perhatian dengan baik."),
            (1.5, "Pembicara menjelaskan dengan intonasi dan volume suara yang cukup bervariasi; membantu mempertahankan minat dan menekankan poin-poin penting."),
            (2, "Pembicara menjelaskan dengan intonasi dan volume suara yang sangat bervariasi; mendukung dan meningkatkan pengalaman mendengarkan secara keseluruhan."),
        ],
        "Time Management": [
            (1, "Waktu presentasi lebih dari 4 menit dari seharusnya."),
            (2, "Waktu presentasi melebihi 3 - 4 menit dari seharusnya."),
            (3, "Waktu presentasi melebihi 1 - 2 menit dari seharusnya."),
            (4, "Waktu presentasi masih dalam batas maksimal presentasi."),
        ],
    },
}

# ----------------------------------------------------------------------
# Form Penilaian
# ----------------------------------------------------------------------
st.header("Form Penilaian")

results = {}

with st.form("form_penilaian"):
    for kriteria, sub_kriteria_dict in criteria.items():
        st.subheader(kriteria)
        for idx, (sub_kriteria, options) in enumerate(sub_kriteria_dict.items(), start=1):
            st.markdown(f"**{idx}. {sub_kriteria}**")
            choice = st.radio(
                label=sub_kriteria,
                options=options,
                format_func=lambda x: f"{x[0]} : {x[1]}",
                key=sub_kriteria,
                label_visibility="collapsed",
            )
            results[sub_kriteria] = choice[0]
        st.markdown("---")

    submitted = st.form_submit_button("Submit Penilaian")

# ----------------------------------------------------------------------
# Hasil & Simpan
# ----------------------------------------------------------------------
if submitted:
    if not nama_student or not phase_student or not batch_student:
        st.error("Mohon lengkapi Nama Student, Phase, dan Batch terlebih dahulu.")
    else:
        df = pd.DataFrame(
            list(results.items()), columns=["Sub Kriteria", "Point"]
        )

        total_score = df["Point"].sum()

        st.success("Penilaian berhasil disimpan!")
        st.subheader("Hasil Penilaian")
        st.dataframe(df, use_container_width=True)
        st.markdown(f"**Total Skor: {total_score}**")
        st.markdown(f"**Nilai: {total_score/36*100:.2f}**")

        csv = df.to_csv(index=False).encode("utf-8")
        file_name = f"scores/{batch_student}_{phase_student}_{nama_student}_presentasi.csv"

        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=file_name,
            mime="text/csv",
        )