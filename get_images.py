import requests  # Untuk membuat permintaan HTTP ke API
import os        # Untuk membuat folder dan mengelola path file

# ==============================================================================
# KONFIGURASI PENTING - SESUAIKAN BAGIAN INI
# ==============================================================================

# 1. Masukkan Kunci API Pexels Anda di sini
# Ganti "MASUKKAN_KUNCI_API_PEXELS_ANDA_DI_SINI" dengan kunci yang Anda dapatkan.
API_KEY = "9cMOewBJcmPVL8C7XVIfAxfC0yj3QtgnHc67kQJfbdgto5cEU5LD6UK2"

# 2. Definisikan kata kunci pencarian (queries)
# Kata kunci ini dibuat lebih spesifik untuk mengumpulkan data wajah perempuan
# dari berbagai etnis, usia, dan kondisi pencahayaan.
SEARCH_QUERIES = [
    # Spesifik Usia & Umum
    "woman face portrait",
    "beautiful woman close up",
    "teenager girl portrait",
    "middle-aged woman face",
    "elderly woman portrait",

    # Spesifik Etnis
    "asian woman portrait",
    "indonesian woman face",
    "african woman portrait",
    "caucasian woman portrait",
    "indian woman face",
    "hispanic woman portrait",
    "middle eastern woman face",

    # Spesifik Warna Kulit & Fitur
    "woman with fair skin portrait",
    "woman with olive skin",
    "woman with dark skin portrait",
    "woman with freckles face",

    # Spesifik Konteks & Pencahayaan
    "woman natural light portrait",
    "woman studio lighting face",
    "woman neutral expression",
    "woman smiling face"
]

# 3. Definisikan jumlah gambar per kata kunci dan folder output
# Pexels API biasanya mengembalikan maksimal 80 gambar per query.
# Kita akan mengambil 80 gambar (1 halaman) per kata kunci.
IMAGES_PER_QUERY = 20
OUTPUT_FOLDER = "raw_images"

def download_images():
    """Fungsi utama untuk mencari dan mengunduh gambar."""

    # Cek apakah Kunci API sudah dimasukkan
    # if API_KEY == "9cMOewBJcmPVL8C7XVIfAxfC0yj3QtgnHc67kQJfbdgto5cEU5LD6UK2":
    #     print("!!! KESALAHAN: Harap masukkan Kunci API Pexels Anda di variabel API_KEY.")
    #     return

    # Buat folder output jika belum ada
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"Folder '{OUTPUT_FOLDER}' berhasil dibuat.")

    # Siapkan header untuk permintaan API, ini wajib untuk otorisasi
    headers = {
        "Authorization": API_KEY
    }

    total_downloaded = 0
    # Loop untuk setiap kata kunci yang telah kita definisikan
    for query in SEARCH_QUERIES:
        print(f"\n--- Memulai pencarian untuk kata kunci: '{query}' ---")
        
        # Siapkan parameter untuk permintaan GET
        params = {
            "query": query,
            "per_page": IMAGES_PER_QUERY,
            "page": 1  # Kita ambil halaman pertama saja
        }
        
        # Lakukan permintaan ke Pexels API
        try:
            response = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params)
            # Cek jika ada error dari server (misal: 404, 500)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Gagal melakukan permintaan API: {e}")
            continue # Lanjut ke kata kunci berikutnya

        # Ubah respons dari API (dalam format JSON) menjadi dictionary Python
        data = response.json()

        # Cek jika tidak ada foto yang ditemukan untuk query ini
        if not data.get("photos"):
            print("Tidak ada foto ditemukan untuk kata kunci ini.")
            continue

        # Loop untuk setiap foto yang ditemukan dalam respons
        for photo in data["photos"]:
            # Dapatkan URL gambar dalam kualitas original
            image_url = photo["src"]["original"]
            
            # Buat nama file yang unik berdasarkan ID foto
            file_name = f"pexels_{photo['id']}.jpg"
            file_path = os.path.join(OUTPUT_FOLDER, file_name)

            # Cek apakah file sudah pernah diunduh sebelumnya untuk menghindari duplikat
            if os.path.exists(file_path):
                print(f"File {file_name} sudah ada, melewati...")
                continue

            # Unduh gambar dari URL
            try:
                print(f"Mengunduh {image_url} -> {file_name}")
                image_response = requests.get(image_url, stream=True, timeout=10)
                image_response.raise_for_status()
                
                # Tulis data gambar ke dalam file di komputer Anda
                with open(file_path, "wb") as f:
                    for chunk in image_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                total_downloaded += 1

            except requests.exceptions.RequestException as e:
                print(f"Gagal mengunduh gambar {image_url}: {e}")

    print(f"\n--- Proses Selesai ---")
    print(f"Total gambar yang berhasil diunduh: {total_downloaded}")


# Jalankan fungsi utama saat skrip dieksekusi
if __name__ == "__main__":
    download_images()
