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
RANGE = "Sheet3!A1:K1000"  # Sesuaikan jangkauan untuk menyertakan kolom K

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

        # Standarisasi kolom 'Kecamatan' untuk menghindari duplikasi akibat spasi atau kapitalisasi
        df['Kecamatan'] = df['Kecamatan'].str.strip().str.title()

        # Konversi kolom numerik
        df['Suara 01'] = pd.to_numeric(df['Suara 01'], errors='coerce').fillna(0)
        df['Suara 02'] = pd.to_numeric(df['Suara 02'], errors='coerce').fillna(0)
        df['Suara Tidak Sah'] = pd.to_numeric(df['Suara Tidak Sah'], errors='coerce').fillna(0)
        
        # Memastikan kolom 'DPT' diakses dengan benar
        if 'DPT' in df.columns:
            df['DPT'] = pd.to_numeric(df['DPT'], errors='coerce').fillna(0)
        else:
            st.write("Kolom 'DPT' tidak ditemukan dalam data.")

        # Filter out any rows where 'Kecamatan' might contain unintended header or invalid data
        df = df[df['Kecamatan'] != 'Kecamatan']

        # Mengelompokkan data berdasarkan kecamatan dan menjumlahkan nilai suara
        df_grouped = df.groupby('Kecamatan', as_index=False).agg({
            'Suara 01': 'sum',
            'Suara 02': 'sum'
        })

        # Hitung total perolehan Suara 01 dan Suara 02
        total_suara_01 = int(df_grouped['Suara 01'].sum())
        total_suara_02 = int(df_grouped['Suara 02'].sum())

        # Layout untuk menampilkan chart dan gambar berdampingan
        col_chart, col_image1, col_image2 = st.columns([2, 1, 1])

        # Chart 2: Total Perolehan Suara 01 dan Suara 02 dalam bentuk Pie Chart
        with col_chart:
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
                            {
                                "value": total_suara_01,
                                "name": "Suara 01",
                                "itemStyle": {"color": "#fac858"},
                                "label": {
                                    "show": True,
                                    "formatter": "{b}: {c}"
                                }
                            },
                            {
                                "value": total_suara_02,
                                "name": "Suara 02",
                                "itemStyle": {"color": "#5470c6"},
                                "label": {
                                    "show": True,
                                    "formatter": "{b}: {c}"
                                }
                            }
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

        # Display images of candidates in adjacent columns with circular style
        with col_image1:
            st.markdown(
                """
                <div style="display: flex; align-items: center; justify-content: center;">
                    <img src="ky.png" alt="Kandidat Suara 01" style="border-radius: 50%; width: 150px; height: 150px;">
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_image2:
            st.markdown(
                """
                <div style="display: flex; align-items: center; justify-content: center;">
                    <img src="amboy.png" alt="Kandidat Suara 02" style="border-radius: 50%; width: 150px; height: 150px;">
                </div>
                """,
                unsafe_allow_html=True
            )

    else:
        st.write("Tidak ada data yang ditemukan.")
else:
    st.write(f"Error: {response.status_code}, {response.text}")

# Footer
st.markdown("""
    Dikembangkan oleh [Cucu Anduang](https://scholar.google.com/citations?user=RUg3RQUAAAAJ&hl=id&oi=ao), Untuk korespondensi hubungi duckblurry-royal-coma@duck.com
""", unsafe_allow_html=True)
