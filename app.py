import os
from flask import Flask, request, render_template, redirect, url_for
import cv2
import joblib
import numpy as np
from werkzeug.utils import secure_filename
import shutil

# Impor dari file lain
from makeup_recommendations import RECOMMENDATIONS
# Hapus impor fungsi lama jika ada, kita akan memanggil modul baru
# from feature_extractor import extract_skin_color <- (Hapus jika ada)

# --- IMPOR MODUL BARU KITA ---
from virtual_makeup import apply_virtual_makeup

app = Flask(__name__)

# Konfigurasi folder (disesuaikan agar lebih robust)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
# Folder untuk menyimpan gambar final yang akan ditampilkan ke user
app.config['STATIC_UPLOADS'] = os.path.join(BASE_DIR, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Pastikan semua folder ada
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['STATIC_UPLOADS'], exist_ok=True)

# Muat model klasifikasi skintone
try:
    skintone_model = joblib.load('skintone_classifier.pkl')
except FileNotFoundError:
    print("Error: File 'skintone_classifier.pkl' tidak ditemukan. Latih model terlebih dahulu.")
    skintone_model = None

# Fungsi ekstraksi fitur warna kulit (diletakkan di sini agar mandiri)
import mediapipe as mp
mp_face_mesh_extractor = mp.solutions.face_mesh
def extract_skin_color(image_path):
    image = cv2.imread(image_path)
    with mp_face_mesh_extractor.FaceMesh(static_image_mode=True, max_num_faces=1, min_detection_confidence=0.5) as face_mesh:
        results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if not results.multi_face_landmarks:
            return None
        
        cheek_forehead_indices = [10, 338, 297, 332, 284, 295, 288, 97, 326, 317, 234, 127, 162, 21, 54, 103, 67, 109, 454, 356, 389, 251]
        
        h, w, _ = image.shape
        skin_pixels = []
        for landmark in results.multi_face_landmarks:
            for idx in cheek_forehead_indices:
                point = landmark.landmark[idx]
                x, y = int(point.x * w), int(point.y * h)
                if 0 <= x < w and 0 <= y < h:
                    skin_pixels.append(image[y, x])

        if not skin_pixels: return None
        return np.mean(skin_pixels, axis=0).astype(int)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files or request.files['file'].filename == '':
            return redirect(request.url)
        
        file = request.files['file']
        if file and skintone_model:
            filename = secure_filename(file.filename)
            upload_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_filepath)

            # --- ALUR KERJA UTAMA ---
            
            # 1. Ekstraksi Fitur Warna Kulit
            avg_color = extract_skin_color(upload_filepath)
            if avg_color is None:
                os.remove(upload_filepath)
                return render_template('index.html', error="Wajah tidak dapat terdeteksi pada gambar.")
                
            # 2. Prediksi Skintone
            skin_features = np.array([avg_color])
            predicted_skintone = skintone_model.predict(skin_features)[0]

            # 3. Dapatkan Rekomendasi
            recommendations = RECOMMENDATIONS.get(predicted_skintone)

            # 4. TERAPKAN MAKEUP VIRTUAL (LANGKAH BARU)
            # Baca gambar lagi untuk diterapkan makeup
            image_to_process = cv2.imread(upload_filepath)
            output_image = apply_virtual_makeup(image_to_process, predicted_skintone, recommendations)
            
            # 5. Simpan gambar HASIL ke folder static
            output_filename = 'result_' + filename
            output_filepath = os.path.join(app.config['STATIC_UPLOADS'], output_filename)
            cv2.imwrite(output_filepath, output_image)
            
            # 6. Kirim hasil ke template
            return render_template('result.html', 
                                   skintone=predicted_skintone.capitalize(),
                                   recommendations=recommendations,
                                   image_file=output_filename) # Kirim nama file HASIL

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
