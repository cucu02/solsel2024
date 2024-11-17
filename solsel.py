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
        #st.write("Kolom yang ditemukan:", df.columns.tolist())

        # Validasi keberadaan kolom yang diharapkan
        required_columns = ['Kecamatan', 'Suara 01', 'Suara 02', 'Suara Tidak Sah', 'DPT']
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

            # Periksa dan proses kolom opsional 'Surat Suara + 2,5% dari DPT'
            if 'Surat Suara + 2,5% dari DPT' in df.columns:
                df['Surat Suara + 2,5% dari DPT'] = pd.to_numeric(df['Surat Suara + 2,5% dari DPT'], errors='coerce').fillna(0)
            else:
                st.warning("Kolom 'Surat Suara + 2,5% dari DPT' tidak ditemukan. Pastikan data Google Sheets memiliki kolom tersebut.")

            # Filter out invalid rows
            df = df[df['Kecamatan'] != 'Kecamatan']

            # Mengelompokkan data berdasarkan kecamatan dan menjumlahkan nilai suara
            df_grouped = df.groupby('Kecamatan', as_index=False).agg({
                'Suara 01': 'sum',
                'Suara 02': 'sum',
                'Suara Tidak Sah': 'sum',
                'DPT': 'sum'
            })

            # Hitung total perolehan Suara 01 dan Suara 02
            total_suara_01 = int(df_grouped['Suara 01'].sum())
            total_suara_02 = int(df_grouped['Suara 02'].sum())
            total_suara_tidak_sah = int(df['Suara Tidak Sah'].sum())
            total_tps = df['Kecamatan'].notna().sum()
            total_dpt = int(df['DPT'].sum()) if 'DPT' in df.columns else 0

            # Calculate unique count of Kecamatan and Nagari
            unique_kecamatan_count = df['Kecamatan'].nunique()
            unique_nagari_count = df['Nagari'].nunique() if 'Nagari' in df.columns else 0

            # Metrics Layout
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Jumlah Kecamatan", unique_kecamatan_count)
            with col2:
                st.metric("Jumlah Nagari", unique_nagari_count)
            with col3:
                st.metric("Jumlah TPS", total_tps)

            col4, col5, col6, col7 = st.columns(4)
            with col4:
                st.metric("Jumlah DPT", total_dpt)
            with col5:
                st.metric("Total Jumlah Suara Tidak Sah", total_suara_tidak_sah)
            with col6:
                st.metric("Total Perolehan Suara 01", total_suara_01)
            with col7:
                st.metric("Total Perolehan Suara 02", total_suara_02)

            # Layout untuk menampilkan dua chart berdampingan
            col_chart1, col_chart2 = st.columns(2)

            # Chart 1: Segmented Bar Chart untuk Perolehan Suara Paslon per Kecamatan
            with col_chart1:
                st.subheader("Perolehan Suara per Kecamatan")
                option_segmented_bar = {
                    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                    "legend": {"data": ["Suara 01", "Suara 02"], "top": "5%"},
                    "xAxis": {"type": "value", "boundaryGap": [0, 0.01]},
                    "yAxis": {"type": "category", "data": df_grouped['Kecamatan'].tolist()},
                    "series": [
                        {"name": "Suara 01", "type": "bar", "stack": "total", "label": {"show": True, "position": "inside", "formatter": "{c}"}, "data": df_grouped['Suara 01'].tolist(), "itemStyle": {"color": "#fac858"}},
                        {"name": "Suara 02", "type": "bar", "stack": "total", "label": {"show": True, "position": "inside", "formatter": "{c}"}, "data": df_grouped['Suara 02'].tolist(), "itemStyle": {"color": "#5470c6"}}
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
                        {"name": "Total Perolehan Suara", "type": "pie", "radius": "50%", "data": [
                            {"value": total_suara_01, "name": "Suara 01", "itemStyle": {"color": "#fac858"}},
                            {"value": total_suara_02, "name": "Suara 02", "itemStyle": {"color": "#5470c6"}}
                        ]}
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
