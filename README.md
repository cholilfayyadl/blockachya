
# Blockachya

Blockachya adalah aplikasi web yang memungkinkan pengguna untuk melakukan transaksi koin, top-up, melihat mutasi transaksi, dan mengelola profil mereka. Aplikasi ini dibangun menggunakan Flask, MongoDB, dan Bootstrap 5.

## Fitur Utama
- **Registrasi & Login:** Pengguna dapat mendaftar dan masuk menggunakan email.
- **Dashboard:** Menampilkan informasi koin yang dimiliki dan akses ke fitur lainnya.
- **Transfer Koin:** Memungkinkan pengguna untuk mentransfer koin ke pengguna lain.
- **Mutasi Transaksi:** Menampilkan riwayat transaksi berdasarkan filter (harian, bulanan, tahunan, atau custom).
- **Top-Up Koin:** Mengajukan permintaan top-up koin.
- **Edit Profil:** Mengelola data profil pengguna.

## Teknologi yang Digunakan
- **Backend:** Flask (Python)
- **Database:** MongoDB Atlas
- **Frontend:** Bootstrap 5
- **Authentication:** Flask-Login dan Flask-Bcrypt

## Instalasi dan Pengaturan
Ikuti langkah-langkah berikut untuk menjalankan aplikasi ini secara lokal:

### 1. Pastikan Prasyarat Terinstal
- **Python 3.8 atau lebih baru**
- **Pip** (termasuk dalam instalasi Python)
- **Git**
- **MongoDB Atlas Account** (atau server MongoDB lokal)

### 2. Clone Repository
```bash
git clone https://github.com/username/blockachya.git
cd blockachya
```

### 3. Buat Virtual Environment
Buat lingkungan virtual untuk mengelola dependensi aplikasi:
```bash
python -m venv venv
```

Aktifkan lingkungan virtual:
- Untuk **Linux/Mac**:
  ```bash
  source venv/bin/activate
  ```
- Untuk **Windows**:
  ```bash
  venv\Scripts\activate
  ```

### 4. Install Dependensi
```bash
pip install -r requirements.txt
```

### 5. Konfigurasi Environment Variables
Buat file `.env` di direktori utama proyek dan tambahkan konfigurasi berikut:
```env
SECRET_KEY=your_secret_key   # Ganti dengan kunci rahasia Anda
MONGO_URI=your_mongodb_atlas_uri   # URI MongoDB Anda
```

**Contoh SECRET_KEY dan MONGO_URI**:
- `SECRET_KEY`: Anda bisa menggunakan string acak panjang. Contoh: `my_super_secret_key_123!`.
- `MONGO_URI`: Dapatkan URI dari [MongoDB Atlas](https://www.mongodb.com/atlas/database).

### 6. Jalankan Aplikasi
Setelah konfigurasi selesai, jalankan aplikasi:
```bash
flask run
```

Aplikasi akan tersedia di: `http://127.0.0.1:5000`.

## Struktur Direktori
```
blockachya/
├── templates/            # File HTML
├── static/               # File CSS, JS, dan assets lainnya
├── app.py                # Entry point aplikasi Flask
├── requirements.txt      # Dependensi Python
└── README.md             # Dokumentasi proyek
```

## Screenshot Aplikasi
### 1. Halaman Dashboard
Tampilan dashboard dengan informasi saldo koin dan navigasi ke fitur lain.

![Dashboard Screenshot](https://github.com/cholilfayyadl/blockachya/blob/main/static/img/dashboard.png)

### 2. Halaman Transfer
Form untuk transfer koin ke pengguna lain.

![Transfer Screenshot](https://via.placeholder.com/800x400)

## Kontribusi
Kontribusi sangat dihargai! Jika Anda ingin berkontribusi, fork repository ini, buat branch fitur baru, dan kirim pull request.

1. Fork repository ini
2. Buat branch fitur baru
   ```bash
   git checkout -b fitur-baru
   ```
3. Commit perubahan Anda
   ```bash
   git commit -m "Menambahkan fitur baru"
   ```
4. Push ke branch Anda
   ```bash
   git push origin fitur-baru
   ```
5. Buat pull request

## Lisensi
Proyek ini dilisensikan di bawah lisensi MIT. Silakan baca file `LICENSE` untuk detailnya.
