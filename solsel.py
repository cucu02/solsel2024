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
        required_columns = ['Kecamatan', 'Nomor TPS', 'Suara 01', 'Suara 02', 'Suara Tidak Sah', 'DPT', 'Suara Sah']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            st.error(f"Kolom berikut tidak ditemukan: {', '.join(missing_columns)}")
        else:
            # Standarisasi kolom 'Kecamatan'
            df['Kecamatan'] = df['Kecamatan'].str.strip().str.title()

            # Konversi kolom numerik
            df['Suara 01'] = pd.to_numeric(df['Suara 01'], errors='coerce').fillna(0)
            df['Suara 02'] = pd.to_numeric(df['Suara 02'], errors='coerce').fillna(0)
            df['Suara Tidak Sah'] = pd.to_numeric(df['Suara Tidak Sah'], errors='coerce').fillna(0)
            df['DPT'] = pd.to_numeric(df['DPT'], errors='coerce').fillna(0)
            df['Suara Sah'] = pd.to_numeric(df['Suara Sah'], errors='coerce').fillna(0)

            # Periksa dan proses kolom opsional 'Surat Suara + 2,5% dari DPT'
            if 'Surat Suara + 2,5% dari DPT' in df.columns:
                df['Surat Suara + 2,5% dari DPT'] = pd.to_numeric(df['Surat Suara + 2,5% dari DPT'], errors='coerce').fillna(0)
            else:
                st.warning("Kolom 'Surat Suara + 2,5% dari DPT' tidak ditemukan. Pastikan data Google Sheets memiliki kolom tersebut.")

            # Hitung total DPT
            total_dpt = int(df['DPT'].sum())

            # Hitung jumlah TPS yang sudah mengirimkan data
            jumlah_tps_masuk = df[df['Suara Sah'] > 0].shape[0]

            # Hitung total suara 01 dan 02
            total_suara_01 = int(df['Suara 01'].sum())
            total_suara_02 = int(df['Suara 02'].sum())

            # Tambahkan kolom "Total TPS per Kecamatan" dan "TPS Masuk per Kecamatan"
            df['Nomor TPS'] = pd.to_numeric(df['Nomor TPS'], errors='coerce').fillna(0)
            df_kecamatan = df.groupby('Kecamatan').agg({
                'Nomor TPS': 'count',  # Total TPS per Kecamatan
                'Suara Sah': lambda x: (x > 0).sum(),  # TPS yang sudah mengirimkan data
                'Suara 01': 'sum',
                'Suara 02': 'sum'
            }).reset_index()

            # Hitung persentase TPS masuk per Kecamatan
            df_kecamatan['Persentase TPS Masuk'] = (df_kecamatan['Suara Sah'] / df_kecamatan['Nomor TPS']) * 100

            # Metrics Layout
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Jumlah Kecamatan", df['Kecamatan'].nunique())
            with col2:
                st.metric("Jumlah TPS", df.shape[0])
            with col3:
                st.metric("TPS yang Sudah Mengirimkan Data", jumlah_tps_masuk)

            # Barisan metrik Total DPT, Suara 01, Suara 02
            col4, col5, col6, col7 = st.columns(4)
            with col4:
                st.metric("Total DPT", total_dpt)
            with col5:
                st.metric("TPS yang Sudah Mengirimkan Data", jumlah_tps_masuk)
            with col6:
                st.metric("Total Suara 01", total_suara_01)
            with col7:
                st.metric("Total Suara 02", total_suara_02)

            # Chart 1: Stacked Bar Chart untuk Perolehan Suara Paslon dan Persentase TPS Masuk per Kecamatan
            st.subheader("Perolehan Suara dan Persentase TPS Masuk per Kecamatan")
            option_segmented_bar = {
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "legend": {"data": ["Suara 01", "Suara 02", "Persentase TPS Masuk"], "top": "5%"},
                "xAxis": {"type": "value", "boundaryGap": [0, 0.01]},
                "yAxis": {"type": "category", "data": df_kecamatan['Kecamatan'].tolist()},
                "series": [
                    {
                        "name": "Suara 01",
                        "type": "bar",
                        "stack": "total",
                        "label": {"show": True, "position": "inside", "formatter": "{c}"},
                        "data": df_kecamatan['Suara 01'].tolist(),
                        "itemStyle": {"color": "#fac858"}
                    },
                    {
                        "name": "Suara 02",
                        "type": "bar",
                        "stack": "total",
                        "label": {"show": True, "position": "inside", "formatter": "{c}"},
                        "data": df_kecamatan['Suara 02'].tolist(),
                        "itemStyle": {"color": "#5470c6"}
                    },
                    {
                        "name": "Persentase TPS Masuk",
                        "type": "bar",
                        "stack": "total",
                        "label": {"show": True, "position": "right", "formatter": "{c}%"},
                        "data": df_kecamatan['Persentase TPS Masuk'].tolist(),
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
