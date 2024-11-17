import streamlit as st
import pandas as pd
import requests
from streamlit_echarts import st_echarts

# Konfigurasi halaman harus diatur di bagian paling atas
st.set_page_config(layout="wide", page_title="Quick Count Pilkada Solsel 2024", page_icon="🗳️")
st.title("Quick Count Pilkada Solsel 2024")

# ID dari Google Sheets dan API Key
SHEET_ID = "11VpCK1BHH74-LOL6dMT8g4W28c_a9Ialf-Gu2CLAfSo"
API_KEY = "AIzaSyD48O12Pwu9KE3o9Gl0YO1JM0hSUiwR3k8"
RANGE = "Sheet3!A1:Z1000"

# Membuat URL API untuk mengakses data dari Google Sheets
url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{RANGE}?key={API_KEY}"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    values = data.get('values', [])
    if values:
        df = pd.DataFrame(values[1:], columns=values[0])
        df.columns = df.columns.str.strip().str.replace(" ", "_").str.lower()

        required_columns = ['kecamatan', 'suara_01', 'suara_02', 'suara_tidak_sah', 'dpt', 'suara_sah']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Kolom berikut tidak ditemukan: {', '.join(missing_columns)}")
        else:
            df['kecamatan'] = df['kecamatan'].str.strip().str.title()
            for col in ['suara_01', 'suara_02', 'suara_tidak_sah', 'dpt', 'suara_sah']:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            total_tps = df.shape[0]
            jumlah_tps_masuk = df[df['suara_sah'] > 0].shape[0]
            df = df[df['kecamatan'].notna() & (df['kecamatan'] != 'Kecamatan')]

            df_grouped = df.groupby('kecamatan', as_index=False).agg({
                'suara_01': 'sum',
                'suara_02': 'sum',
                'suara_tidak_sah': 'sum',
                'dpt': 'sum'
            })

            total_suara_01 = int(df_grouped['suara_01'].sum())
            total_suara_02 = int(df_grouped['suara_02'].sum())
            total_dpt = int(df['dpt'].sum())

            unique_kecamatan_count = df['kecamatan'].nunique()
            unique_nagari_count = df['nagari'].nunique() if 'nagari' in df.columns else 0

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Jumlah Kecamatan", unique_kecamatan_count)
            with col2:
                st.metric("Jumlah Nagari", unique_nagari_count)
            with col3:
                st.metric("Total TPS", total_tps)

            col4, col5, col6, col7 = st.columns(4)
            with col4:
                st.metric("Jumlah DPT", total_dpt)
            with col5:
                st.metric("Jumlah TPS yang sudah masuk", jumlah_tps_masuk)
            with col6:
                st.metric("Total Perolehan Suara 01", total_suara_01)
            with col7:
                st.metric("Total Perolehan Suara 02", total_suara_02)

            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.subheader("Perolehan Suara per Kecamatan")
                option_segmented_bar = {
                    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                    "legend": {"data": ["Suara 01", "Suara 02"], "top": "5%"},
                    "xAxis": {"type": "value", "boundaryGap": [0, 0.01]},
                    "yAxis": {"type": "category", "data": df_grouped['kecamatan'].tolist()},
                    "series": [
                        {
                            "name": "Suara 01",
                            "type": "bar",
                            "stack": "total",
                            "label": {
                                "show": True,
                                "position": "inside",
                                "formatter": "{c}"  # Menampilkan nilai
                            },
                            "data": df_grouped['suara_01'].tolist(),
                            "itemStyle": {"color": "#fac858"}  # Warna Suara 01
                        },
                        {
                            "name": "Suara 02",
                            "type": "bar",
                            "stack": "total",
                            "label": {
                                "show": True,
                                "position": "inside",
                                "formatter": "{c}"  # Menampilkan nilai
                            },
                            "data": df_grouped['suara_02'].tolist(),
                            "itemStyle": {"color": "#5470c6"}  # Warna Suara 02
                        }
                    ]
                }
                st_echarts(options=option_segmented_bar, height="600px")

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
    st.error(f"Error: {response.status_code}. Response: {response.text}")
