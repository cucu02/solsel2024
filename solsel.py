import streamlit as st
import pandas as pd
import requests
from streamlit_echarts import st_echarts

# ID dari Google Sheets dan API Key
SHEET_ID = "11VpCK1BHH74-LOL6dMT8g4W28c_a9Ialf-Gu2CLAfSo"
API_KEY = "YOUR_GOOGLE_API_KEY"
RANGE = "Sheet3!A1:J1000"

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
        
        # Konversi kolom numerik
        df['Suara 01'] = pd.to_numeric(df['Suara 01'], errors='coerce').fillna(0)
        df['Suara 02'] = pd.to_numeric(df['Suara 02'], errors='coerce').fillna(0)
        
        # Mengelompokkan data berdasarkan kecamatan dan menjumlahkan nilai suara
        df_grouped = df.groupby('Kecamatan', as_index=False).agg({
            'Suara 01': 'sum',
            'Suara 02': 'sum'
        })

        # Hitung total perolehan Suara 01 dan Suara 02
        total_suara_01 = int(df_grouped['Suara 01'].sum())
        total_suara_02 = int(df_grouped['Suara 02'].sum())
        total_suara = total_suara_01 + total_suara_02

        # Mulai dashboard
        st.set_page_config(layout="wide", page_title="Quick Count Pilkada Solsel 2024", page_icon="🗳️")
        st.title("Quick Count Pilkada Solsel 2024")

        # Segmented Bar Chart untuk Perolehan Suara
        st.subheader("Segmented Bar Chart Perolehan Suara Paslon")

        # Menentukan proporsi suara
        proporsi_suara_01 = round((total_suara_01 / total_suara) * 100, 2)
        proporsi_suara_02 = round((total_suara_02 / total_suara) * 100, 2)

        # Konfigurasi segmented bar chart
        option_segmented_bar = {
            "tooltip": {
                "trigger": "item",
                "formatter": "{b}: {c} ({d}%)"
            },
            "xAxis": {
                "type": "value",
                "show": False
            },
            "yAxis": {
                "type": "category",
                "show": False
            },
            "series": [
                {
                    "type": "bar",
                    "stack": "total",
                    "label": {
                        "show": True,
                        "position": "inside",
                        "formatter": "{c}"
                    },
                    "data": [
                        {
                            "value": total_suara_01,
                            "name": f"Suara 01 ({proporsi_suara_01}%)",
                            "itemStyle": {"color": "#fac858"}
                        },
                        {
                            "value": total_suara_02,
                            "name": f"Suara 02 ({proporsi_suara_02}%)",
                            "itemStyle": {"color": "#5470c6"}
                        }
                    ]
                }
            ]
        }

        # Tampilkan segmented bar chart
        st_echarts(options=option_segmented_bar, height="100px")

    else:
        st.write("Tidak ada data yang ditemukan.")
else:
    st.write(f"Error: {response.status_code}, {response.text}")

# Footer
st.markdown("""
    Dikembangkan oleh [Cucu Anduang](https://scholar.google.com/citations?user=RUg3RQUAAAAJ&hl=id&oi=ao), Untuk korespondensi hubungi duckblurry-royal-coma@duck.com
""", unsafe_allow_html=True)
