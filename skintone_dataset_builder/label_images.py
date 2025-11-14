import os
import io
import pandas as pd
from google.cloud import vision

# ==============================================================================
# KONFIGURASI PENTING - SESUAIKAN BAGIAN INI
# ==============================================================================

# 1. Atur Path ke File Kredensial JSON Anda
# Ganti dengan path lengkap ke file JSON yang Anda unduh dari Google Cloud.
# Contoh Windows: "C:\\Users\\windiwitari\\Downloads\\ai-makeup-project-xxxxxxxx.json"
# Contoh MacOS/Linux: "/Users/windiwitari/Downloads/ai-makeup-project-xxxxxxxx.json"
# PENTING: Gunakan double backslash (\\) untuk path di Windows.
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:\\Users\\windiwitari\\makeup_ai_app\\ai-skintone-bbba890b258f.json'

# 2. Definisikan folder input dan file output
INPUT_FOLDER = "raw_images"
OUTPUT_CSV_FILE = "skintone_data_otomatis.csv"

# ==============================================================================
# LOGIKA ATURAN (RULE ENGINE) - BAGIAN PALING EKSPERIMENTAL
# ==============================================================================

def get_skintone_label(r, g, b):
    """
    Fungsi ini adalah Rule Engine kita. Ia menerima nilai RGB dan mengembalikan
    salah satu dari 5 label skintone.
    ANDA PERLU MENYESUAIKAN NILAI-NILAI INI MELALUI BANYAK EKSPERIMEN.
    Nilai di bawah ini hanyalah titik awal.
    """
    if r >= 225 and g >= 220 and b >= 210:
        return 'fair'
    elif r >= 215 and g >= 195 and b >= 175:
        return 'light'
    elif r >= 190 and g >= 165 and b >= 140:
        return 'medium'
    elif r >= 150 and g >= 125 and b >= 105:
        return 'tan'
    else:
        # Semua nilai di bawah rentang 'tan' akan diklasifikasikan sebagai 'deep'
        return 'deep'

# ==============================================================================
# FUNGSI UTAMA - JANGAN UBAH BAGIAN INI
# ==============================================================================

def label_images_from_folder():
    """Fungsi utama untuk memproses semua gambar dan membuat file CSV."""
    
    # Inisialisasi klien Google Vision AI
    try:
        client = vision.ImageAnnotatorClient()
    except Exception as e:
        print("!!! KESALAHAN: Gagal menginisialisasi Google Vision Client.")
        print("Pastikan Anda sudah mengatur path kredensial dengan benar di variabel lingkungan.")
        print(f"Detail error: {e}")
        return

    # Pastikan folder input ada
    if not os.path.isdir(INPUT_FOLDER):
        print(f"!!! KESALAHAN: Folder '{INPUT_FOLDER}' tidak ditemukan.")
        print("Pastikan Anda sudah menjalankan skrip 'get_images.py' terlebih dahulu.")
        return

    # List untuk menampung hasil
    results_data = []

    # Dapatkan daftar semua file gambar di folder input
    image_files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    print(f"Ditemukan {len(image_files)} gambar. Memulai proses pelabelan...")

    # Loop untuk setiap file gambar
    for i, filename in enumerate(image_files):
        file_path = os.path.join(INPUT_FOLDER, filename)
        
        print(f"[{i+1}/{len(image_files)}] Memproses: {filename}...")
        
        try:
            # Baca file gambar
            with io.open(file_path, 'rb') as image_file:
                content = image_file.read()
            image = vision.Image(content=content)

            # Kirim permintaan ke Vision AI untuk mendeteksi properti gambar (termasuk warna dominan)
            response = client.image_properties(image=image)
            props = response.image_properties_annotation

            if response.error.message:
                print(f"  -> Error dari API: {response.error.message}")
                continue

            # Ambil warna dominan pertama dari hasil
            if props.dominant_colors.colors:
                dominant_color = props.dominant_colors.colors[0].color
                r = int(dominant_color.red)
                g = int(dominant_color.green)
                b = int(dominant_color.blue)
                
                # Gunakan Rule Engine kita untuk mendapatkan label skintone
                label = get_skintone_label(r, g, b)
                
                # Tambahkan hasil ke dalam list
                results_data.append({
                    "filename": filename,
                    "B": b,
                    "G": g,
                    "R": r,
                    "label": label
                })
                print(f"  -> Warna dominan: R={r}, G={g}, B={b} -> Label: {label}")
            else:
                print("  -> Tidak ada warna dominan terdeteksi.")

        except Exception as e:
            print(f"  -> Gagal memproses file: {e}")

    # Setelah semua gambar diproses, simpan hasilnya ke file CSV menggunakan Pandas
    if results_data:
        df = pd.DataFrame(results_data)
        
        # Hapus baris dengan label 'unknown' sebelum menyimpan ke CSV utama
        df_filtered = df[df.label != 'unknown']
        
        df_filtered.to_csv(OUTPUT_CSV_FILE, index=False, columns=["B", "G", "R", "label"])
        print(f"\n--- Proses Selesai ---")
        print(f"Dataset berhasil disimpan ke '{OUTPUT_CSV_FILE}'")
        print(f"Total gambar yang berhasil dilabeli (tidak termasuk 'unknown'): {len(df_filtered)}")
    else:
        print("\nTidak ada data yang berhasil diproses untuk disimpan.")


# Jalankan fungsi utama
if __name__ == "__main__":
    label_images_from_folder()
