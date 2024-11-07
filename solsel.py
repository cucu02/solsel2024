import streamlit as st
import pandas as pd
import requests
from streamlit_echarts import st_echarts

# ID dari Google Sheets dan API Key
SHEET_ID = "11VpCK1BHH74-LOL6dMT8g4W28c_a9Ialf-Gu2CLAfSo"
API_KEY = "AIzaSyD48O12Pwu9KE3o9Gl0YO1JM0hSUiwR3k8"
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
        df['Suara 01'] = pd.to_numeric(df['Suara 01'], errors='coerce')
        df['Suara 02'] = pd.to_numeric(df['Suara 02'], errors='coerce')
        df['Suara Sah'] = pd.to_numeric(df['Suara Sah'], errors='coerce')
        df['Suara Tidak Sah'] = pd.to_numeric(df['Suara Tidak Sah'], errors='coerce')

        # Mengelompokkan data berdasarkan kecamatan dan menjumlahkan nilai suara
        df_grouped = df.groupby('Kecamatan', as_index=False).agg({
            'Suara 01': 'sum',
            'Suara 02': 'sum'
        })

        # Hitung total perolehan Suara 01, Suara 02, dan Jumlah Suara tidak sah
        total_suara_01 = int(df_grouped['Suara 01'].sum())  # Konversi ke int untuk kompatibilitas JSON
        total_suara_02 = int(df_grouped['Suara 02'].sum())  # Konversi ke int untuk kompatibilitas JSON
        total_suara_tidak_sah = int(df['Suara Tidak Sah'].sum())  # Konversi ke int untuk kompatibilitas JSON

        # Hitung jumlah TPS terisi dan belum terisi berdasarkan jumlah baris di kolom Nomor TPS
        tps_terisi = int(df['Nomor TPS'].count())  # Menghitung jumlah baris yang terisi
        jumlah_tps = 347  # Total TPS (nilai tetap)
        tps_belum_terisi = jumlah_tps - tps_terisi  # TPS yang belum terisi

        # Mulai dashboard
        st.set_page_config(layout="wide", page_title="Quick Count Pilkada Solsel 2024", page_icon="🗳️")
        st.title("Quick Count Pilkada Solsel 2024")

        # Hitung data penting
        jumlah_kecamatan = len(df_grouped)  # Hitung jumlah kecamatan setelah pengelompokan
        jumlah_nagari = 39
        total_dpt = 127858  # Total jumlah DPT sebagai nilai tetap

        # Metrics Layout
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Jumlah Kecamatan", jumlah_kecamatan)
        with col2:
            st.metric("Jumlah Nagari", jumlah_nagari)
        with col3:
            st.metric("Jumlah TPS", jumlah_tps)

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

        # Chart 1: Perolehan Suara 01 dan Suara 02 per Kecamatan dalam bentuk Bar Race dengan Legend
        with col_chart1:
            st.subheader("Perolehan Suara Paslon")
            
            option_bar_race = {
                "legend": {
                    "data": ["Perolehan Suara 01", "Perolehan Suara 02"],
                    "top": "5%"
                },
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {
                        "type": "shadow"
                    }
                },
                "xAxis": {
                    "type": "value"
                },
                "yAxis": {
                    "type": "category",
                    "data": df_grouped['Kecamatan'].tolist()
                },
                "series": [
                    {
                        "name": "Perolehan Suara 01",
                        "type": "bar",
                        "data": df_grouped['Suara 01'].astype(int).tolist(),
                        "label": {
                            "show": True,
                            "position": "right",
                            "valueAnimation": True
                        },
                        "itemStyle": {
                            "color": "#fac858"
                        }
                    },
                    {
                        "name": "Perolehan Suara 02",
                        "type": "bar",
                        "data": df_grouped['Suara 02'].astype(int).tolist(),
                        "label": {
                            "show": True,
                            "position": "right",
                            "valueAnimation": True
                        },
                        "itemStyle": {
                            "color": "#5470c6"
                        }
                    }
                ],
                "animationDuration": 4000,
                "animationDurationUpdate": 3000,
                "animationEasing": "linear",
                "animationEasingUpdate": "linear"
            }

            st_echarts(options=option_bar_race, height="600px")

        # Chart 2: Total Perolehan Suara 01 dan Suara 02 dalam bentuk Pie Chart
        with col_chart2:
            st.subheader("Total Perolehan Suara Paslon")
            
            option_pie_chart = {
                "tooltip": {
                    "trigger": "item"
                },
                "legend": {
                    "top": "5%",
                    "left": "center"
                },
                "series": [
                    {
                        "name": "Total Perolehan Suara",
                        "type": "pie",
                        "radius": "50%",
                        "data": [
                            {"value": total_suara_01, "name": "Suara 01"},
                            {"value": total_suara_02, "name": "Suara 02"}
                        ],
                        "emphasis": {
                            "label": {
                                "show": True,
                                "fontSize": "20",
                                "fontWeight": "bold"
                            }
                        }
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
    Dikembangkan oleh [Cucu Anduang](https://scholar.google.com/citations?user=RUg3RQUAAAAJ&hl=id&oi=ao), Untuk korespondensi hubungi duckblurry-royal-coma@duck.com
""", unsafe_allow_html=True)
