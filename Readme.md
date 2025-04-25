# 📥 Mangaita.io Downloader

**Mangaita.io Downloader** is a tool written in pure Python that allows you to download manga from [Mangaita](https://mangaita.io/).  
With this tool, you can download a single chapter, a range of chapters, or the entire manga.

## 🚀 Installation

### 1️⃣ Requirements

Make sure you have installed:
- [Python](https://www.python.org/) (>=3.x)
- [Git](https://git-scm.com/)

### 2️⃣ Clone the repository

```sh
git clone https://github.com/TheMrZenith/Mangaita.io-Downloader/
```

### 3️⃣ Navigate to the project directory
```
cd Mangaita.io-Downloader
```

### 4️⃣ Run the main script
```
python main.py
```

### 5️⃣ Follow the menu instructions to choose what you want to download or customize the program

### ⚙️ Functionality
### ⚙️ Functionality
✅ Download single chapter  
✅ Download range of chapters  
✅ Download entire manga  
✅ Save chapters in folders  
✅ Create PDF (optional)  
✅ Create "Manga" and "Scan" folders (optional)  
✅ Save to custom paths (optional)  

### 🔜 Coming Soon Functionality
⏳ GUI version  
⏳ different output formats

### 🛠️ Configurations

The **config.json** file allows you to customize some settings, such as:
- **`latest_first`**: If set to `true`, the downloader will prioritize downloading the latest chapters first.  
- **`create_pdf`**: If set to `true`, the downloader will generate a PDF file for each downloaded chapter.  
- **`download_type`**: Determines the download method. If set to `async`, the downloader will download multiple pages concurrently, speeding up the process.

### 📝 License

This project is distributed under the **MIT** license. For more details, see the file [LICENSE](https://github.com/TheMrZenith/Mangaita.io-Dowloader/blob/main/LICENSE)
