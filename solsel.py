import streamlit as st
import pandas as pd
import requests
from streamlit_echarts import st_echarts

# Konfigurasi halaman harus diatur di bagian paling atas
st.set_page_config(layout="wide", page_title="Quick Count Pilkada Solsel 2024", page_icon="🗳️")
st.title("Quick Count Pilkada Solsel 2024")

# ID dari Google Sheets dan API Key
SHEET_ID = "11VpCK1BHH74-LOL6dMT8g4W28c_a9Ialf-Gu2CLAfSo"
API_KEY = "AIzaSyD48O12Pwu9KE3o9Gl0YO1JM0hSUiwR3k8"  # Gantilah dengan API Key yang benar
RANGE = "Sheet3!A1:Z1000"  # Perluas rentang untuk mencakup lebih banyak kolom

# Membuat URL API untuk mengakses data dari Google Sheets
url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{RANGE}?key={API_KEY}"

# Mengirim permintaan GET ke URL API
response = requests.get(url)

# Jika berhasil mendapatkan data (status code 200)
if response.status_code == 200:
    data = response.json()
    values = data.get('values', [])
    
    if values:
        # Konversi data ke Pandas DataFrame
        df = pd.DataFrame(values[1:], columns=values[0])

        # Menghilangkan spasi tambahan pada nama kolom
        df.columns = df.columns.str.strip()

        # Tampilkan nama kolom untuk debugging
        st.write("Kolom yang ditemukan:", df.columns.tolist())

        # Validasi keberadaan kolom yang diharapkan
        required_columns = ['Kecamatan', 'Suara 01', 'Suara 02', 'Suara Sah']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            st.error(f"Kolom berikut tidak ditemukan: {', '.join(missing_columns)}")
        else:
            # Standarisasi kolom 'Kecamatan'
            df['Kecamatan'] = df['Kecamatan'].str.strip().str.title()

            # Konversi kolom numerik
            df['Suara 01'] = pd.to_numeric(df['Suara 01'], errors='coerce').fillna(0)
            df['Suara 02'] = pd.to_numeric(df['Suara 02'], errors='coerce').fillna(0)
            df['Suara Sah'] = pd.to_numeric(df['Suara Sah'], errors='coerce').fillna(0)

            # Tambahkan kolom TPS masuk (True jika 'Suara Sah' > 0)
            df['TPS Masuk'] = df['Suara Sah'] > 0

            # Hitung total TPS dan TPS masuk per kecamatan
            df_grouped_tps = df.groupby('Kecamatan', as_index=False).agg(
                TotalTPS=('TPS Masuk', 'count'),  # Total TPS per kecamatan
                TPSMasuk=('TPS Masuk', 'sum')  # TPS yang sudah mengirim data
            )
            # Hitung persentase TPS masuk
            df_grouped_tps['Persen TPS Masuk'] = (df_grouped_tps['TPSMasuk'] / df_grouped_tps['TotalTPS']) * 100

            # Hitung perolehan suara per kecamatan
            df_grouped = df.groupby('Kecamatan', as_index=False).agg({
                'Suara 01': 'sum',
                'Suara 02': 'sum'
            })

            # Gabungkan persentase TPS masuk ke data perolehan suara
            df_grouped = pd.merge(df_grouped, df_grouped_tps[['Kecamatan', 'Persen TPS Masuk']], on='Kecamatan', how='left')

            # Hitung total perolehan suara
            total_suara_01 = int(df_grouped['Suara 01'].sum())
            total_suara_02 = int(df_grouped['Suara 02'].sum())

            # Metrics Layout
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Jumlah Kecamatan", df['Kecamatan'].nunique())
            with col2:
                st.metric("Total TPS", df.shape[0])
            with col3:
                st.metric("Jumlah TPS yang sudah masuk", int(df['TPS Masuk'].sum()))

            # Chart 1: Segmented Bar Chart untuk Perolehan Suara Paslon per Kecamatan dengan Persentase TPS Masuk
            st.subheader("Perolehan Suara per Kecamatan dengan Persentase TPS Masuk")
            option_segmented_bar = {
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "legend": {"data": ["Suara 01", "Suara 02", "Persen TPS Masuk"], "top": "5%"},
                "xAxis": {"type": "value", "boundaryGap": [0, 0.01]},
                "yAxis": {
                    "type": "category",
                    "data": df_grouped['Kecamatan'].tolist()
                },
                "series": [
                    {
                        "name": "Suara 01",
                        "type": "bar",
                        "stack": "total",
                        "label": {
                            "show": True,
                            "position": "inside",
                            "formatter": "{c}"
                        },
                        "data": df_grouped['Suara 01'].tolist(),
                        "itemStyle": {"color": "#fac858"}
                    },
                    {
                        "name": "Suara 02",
                        "type": "bar",
                        "stack": "total",
                        "label": {
                            "show": True,
                            "position": "inside",
                            "formatter": "{c}"
                        },
                        "data": df_grouped['Suara 02'].tolist(),
                        "itemStyle": {"color": "#5470c6"}
                    },
                    {
                        "name": "Persen TPS Masuk",
                        "type": "line",
                        "label": {
                            "show": True,
                            "formatter": "{c}%"
                        },
                        "data": df_grouped['Persen TPS Masuk'].tolist(),
                        "itemStyle": {"color": "#91cc75"}
                    }
                ]
            }
            st_echarts(options=option_segmented_bar, height="600px")

    else:
        st.write("Tidak ada data yang ditemukan.")
else:
    st.write(f"Error: {response.status_code}, {response.text}")

# Footer
st.markdown("""
    Dikembangkan oleh [Palendo](#), Untuk korespondensi hubungi duckblurry-royal-coma@duck.com
""", unsafe_allow_html=True)
