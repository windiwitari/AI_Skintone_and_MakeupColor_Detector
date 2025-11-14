import cv2
import numpy as np
import mediapipe as mp

# Inisialisasi MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh

# Kamus untuk memetakan nama warna makeup ke nilai warna BGR (Blue, Green, Red)
# Ini adalah "database warna" kita. Anda bisa menyesuaikan warna-warna ini.
MAKEUP_COLORS = {
    # Lipstick
    "Nude Pink": (180, 180, 220),
    "Coral": (110, 120, 240),
    "Dusty Rose": (140, 125, 200),
    "Berry": (90, 30, 130),
    "Deep Red": (50, 50, 200),
    "Burgundy": (40, 40, 140),

    # Blush
    "Baby Pink": (220, 180, 245),
    "Light Peach": (180, 200, 240),
    "Mauve": (180, 150, 220),
    "Coral Orange": (120, 150, 250),
    "Deep Berry": (140, 90, 160)
}

# Indeks landmark dari MediaPipe untuk bibir bagian luar dan dalam
LIPS_OUTER_INDICES = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 321, 405, 314, 17, 84, 181, 91, 146]
LIPS_INNER_INDICES = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]

# Indeks landmark untuk area pipi
CHEEK_LEFT_INDICES = [117, 118, 119, 126, 135, 138, 147, 213]
CHEEK_RIGHT_INDICES = [346, 347, 348, 355, 364, 367, 376, 433]


def apply_lipstick(image, landmarks, color_name):
    """Menerapkan warna lipstik ke gambar."""
    # Ambil titik-titik koordinat untuk bibir luar dan dalam
    lip_points_outer = np.array([landmarks[i] for i in LIPS_OUTER_INDICES], dtype=np.int32)
    lip_points_inner = np.array([landmarks[i] for i in LIPS_INNER_INDICES], dtype=np.int32)

    # Buat sebuah lapisan overlay kosong
    overlay = image.copy()
    
    # Gambar poligon bibir pada lapisan overlay dengan warna yang dipilih
    cv2.fillPoly(overlay, [lip_points_outer], MAKEUP_COLORS.get(color_name, (0,0,0)))
    cv2.fillPoly(overlay, [lip_points_inner], MAKEUP_COLORS.get(color_name, (0,0,0)))

    # Blend overlay dengan gambar asli untuk efek transparan
    alpha = 0.6  # Tingkat transparansi (0.0 - 1.0)
    cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

def apply_blush(image, landmarks, color_name):
    """Menerapkan warna blush ke gambar."""
    # Ambil titik tengah untuk pipi kiri dan kanan
    cheek_left_center = np.mean([landmarks[i] for i in CHEEK_LEFT_INDICES], axis=0).astype(int)
    cheek_right_center = np.mean([landmarks[i] for i in CHEEK_RIGHT_INDICES], axis=0).astype(int)
    
    # Ukuran radius blush (sesuaikan jika perlu)
    radius = int(np.linalg.norm(landmarks[135] - landmarks[147]))

    # Buat lapisan overlay kosong
    overlay = image.copy()
    
    # Gambar lingkaran blush pada lapisan overlay
    cv2.circle(overlay, tuple(cheek_left_center), radius, MAKEUP_COLORS.get(color_name, (0,0,0)), -1)
    cv2.circle(overlay, tuple(cheek_right_center), radius, MAKEUP_COLORS.get(color_name, (0,0,0)), -1)
    
    # Berikan efek blur yang kuat untuk membuatnya terlihat natural
    blurred_overlay = cv2.GaussianBlur(overlay, (121, 121), 0)
    
    # Blend overlay yang sudah diblur dengan gambar asli
    alpha = 0.35 # Blush harus lebih transparan dari lipstik
    cv2.addWeighted(blurred_overlay, alpha, image, 1 - alpha, 0, image)


def apply_virtual_makeup(image, skintone_label, recommendations):
    """Fungsi utama untuk menerapkan semua jenis makeup."""
    h, w, _ = image.shape
    
    # Proses gambar dengan MediaPipe Face Mesh
    with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, min_detection_confidence=0.5) as face_mesh:
        results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        if not results.multi_face_landmarks:
            # Jika tidak ada wajah terdeteksi, kembalikan gambar asli
            return image
            
        # Konversi landmark ke koordinat piksel
        face_landmarks = results.multi_face_landmarks[0]
        landmarks = np.array([(int(point.x * w), int(point.y * h)) for point in face_landmarks.landmark])

        # --- TERAPKAN MAKEUP BERDASARKAN REKOMENDASI ---
        
        # 1. Terapkan Lipstik
        # Kita ambil rekomendasi pertama dari string, misal "Nude Pink, Coral, Light Red" -> "Nude Pink"
        lipstick_color_name = recommendations["lipstick"].split(',')[0].strip()
        apply_lipstick(image, landmarks, lipstick_color_name)
        
        # 2. Terapkan Blush
        blush_color_name = recommendations["blush"].split(',')[0].strip()
        apply_blush(image, landmarks, blush_color_name)

    # Kembalikan gambar yang sudah diberi makeup
    return image