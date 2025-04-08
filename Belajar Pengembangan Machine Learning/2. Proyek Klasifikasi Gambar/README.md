# Dokumentasi Proyek Klasifikasi Gambar

Ini adalah dokumentasi yang menjelaskan tentang fungsi setiap folder yang ada di sini.

Kebetulan saya juga mengerjakan proyek capstone untuk coding camp dengan tema klasifikasi bunga, sama dengan proyek submission ini. Saya mennggunakan beberapa aset yang sudah saya buat di proyek capstone sebelumnya, seperti script, dataset, serta dokumentasinya.

Jika reviewer penasaran dengan proyek saya, bisa diakses di github [Flower-Classification-Website](https://github.com/Ar-Syhptra/Flower-Classification-Website), terutama di branch `ml`.

Jika reviewer curiga apakah kodenya dibantu orang lain, untuk sekarang ini proyek capstone bagian machine learning hanya saya yang mengerjakannya, teman saya belum membantu, bisa dilihat dari riwayat commitnya di github pada branch `ml`.

> Dataset saya kumpulkan dengan menggunakan selenium secara otomatis, kaggle, serta Flower 102. Karena itulah ada beberapa nama file yang berbeda.

## `chromedriver-win64`

Folder yang berisi program chrome driver yang digunakan untuk mengumpulkan data melalui browser chrome. Program chrome driver ini digunakan oleh script `scrape-dataset.py`.

> Program chromedriver memiliki versi 134.0.6998.165 untuk sistem operasi windows.

## `datasets`

Folder yang berisi dataset yang telah didapatkan dari pengumpulan data yang dikelompokkan berdasarkan kategori. Folder ini digunakan oleh script `scrape-dataset.py`, `reduce-dataset.py`, dan `remove-duplicated-dataset.py`.

> Dataset dibagikan di cloud MEGA untuk mengoptimalkan repository ini yang bisa diakses di [Flower-Classification-Website/datasets](https://mega.nz/folder/MlgGRL4K#hikilKZ0F1gXoWCzvKkxcA/folder/plAz2ZjR).
> Kelas yang digunakan hanyalah 5, dapat dilihat di [`total-datasets.json`](./total-datasets.json).

```
datasets/
└── {kategori}/
    └── {dataset}
```

## `model-datasets`

Folder yang digunakan untuk tempat dataset yang telah dipisah menjadi 3 bagian untuk keperluan pembuatan model deep learning. Folder ini digunakan oleh script `split-dataset.py`.

> Dataset yang telah dipisah dibagikan di cloud Google Drive untuk mengoptimalkan repository ini yang bisa diakses di [model-datasets.zip](https://drive.google.com/file/d/1LzGsFkr70xCbA9EdTXF4o03hAinJ2RU7/view?usp=sharing).

```
model-datasets/
├── train/
|   └── {kategori}/
|       └── {dataset}
├── validation/
|   └── {kategori}/
|       └── {dataset}
└── test/
    └── {kategori}/
        └── {dataset}
```

- `train/`: Folder yang berisi dataset untuk melatih model.
- `train/`: Folder yang berisi dataset untuk validasi model.
- `test/`: Folder yang berisi dataset untuk menguji model.

## `models`

Folder yang berisi model machine learning yang sudah dilatih dan disimpan dalam berbagai bentuk.

> Model yang telah disimpan dibagikan di cloud MEGA untuk mengoptimalkan repository ini yang bisa diakses di [models.zip](https://mega.nz/file/opRi0S5T#fPaDaG5ElBK7U6IXA40kQKC4JJuYcGU2kbhFwDBeg1c).

```
models/
├── model.h5
├── saved_model/
|   └── ...
├── tfjs_model/
|   └── ...
└── tflite_model/
    └── ...
```

- `saved_model/`: Folder model yang disimpan dalam format saved model.
- `tfjs_model/`: Folder model yang disimpan dalam format tensorflowjs untuk dapat digunakan di browser dengan menggunakan TensorFlow.js.
- `tflite_model/`: Folder model yang disimpan dalam format tflite untuk dapat digunakan di perangkat mobile dengan menggunakan LiteRT. 

## `scripts`

Folder yang berisi script yang berkaitan dengan semua hal yang ada disini mulai dari mengumpulkan data, mengolah data, dan sebagainya.

> Dokumentasi file pada folder `scripts` bisa ditemukan [scripts/README.md](scripts/README.md).