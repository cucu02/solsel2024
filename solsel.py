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

        # Validasi keberadaan kolom yang diharapkan
        required_columns = ['Kecamatan', 'Suara 01', 'Suara 02', 'Suara Tidak Sah', 'DPT', 'Suara Sah']
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

            # Hitung total TPS dan jumlah TPS yang sudah masuk
            total_tps_per_kecamatan = df.groupby('Kecamatan').size().reset_index(name='Total TPS')
            tps_masuk_per_kecamatan = df[df['Suara Sah'] > 0].groupby('Kecamatan').size().reset_index(name='TPS Masuk')

            # Gabungkan ke DataFrame utama
            df_grouped = df.groupby('Kecamatan', as_index=False).agg({
                'Suara 01': 'sum',
                'Suara 02': 'sum',
                'Suara Tidak Sah': 'sum',
                'DPT': 'sum'
            })
            df_grouped = pd.merge(df_grouped, total_tps_per_kecamatan, on='Kecamatan', how='left')
            df_grouped = pd.merge(df_grouped, tps_masuk_per_kecamatan, on='Kecamatan', how='left').fillna(0)

            # Hitung persentase TPS masuk
            df_grouped['Persentase TPS'] = (df_grouped['TPS Masuk'] / df_grouped['Total TPS']) * 100

            # Hitung total perolehan Suara 01 dan Suara 02
            total_suara_01 = int(df_grouped['Suara 01'].sum())
            total_suara_02 = int(df_grouped['Suara 02'].sum())
            total_dpt = int(df['DPT'].sum()) if 'DPT' in df.columns else 0

            # Metrics Layout
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Jumlah Kecamatan", df['Kecamatan'].nunique())
            with col2:
                st.metric("Total TPS", int(total_tps_per_kecamatan['Total TPS'].sum()))
            with col3:
                st.metric("Jumlah TPS yang sudah masuk", int(tps_masuk_per_kecamatan['TPS Masuk'].sum()))

            col4, col5 = st.columns(2)
            with col4:
                st.metric("Total Perolehan Suara 01", total_suara_01)
            with col5:
                st.metric("Total Perolehan Suara 02", total_suara_02)

            # Layout untuk menampilkan dua chart berdampingan
            col_chart1, col_chart2 = st.columns(2)

            # Chart 1: Segmented Bar Chart untuk Perolehan Suara dan Persentase TPS
            with col_chart1:
                st.subheader("Perolehan Suara dan Persentase TPS per Kecamatan")
                option_segmented_bar = {
                    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                    "legend": {"data": ["Suara 01", "Suara 02", "Persentase TPS (%)"], "top": "5%"},
                    "xAxis": {"type": "value", "boundaryGap": [0, 0.01]},
                    "yAxis": {"type": "category", "data": df_grouped['Kecamatan'].tolist()},
                    "series": [
                        {
                            "name": "Suara 01",
                            "type": "bar",
                            "stack": "total",
                            "label": {"show": True, "position": "inside", "formatter": "{c}"},
                            "data": df_grouped['Suara 01'].tolist(),
                            "itemStyle": {"color": "#fac858"}
                        },
                        {
                            "name": "Suara 02",
                            "type": "bar",
                            "stack": "total",
                            "label": {"show": True, "position": "inside", "formatter": "{c}"},
                            "data": df_grouped['Suara 02'].tolist(),
                            "itemStyle": {"color": "#5470c6"}
                        },
                        {
                            "name": "Persentase TPS (%)",
                            "type": "bar",
                            "stack": None,  # Tidak ditumpuk
                            "label": {"show": True, "position": "right", "formatter": "{c}%"},
                            "data": df_grouped['Persentase TPS'].tolist(),
                            "itemStyle": {"color": "#91cc75"}  # Warna hijau untuk persentase TPS
                        }
                    ]
                }
                st_echarts(options=option_segmented_bar, height="600px")

            # Chart 2: Total Perolehan Suara 01 dan Suara 02 dalam bentuk Pie Chart
            with col_chart2:
                st.subheader("Total Perolehan Suara")
                option_pie_chart = {
                    "tooltip": {"trigger": "item"},
                    "legend": {"top": "5%", "left": "center"},
                    "series": [
                        {
                            "name": "Total Perolehan Suara",
                            "type": "pie",
                            "radius": "50%",
                            "data": [
                                {"value": total_suara_01, "name": "Suara 01", "itemStyle": {"color": "#fac858"}},
                                {"value": total_suara_02, "name": "Suara 02", "itemStyle": {"color": "#5470c6"}}
                            ]
                        }
                    ]
                }
                st_echarts(options=option_pie_chart, height="600px")

    else:
        st.write("Tidak ada data yang ditemukan.")
else:
    st.write(f"Error: {response.status_code}, {response.text}")

# Footer
st.markdown("""
    Dikembangkan oleh [Palendo](#), Untuk korespondensi hubungi duckblurry-royal-coma@duck.com
""", unsafe_allow_html=True)
