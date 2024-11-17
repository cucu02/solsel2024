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

            # Tambahkan kolom untuk hitung TPS masuk
            df['TPS Masuk'] = (df['Suara Sah'] > 0).astype(int)

            # Hitung data per kecamatan
            df_grouped = df.groupby('Kecamatan', as_index=False).agg({
                'Suara 01': 'sum',
                'Suara 02': 'sum',
                'TPS Masuk': 'sum'
            })
            df_grouped['Total TPS'] = df.groupby('Kecamatan').size().values
            df_grouped['Persentase TPS Masuk'] = (df_grouped['TPS Masuk'] / df_grouped['Total TPS'] * 100).round(2)

            # Chart: Perolehan Suara dengan Persentase di Kanan
            st.subheader("Perolehan Suara dan Persentase TPS Masuk per Kecamatan")

            option_bar_with_percentage = {
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "legend": {"data": ["Suara 01", "Suara 02"], "top": "5%"},
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
                            "formatter": "{c}"  # Menampilkan jumlah suara
                        },
                        "emphasis": {
                            "focus": "series"
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
                            "formatter": "{c}"  # Menampilkan jumlah suara
                        },
                        "emphasis": {
                            "focus": "series"
                        },
                        "data": df_grouped['Suara 02'].tolist(),
                        "itemStyle": {"color": "#5470c6"}
                    },
                    {
                        "name": "Persentase TPS Masuk",
                        "type": "bar",
                        "label": {
                            "show": True,
                            "position": "right",  # Menempatkan persentase di kanan
                            "formatter": "{c}%"  # Format persentase
                        },
                        "data": df_grouped['Persentase TPS Masuk'].tolist(),
                        "itemStyle": {"color": "transparent"}  # Membuat batang ini transparan
                    }
                ]
            }

            st_echarts(options=option_bar_with_percentage, height="600px")
    else:
        st.write("Tidak ada data yang ditemukan.")
else:
    st.write(f"Error: {response.status_code}, {response.text}")

# Footer
st.markdown("""
    Dikembangkan oleh [Palendo](#), Untuk korespondensi hubungi duckblurry-royal-coma@duck.com
""", unsafe_allow_html=True)
