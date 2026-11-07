# IF3070_G58_AssignedTeam3

Deskripsi dari Tugas Besar 1

Repositories ini berisi tentang program algoritma local search yang bertujuan untuk optimasi penempatan kendaraan dalam kapal.
## Struktur repositories ini terdiri dari
```
.
├── src/                       # Algoritma untuk menjalankan program
├── docs/                      # Laporan
├── output/                    # Hasil algoritma
└── README.md
```

## Persyaratan

- Python 3.9 atau lebih baru.
- Menjalankan algoritma memerlukan library tambahan bawaan python.
- Visualisasi memerlukan `matplotlib`.

## Cara Menjalankan Hill-climbing with Sideways Move

1. Clone repositori dan masuk ke folder `src`:
   ```bash
   git clone https://github.com/<username>/IF3070_GXX_NamaKelompok.git
   cd IF3070_GXX_NamaKelompok/src
   ```
   Seluruh perintah di bawah harus dijalankan dari folder `src`.

2. Jalankan algoritma:
   ```bash
   python hc_run.py
   ```
   Pada beberapa sistem, gunakan `python3`.

3. Program menjalankan algoritma dengan seed sesuai dengan yang dimasukkan. (di src, menggunakan seed 1, 3, dan 5 ,satu run per seed). Setiap run menghasilkan ringkasan hasil dari search yang dilakukan.

4. Visualisasi gambar state awal, state akhir, dan plot objective terhadap iterasi dapat dihasilkan dengan berikut:
   ```bash
   python visualize_hc.py
   ```

## Output Algoritma

Hasil disimpan di folder `output/`:

## Cara Kerja

Algoritma mulai dari state acak yang valid. Pada setiap iterasi, seluruh neighbor valid dievaluasi (tukar dua kendaraan, pindahkan kendaraan, ubah orientasi). Algoritma berpindah ke neighbor yang memiliki nilai terbaik:

- jika nilainya **lebih tinggi**, algoritma naik;
- jika nilainya **sama**, algoritma melakukan sideways move selama jumlah `max_sideways` berturut-turut belum habis;
- jika tidak ada yang lebih baik dan nilai `max_sideways` habis, search berhenti.

Jika beberapa neighbor terbaik bernilai sama, salah satunya dipilih secara acak.

Anggota Kelompok:
Padmanabha Adyaksa (18222142)
Zafran Abqary Faisal (18225084)
Fawwaz Aydin Mustofa (18222109)

