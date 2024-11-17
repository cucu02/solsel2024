import streamlit as st
import pandas as pd
import requests
from streamlit_echarts import st_echarts

# Konfigurasi halaman
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

        required_columns = ['kecamatan', 'suara_01', 'suara_02', 'suara_tidak_sah', 'dpt', 'suara_sah', 'tps_terdaftar']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Kolom berikut tidak ditemukan: {', '.join(missing_columns)}")
        else:
            df['kecamatan'] = df['kecamatan'].str.strip().str.title()
            for col in ['suara_01', 'suara_02', 'suara_tidak_sah', 'dpt', 'suara_sah', 'tps_terdaftar']:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            # Hitung persentase TPS yang sudah masuk berdasarkan 'Suara Sah' > 0
            df['tps_masuk'] = (df['suara_sah'] > 0).astype(int)
            tps_persen = df.groupby('kecamatan', as_index=False).agg({
                'tps_masuk': 'sum',
                'tps_terdaftar': 'sum'
            })
            tps_persen['persentase_tps'] = (tps_persen['tps_masuk'] / tps_persen['tps_terdaftar']) * 100

            df_grouped = df.groupby('kecamatan', as_index=False).agg({
                'suara_01': 'sum',
                'suara_02': 'sum',
                'suara_tidak_sah': 'sum',
                'dpt': 'sum'
            })

            df_grouped = pd.merge(df_grouped, tps_persen[['kecamatan', 'persentase_tps']], on='kecamatan', how='left')

            total_suara_01 = int(df_grouped['suara_01'].sum())
            total_suara_02 = int(df_grouped['suara_02'].sum())
            total_dpt = int(df['dpt'].sum())

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Jumlah Kecamatan", df['kecamatan'].nunique())
            with col2:
                st.metric("Total TPS", int(df['tps_terdaftar'].sum()))
            with col3:
                st.metric("Jumlah TPS yang sudah masuk", int(df['tps_masuk'].sum()))

            col4, col5 = st.columns(2)
            with col4:
                st.metric("Total Perolehan Suara 01", total_suara_01)
            with col5:
                st.metric("Total Perolehan Suara 02", total_suara_02)

            # Chart 1: Bar Chart Bertumpuk untuk Perolehan Suara
            st.subheader("Perolehan Suara per Kecamatan")
            option_stacked_bar = {
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "legend": {"data": ["Suara 01", "Suara 02"], "top": "5%"},
                "xAxis": {"type": "value", "boundaryGap": [0, 0.01]},
                "yAxis": {"type": "category", "data": df_grouped['kecamatan'].tolist()},
                "series": [
                    {
                        "name": "Suara 01",
                        "type": "bar",
                        "stack": "total",
                        "label": {"show": True, "position": "inside", "formatter": "{c}"},
                        "data": df_grouped['suara_01'].tolist(),
                        "itemStyle": {"color": "#fac858"}
                    },
                    {
                        "name": "Suara 02",
                        "type": "bar",
                        "stack": "total",
                        "label": {"show": True, "position": "inside", "formatter": "{c}"},
                        "data": df_grouped['suara_02'].tolist(),
                        "itemStyle": {"color": "#5470c6"}
                    }
                ]
            }
            st_echarts(options=option_stacked_bar, height="700px")

            # Chart 2: Bar Chart untuk Persentase TPS Masuk
            st.subheader("Persentase TPS yang Sudah Masuk per Kecamatan")
            option_percentage_bar = {
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "xAxis": {"type": "value", "boundaryGap": [0, 0.01]},
                "yAxis": {"type": "category", "data": df_grouped['kecamatan'].tolist()},
                "series": [
                    {
                        "name": "Persentase TPS",
                        "type": "bar",
                        "label": {"show": True, "position": "inside", "formatter": "{c}%"},
                        "data": df_grouped['persentase_tps'].tolist(),
                        "itemStyle": {"color": "#91cc75"}
                    }
                ]
            }
            st_echarts(options=option_percentage_bar, height="700px")
    else:
        st.write("Tidak ada data yang ditemukan.")
else:
    st.write(f"Error: {response.status_code}, {response.text}")

# Footer
st.markdown("""
    Dikembangkan oleh [Palendo](#), Untuk korespondensi hubungi duckblurry-royal-coma@duck.com
""", unsafe_allow_html=True)
