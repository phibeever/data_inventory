import json
import os
import streamlit as st
from PIL import Image
import zxingcpp

FILE_DATABASE = "inventaris_data.json"

st.set_page_config(
    page_title="Inventaris Barang",
    page_icon="📦",
    layout="wide"
)

def load_data():
    if os.path.exists(FILE_DATABASE):
        try:
            with open(FILE_DATABASE, "r") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
    return {
        "8999999001": {"nama": "Kopi Sachet Instant", "stok": 50, "harga": 3000},
        "BRG1002": {"nama": "Air Mineral 600ml", "stok": 100, "harga": 4000}
    }

def save_data(data):
    try:
        with open(FILE_DATABASE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        st.error(f"Gagal menyimpan data: {e}")

# MENSYARATKAN STRICT DICTIONARY DENGAN KEAMANAN TINGGI
if "items" not in st.session_state or not isinstance(st.session_state.items, dict):
    st.session_state["items"] = load_data()

if "scanned_code" not in st.session_state:
    st.session_state["scanned_code"] = ""

st.title("📦 Sistem Inventaris Barang Web")
st.caption("Aplikasi Web Inventaris - Kompatibel dengan Laptop dan HP")

st.divider()

# --- MODUL PEMINDAI BARCODE KAMERA ---
with st.expander("📷 **Buka Scanner Barcode / QR Code Kamera**", expanded=False):
    st.write("Ambil foto barcode barang menggunakan kamera HP / Komputer Anda:")
    img_file = st.camera_input("Ambil Foto Barcode")
    
    if img_file is not None:
        try:
            image = Image.open(img_file)
            results = zxingcpp.read_barcodes(image)
            
            if results:
                found_code = results[0].text
                st.session_state["scanned_code"] = found_code
                st.success(f"✅ Barcode Terdeteksi: **{found_code}**")
            else:
                st.warning("⚠️ Barcode tidak terdeteksi pada foto. Pastikan posisi barcode jelas dan terang.")
        except Exception as e:
            st.error(f"Gagal memproses gambar: {e}")

# --- FORM INPUT DATA BARANG ---
st.subheader("📝 Form Input / Edit Barang")

default_kode = st.session_state.get("scanned_code", "")

col1, col2 = st.columns(2)

with col1:
    kode_input = st.text_input("Kode Barang / Barcode", value=default_kode)
    nama_input = st.text_input("Nama Barang")

with col2:
    stok_input = st.number_input("Jumlah Stok", min_value=0, step=1, value=0)
    harga_input = st.number_input("Harga Barang (Rp)", min_value=0, step=500, value=0)

# Ambil dictionary items dengan aman
current_items = st.session_state.get("items", {})
if not isinstance(current_items, dict):
    current_items = {}
    st.session_state["items"] = current_items

# Cek apakah kode barang sudah terdaftar
if kode_input and kode_input in current_items:
    item_exist = current_items[kode_input]
    if isinstance(item_exist, dict):
        st.info(f"💡 Kode terdaftar: **{item_exist.get('nama', '')}** | Stok: {item_exist.get('stok', 0)} | Harga: Rp {item_exist.get('harga', 0):,}")

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("💾 Simpan / Update Barang", type="primary", use_container_width=True):
        if not kode_input or not nama_input:
            st.error("Kode dan Nama Barang wajib diisi!")
        else:
            if not isinstance(st.session_state.get("items"), dict):
                st.session_state["items"] = {}
                
            st.session_state["items"][kode_input] = {
                "nama": nama_input,
                "stok": int(stok_input),
                "harga": int(harga_input)
            }
            save_data(st.session_state["items"])
            st.success(f"Barang '{nama_input}' berhasil disimpan!")
            st.rerun()

with col_btn2:
    if st.button("🗑️ Hapus Barang", type="secondary", use_container_width=True):
        items_dict = st.session_state.get("items", {})
        if isinstance(items_dict, dict) and kode_input in items_dict:
            nama_del = items_dict[kode_input].get("nama", "Barang")
            del st.session_state["items"][kode_input]
            save_data(st.session_state["items"])
            st.warning(f"Barang '{nama_del}' berhasil dihapus.")
            st.rerun()
        else:
            st.error("Kode barang tidak ditemukan di database.")

st.divider()

# --- TABEL DATA INVENTARIS ---
st.subheader("📊 Daftar Stok Barang")

display_items = st.session_state.get("items", {})
if isinstance(display_items, dict) and display_items:
    table_data = []
    for kode, data in display_items.items():
        if isinstance(data, dict):
            table_data.append({
                "Kode Barcode": kode,
                "Nama Barang": data.get("nama", "-"),
                "Stok": data.get("stok", 0),
                "Harga (Rp)": f"Rp {data.get('harga', 0):,}"
            })
    
    st.dataframe(table_data, use_container_width=True)
else:
    st.info("Belum ada data barang disimpan.")
