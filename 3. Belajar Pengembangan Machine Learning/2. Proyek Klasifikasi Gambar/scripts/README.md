# Dokumentasi File Script

Ini adalah dokumentasi yang menjelaskan tentang fungsi setiap file script yang ada di sini.

> [!IMPORTANT]
> Dokumentasi folder di proyek ini bisa ditemukan [disini](../README.md).

## `count-dataset.py`

Script untuk menghitung dataset yang telah dikumpulkan di folder `../datasets`. Script ini juga memberikan daftar folder yang belum memenuhi batas minimum dataset yang diperlukan. Script ini akan menghasilkan file `../total-datasets.json` yang berisi daftar dataset di setiap folder.

```python
total_file = 0
target     = 300
```

- `total_file`: Total dataset yang telah dikumpulkan.
- `target`: Batas minimum dataset yang diperlukan di satu folder.

## `reduce-dataset.py`

Script untuk mengurangi jumlah dataset yang didapat di setiap folder di folder `../datasets`.

```python
folders  = os.listdir('../datasets')
max_item = 400
```

- `folders`: Daftar folder yang akan diperiksa.
- `max_item`: Jumlah maksimum dataset di setiap folder.

## `remove-duplicated-dataset.py`

Script untuk menghapus dataset yang duplikat di setiap folder di folder `../datasets`.

```python
folders = os.listdir('../datasets')
```

- `folders`: Daftar folder yang akan diperiksa.

## `scrape-dataset.py`

Script untuk melakukan pencarian dataset di internet menggunakan program chrome driver. Script ini menggunakan program chrome driver dari folder `../chromedriver-win64`, menggunakan daftar kategori yang akan dicari dari file `../remaining-datasets.json`, dan menyimpan hasilnya di folder `../datasets`.

```python
scrape_id = 2

queries = [
   'bunga {name}'
]

sites = [
   {
      'name'       : 'google',
      'url'        : 'https://www.google.com/search?q={query}&tbm=isch&as_filetype=jpg&tbs=sur:fmc&udm=2',
      'selector'   : 'img.YQ4gaf:not(.zr758c)',
      'pagination' : False,
      'pages'      : 4,
      'amount'     : 40,
   }
]
```

- `scrape_id`: Id unik yang digunakan untuk nama file dataset untuk menghindari nama yang sama setiap kali menjalankan script ini.
- `queries`: Daftar query yang akan digunakan. Setiap query dapat memiliki placeholder `{name}` yang akan diubah menjadi nama kategori dari daftar kategori yang akan dicari.
- `sites`: Daftar situs yang akan digunakan untuk pencarian.

## `split-dataset.py`

Script untuk memisahkan dataset menjadi 3 bagian (folder), yaitu `train`, `validation`, dan `test`. Script ini menggunakan folder `../model-datasets` untuk menyimpan dataset yang sudah dipisahkan menjadi 3 bagian sebelumnya.

```python
folders     = os.listdir('../datasets')

split_ratio = {
   'train'      : .8,
   'validation' : .1,
   'test'       : .1
}
```

- `folders`: Daftar folder yang akan diperiksa.
- `split_ratio`: Rasio yang akan digunakan untuk pemisahan dataset.