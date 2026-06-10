import streamlit as st
import pandas as pd
import numpy as np
import base64
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard Clustering Nilai TK", layout="wide")

# ======================
# FUNGSI BASE64 (AGAR GAMBAR LOKAL BISA JADI BACKGROUND)
# ======================
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

bg_base64 = get_base64_image("coding_kids.png")

# ======================
# CUSTOM CSS: POLA KARAKTER HIASAN DI BELAKANG
# ======================
if bg_base64:
    st.markdown(f"""
    <style>
    .stApp, .stMainView, .stHeader, .block-container, 
    [data-testid="stMainViewContext"], 
    [data-testid="stAppViewBlockContainer"], 
    [data-testid="stVerticalBlock"] {{
        background-color: transparent !important;
        background: transparent !important;
    }}

    html, body {{
        background-color: white !important;
    }}

    html::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: url("data:image/png;base64,{bg_base64}");
        background-size: 2000px; 
        background-repeat: repeat; 
        background-attachment: fixed;
        opacity: 0.06; 
        z-index: -2; 
    }}

    .main-title {{ color: #0369a1; font-family: 'Segoe UI', sans-serif; font-weight: 800; margin-bottom: 2px; }}
    .card {{ padding: 22px; border-radius: 14px; box-shadow: 0 4px 10px rgba(0,0,0,0.04); text-align: center; }}
    .card-rendah {{ background: linear-gradient(135deg, #fff5f5, #fed7d7); border-top: 6px solid #ef5350; }}
    .card-sedang {{ background: linear-gradient(135deg, #fffde7, #fef9c3); border-top: 6px solid #facc15; }}
    .card-tinggi {{ background: linear-gradient(135deg, #f0fdf4, #dcfce7); border-top: 6px solid #4ade80; }}
    .card-title {{ font-size: 14px; color: #4a5568; font-weight: 700; margin-bottom: 8px; }}
    .card-value {{ font-size: 32px; font-weight: 800; color: #1a202c; }}
    h3 {{ color: #0f172a !important; font-weight: 700 !important; }}
    </style>
    """, unsafe_allow_html=True)

# ======================
# HEADER DASHBOARD
# ======================
head_col1, head_col2 = st.columns([1, 5])
with head_col1:
    try:
        st.image("logo.png", width=125)
    except:
        st.info("💡 Logo header tidak ditemukan.")

with head_col2:
    st.markdown("<h1 class='main-title'>🚀 Dashboard Evaluasi Belajar Coding Anak</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#475569; font-size:16px; margin-top:-5px; font-weight:500;'>Analisis Kelompok Kedekatan Nilai (K-Means) Berdasarkan Jarak Jauh-Dekat Centroid</p>", unsafe_allow_html=True)

st.markdown("---")

# ======================
# INPUT & PROSES DATA
# ======================
file = st.file_uploader("📂 Tarik atau Pilih File Excel Nilai Siswa di Sini", type=["xlsx"])

if file:
    df = pd.read_excel(file)
    
    with st.expander("🔍 Buka Tabel Data Nilai Mentah"):
        st.dataframe(df, use_container_width=True)

    # Filter Kelas
    kelas_pilihan = st.selectbox("🎯 Pilih Kelas Yang Ingin Dievaluasi", df["Kelas"].unique()) if "Kelas" in df.columns else "Semua"
    data = df[df["Kelas"] == kelas_pilihan].copy() if "Kelas" in df.columns else df.copy()

    # Clustering K-Means
    fitur_kolom = ["Rata_Algoritma", "Rata_Pola", "Rata_Perulangan"]
    
    if all(col in data.columns for col in fitur_kolom):
        # Normalisasi dan Fit Model
        scaler = MinMaxScaler()
        data[fitur_kolom] = scaler.fit_transform(data[fitur_kolom])
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10, max_iter=100)
        data["Raw_Cluster"] = kmeans.fit_predict(data[fitur_kolom])
        
        # Pengurutan Kategori Berdasarkan Centroid
        sorted_clusters = pd.DataFrame(kmeans.cluster_centers_, columns=fitur_kolom).mean(axis=1).sort_values().index
        cluster_mapping = {sorted_clusters[0]: "Rendah", sorted_clusters[1]: "Sedang", sorted_clusters[2]: "Tinggi"}
        data["Kategori"] = data["Raw_Cluster"].map(cluster_mapping)
        
        kategori_order = ["Rendah", "Sedang", "Tinggi"]
        warna_skema = {"Rendah": "#ef5350", "Sedang": "#facc15", "Tinggi": "#4ade80"}
        counts = data["Kategori"].value_counts().reindex(kategori_order, fill_value=0)

        # ======================
        # VISUALISASI: KPI KARTU
        # ======================
        st.markdown(f"### 📈 Hasil Pengelompokan Kelas: <span style='color:#0369a1;'>{kelas_pilihan}</span>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        for col, kat in zip([col1, col2, col3], kategori_order):
            with col:
                st.markdown(f"""
                    <div class='card card-{kat.lower()}'>
                        <div class='card-title'>{'🔴' if kat=='Rendah' else '🟡' if kat=='Sedang' else '🟢'} KATEGORI {kat.upper()}</div>
                        <div class='card-value'>{counts[kat]} Siswa</div>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ======================
        # VISUALISASI JURUSAN BARIS 1: 3D PLOT & DONUT CHART
        # ======================
        g_col1, g_col2 = st.columns([3, 2])

        with g_col1:
            st.markdown("### 🌐 Plot Sebaran Jarak Centroid (3D)")
            fig_3d = px.scatter_3d(
                data, x="Rata_Algoritma", y="Rata_Pola", z="Rata_Perulangan",
                color="Kategori", color_discrete_map=warna_skema,
                category_orders={"Kategori": kategori_order},
                hover_name="Nama" if "Nama" in data.columns else None, opacity=0.8
            )
            fig_3d.add_trace(go.Scatter3d(
                x=kmeans.cluster_centers_[:, 0], y=kmeans.cluster_centers_[:, 1], z=kmeans.cluster_centers_[:, 2],
                mode="markers", marker=dict(size=15, color="#0f172a", symbol="x"), name="Pusat Centroid"
            ))
            fig_3d.update_layout(
                margin=dict(l=0, r=0, b=0, t=10), paper_bgcolor='rgba(0,0,0,0)',
                scene=dict(
                    xaxis_title="Algoritma", yaxis_title="Pola", zaxis_title="Perulangan",
                    bgcolor="rgba(230, 216, 255, 0.4)"
                )
            )
            st.plotly_chart(fig_3d, use_container_width=True)

        with g_col2:
            st.markdown("### 🍩 Persentase Proporsi Kelas")
            fig_donut = px.pie(names=counts.index, values=counts.values, hole=0.5, color=counts.index, color_discrete_map=warna_skema)
            fig_donut.update_traces(textinfo='percent+label', textfont_size=12)
            fig_donut.update_layout(margin=dict(l=10, r=10, b=10, t=10), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_donut, use_container_width=True)
            
        # ======================
        # VISUALISASI JURUSAN BARIS 2: BAR CHART UKURAN PENUH (LEBAR)
        # ======================
        st.markdown("---")
        st.markdown("### 📊 Rata-rata Nilai per Kategori (Analisis K-Means)")
        avg_data = data.groupby("Kategori")[fitur_kolom].mean().reset_index()
        avg_melted = avg_data.melt(
            id_vars="Kategori",
            value_vars=fitur_kolom,
            var_name="Mata_Pelajaran",
            value_name="Nilai"
        )

        fig_bar = px.bar(
            avg_melted,
            x="Kategori",
            y="Nilai",
            color="Mata_Pelajaran",
            barmode="group",
            text_auto=".2f"
        )
        fig_bar.update_layout(
            template="plotly_white",
            height=450
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # ======================
        # INSIGHT & TABEL DETAIL
        # ======================
        st.markdown("### 💡 Rekomendasi / Insight Hasil Belajar")
        if counts["Rendah"] > counts["Tinggi"]:
            st.warning("⚠️ **Evaluasi Diperlukan:** Jumlah anak di kategori **Rendah** terdeteksi lebih dominan. Disarankan memperbanyak aktivitas belajar coding berbasis game interaktif (seperti bongkar pasang blok visual di tablet).")
        else:
            st.success("✅ **Performa Bagus:** Mayoritas anak sudah berada di rentang capaian **Sedang & Tinggi**. Metode visual coding menggunakan tablet terbukti efektif membantu pemahaman pola logika mereka.")

        with st.expander("📋 Tampilkan Tabel Data Hasil Pengukuran Jarak (Skala 0-1)"):
            st.dataframe(data.drop(columns=["Raw_Cluster"]), use_container_width=True)
            
    else:
        st.error(f"Kolom penilaian {fitur_kolom} tidak ditemukan di file Excel Anda. Mohon periksa kembali filenya.")