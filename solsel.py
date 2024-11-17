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
        df.columns = df.columns.str.strip()

        required_columns = ['Kecamatan', 'Suara 01', 'Suara 02', 'Suara Tidak Sah', 'DPT', 'Suara Sah']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            st.error(f"Kolom berikut tidak ditemukan: {', '.join(missing_columns)}")
        else:
            df['Kecamatan'] = df['Kecamatan'].str.strip().str.title()
            df['Suara 01'] = pd.to_numeric(df['Suara 01'], errors='coerce').fillna(0)
            df['Suara 02'] = pd.to_numeric(df['Suara 02'], errors='coerce').fillna(0)
            df['Suara Tidak Sah'] = pd.to_numeric(df['Suara Tidak Sah'], errors='coerce').fillna(0)
            df['DPT'] = pd.to_numeric(df['DPT'], errors='coerce').fillna(0)
            df['Suara Sah'] = pd.to_numeric(df['Suara Sah'], errors='coerce').fillna(0)

            total_tps_per_kecamatan = df.groupby('Kecamatan').size().reset_index(name='Total TPS')
            tps_masuk_per_kecamatan = df[df['Suara Sah'] > 0].groupby('Kecamatan').size().reset_index(name='TPS Masuk')

            df_grouped = df.groupby('Kecamatan', as_index=False).agg({
                'Suara 01': 'sum',
                'Suara 02': 'sum',
                'Suara Tidak Sah': 'sum',
                'DPT': 'sum'
            })
            df_grouped = pd.merge(df_grouped, total_tps_per_kecamatan, on='Kecamatan', how='left')
            df_grouped = pd.merge(df_grouped, tps_masuk_per_kecamatan, on='Kecamatan', how='left').fillna(0)

            df_grouped['Persentase TPS'] = ((df_grouped['TPS Masuk'] / df_grouped['Total TPS']) * 100).round(2)

            total_suara_01 = int(df_grouped['Suara 01'].sum())
            total_suara_02 = int(df_grouped['Suara 02'].sum())
            total_dpt = int(df_grouped['DPT'].sum())
            total_tps = int(total_tps_per_kecamatan['Total TPS'].sum())
            total_tps_masuk = int(tps_masuk_per_kecamatan['TPS Masuk'].sum())
            jumlah_kecamatan = df['Kecamatan'].nunique()

            if 'Nagari' in df.columns:
                jumlah_nagari = df['Nagari'].nunique()
            else:
                jumlah_nagari = jumlah_kecamatan

            # Layout Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Jumlah Kecamatan", jumlah_kecamatan)
            with col2:
                st.metric("Jumlah Nagari", jumlah_nagari)
            with col3:
                st.metric("Total TPS", total_tps)

            col4, col5, col6, col7 = st.columns(4)
            with col4:
                st.metric("Total DPT", total_dpt)
            with col5:
                st.metric("TPS yang Masuk", total_tps_masuk)
            with col6:
                st.metric("Total Perolehan Suara 01", total_suara_01)
            with col7:
                st.metric("Total Perolehan Suara 02", total_suara_02)

            # Chart: Segmented Bar Chart untuk Perolehan Suara dan Persentase TPS
            st.subheader("Perolehan Suara dan Persentase TPS per Kecamatan")
            option_segmented_bar = {
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "legend": {"data": ["Suara 01", "Suara 02"], "top": "5%"},
                "xAxis": {"type": "value", "boundaryGap": [0, 0.01]},
                "yAxis": {"type": "category", "data": df_grouped['Kecamatan'].tolist()},
                "series": [
                    {
                        "name": "Suara 01",
                        "type": "bar",
                        "stack": "total",
                        "label": {"show": True, "position": "inside", "formatter": "{c}"},
                        "emphasis": {"focus": "series"},
                        "data": df_grouped['Suara 01'].tolist(),
                        "itemStyle": {"color": "#fac858"}
                    },
                    {
                        "name": "Suara 02",
                        "type": "bar",
                        "stack": "total",
                        "label": {"show": True, "position": "inside", "formatter": "{c}"},
                        "emphasis": {"focus": "series"},
                        "data": df_grouped['Suara 02'].tolist(),
                        "itemStyle": {"color": "#5470c6"}
                    },
                    {
                        "name": "Persentase TPS",
                        "type": "bar",
                        "stack": None,
                        "label": {
                            "show": True,
                            "position": "right",
                            "formatter": "{c}%"  # Format dalam persen
                        },
                        "data": df_grouped['Persentase TPS'].tolist(),
                        "itemStyle": {"color": "#91cc75"}  # Warna hijau untuk persentase TPS
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
