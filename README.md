# Echo

This Flask application allows users to upload, convert, manage, and download music files. It features a YouTube-to-MP3 converter, file uploading with metadata extraction, music file management, and statistical insights into the music library.

## Features

- **YouTube to MP3 Conversion**: Convert YouTube videos to MP3 format and store them in the app's library.
- **File upload**: Upload music files (MP3, WAV, OGG) directly from your device.
- **Metadata extraction**: Automatically extract and save metadata (title, artist, album, duration, etc.) from uploaded files.
- **Music library management**: List, download, edit, and delete music files stored in the app.
- **Library statistics**: View statistics about the music library, including total files, total duration, unique artists, and albums.

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yvmeli/Echo.git
    cd echo
    ```

2. **Create a virtual environment and install dependencies:**

    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3. **Set up the environment variables:**

    ```bash
    export FLASK_APP=app.py
    export FLASK_ENV=development
    ```

4. **Run the application:**

    ```bash
    flask run
    ```

5. **Open your browser and visit:**

    ```
    http://127.0.0.1:5000
    ```

## Usage

- **Home page**: The homepage (`/`) allows you to access the YouTube-to-MP3 converter and see the music library.
- **Convert YouTube video to MP3**: Use the form at `/youtube_to_mp3` to convert a YouTube video to MP3 format.
- **Upload a music file**: Use the file upload form to add a new music file to the library.
- **View library**: Navigate to `/music` to see all uploaded files with their metadata.
- **Download music**: Download any music file by visiting `/downloads/<filename>`.
- **Edit metadata**: Update metadata for any file via a POST request to `/edit/<filename>`.
- **Delete file**: Delete a file from the library using a POST request to `/delete/<filename>`.
- **View statistics**: Get statistics about your library at `/stats`.

## Directory Structure

- `app.py`: Main application file.
- `templates/`: Contains the HTML files for the Flask routes.
  - `index.html`: Homepage template.
  - `base.html`: Base template that serves as the foundation for other templates like `youtube_to_mp3.html`.
  - `youtube_to_mp3.html`: YouTube to MP3 conversion page template.
- `static/uploads/`: Directory where uploaded and converted files are stored.

## Dependencies

- Flask
- WTForms
- mutagen
- yt-dlp

## Contributing

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes.
4. Push to your branch.
5. Create a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.