# train_model.py

import pandas as pd
from sklearn.svm import SVC
import joblib
import warnings

# Mengabaikan peringatan UserWarning dari scikit-learn tentang nama fitur
warnings.filterwarnings("ignore", category=UserWarning)

print("Memulai proses training model...")

# 1. Muat dataset dari file CSV
try:
    df = pd.read_csv('skintone_data.csv')
    print("Dataset 'skintone_data.csv' berhasil dimuat.")
except FileNotFoundError:
    print("Error: File 'skintone_data.csv' tidak ditemukan!")
    print("Pastikan Anda sudah membuat file tersebut sesuai instruksi.")
    exit()

# 2. Pisahkan fitur (X) dan target (y)
X = df[['B', 'G', 'R']] # Fitur adalah kolom warna B, G, R
y = df['label']        # Target adalah kolom label skintone

# 3. Inisialisasi dan latih model
# Kita menggunakan Support Vector Machine (SVC)
model = SVC(kernel='linear', probability=True)
model.fit(X, y)

print("Model berhasil dilatih.")

# 4. Simpan model yang sudah dilatih ke dalam file
# Ini akan membuat atau menimpa file skintone_classifier.pkl
joblib.dump(model, 'skintone_classifier.pkl')

print("======================================================")
print("SUCCESS: Model telah disimpan sebagai 'skintone_classifier.pkl'")
print("Anda sekarang bisa menjalankan aplikasi utama 'app.py'")
print("======================================================")