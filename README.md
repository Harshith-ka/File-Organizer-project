File Management & Organizing Simulator

A Python Flask-based web application that lets you upload, organize, rename, delete, and manage files effortlessly. The app automatically categorizes files by type and even extracts .zip files to organize their contents. Perfect for anyone looking to simulate a desktop-like file management experience in the browser.

🗂 Features

Upload files: Drag-and-drop or select multiple files for upload.

Automatic categorization: Files are organized into dedicated folders:

Documents (.pdf, .docx, .txt, .xlsx, .pptx)

Images (.jpg, .jpeg, .png, .gif, .bmp)

Music (.mp3, .wav, .m4a)

Videos (.mp4, .mkv, .avi, .mov)

Applications (.exe, .msi, .apk)

Compressed (.zip, .rar, .7z)

Others (any uncategorized files)

Automatic extraction: .zip files are extracted, and their contents are categorized.

Organize existing folders: Organize any folder on your system by providing its path.

Rename & Delete files: Easily rename or delete files directly from the UI.

Visual file dashboard: Browse files with a clean, responsive, card-style interface.

Download organized files: Zip the organized folder for easy downloading (optional).

🛠 Technology Stack

Backend: Python 3, Flask

Frontend: HTML, Tailwind CSS

Utilities: shutil, os, zipfile, werkzeug

File handling: Upload, move, rename, delete, extract

Project ScreenShot:-
ss.png

Install dependencies:

pip install flask werkzeug


Run the Flask app:

python app.py

sage

Upload files via the upload form.

Organize existing folder by entering the folder path.

Browse files in the dashboard; filter by category using the sidebar.

Rename or delete files using the icons on each file card.

Automatically handle zip files: uploaded zip files are extracted and categorized.

💡 Notes

Only .zip extraction is supported; .rar and .7z require additional libraries like pyunpack and patool.

Ensure the Flask app has read/write permissions to the specified folders.

Duplicate filenames are automatically renamed with a timestamp.

🎨 UI Preview


Clean, modern, card-based file browsing interface.

🔧 Future Enhancements

Support for other compressed formats (.rar, .7z).

Drag-and-drop file uploads directly from the desktop.

File search and sorting (by date, size, type).

User authentication to manage multiple users.

Download entire organized folder as a zip.

📄 License

This project is MIT licensed. Feel free to use, modify, and distribute.

