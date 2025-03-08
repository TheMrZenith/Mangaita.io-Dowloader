import os
import requests
from PIL import Image
from bs4 import BeautifulSoup
from pathlib import Path
import argparse
import json
import re
from termcolor import colored

# Load config
config_path = Path.cwd() / 'config' / 'config.json'
with open(config_path, 'r') as config_file:
    config_data = json.load(config_file)

# Determine base directory based on custom_save_path value
base_save_path = config_data.get("custom_save_path", False)

# Se custom_save_path è False, usa il percorso di base
if base_save_path is False:
    base_save_path = Path.cwd() / 'Manga'
else:
    base_save_path = Path(base_save_path)

# Create Manga folder structure if allowed
def create_manga_folder_structure():
    if config_data.get("create_manga_folder", True):
        manga_dir = base_save_path
        manga_dir.mkdir(parents=True, exist_ok=True)
        return manga_dir
    return Path.cwd()  # Default to current directory if folder creation is disabled

# Create Scan folder structure if allowed
def create_scan_folder_structure(manga_dir):
    if config_data.get("create_scan_folder", True):
        scan_dir = manga_dir / "Scan"
        scan_dir.mkdir(parents=True, exist_ok=True)
        return scan_dir
    return manga_dir  # If Scan folder creation is disabled, use the manga directory

# Argument parsing
def get_args():
    parser = argparse.ArgumentParser(description='Download Manga from https://mangaita.io/')
    parser.add_argument('-u', '--url', help='URL of the website', required=True)
    parser.add_argument('-d', '--debug', help='Enable debug mode', action='store_true')
    parser.add_argument('-s', '--start_chapter', type=float, help='Start chapter number', default=1)
    parser.add_argument('-e', '--end_chapter', type=float, help='End chapter number', default=None)
    return parser.parse_args()

# Debug print
def debug_print(message):
    if args.debug:
        print(colored(f"Debug: {message}", 'yellow'))

# Download image function (synchronous version)
def download_image(session, img_url, folder, download_info_file):
    if not img_url.startswith("http"):
        img_url = "https://mangaita.io" + img_url  # Adjust URL if needed

    img_name = os.path.basename(img_url.split("?")[0])
    img_path = folder / img_name

    try:
        debug_print(f"Downloading {img_name} from {img_url}")
        response = requests.get(img_url)
        if response.status_code == 200:
            with open(img_path, 'wb') as f:
                f.write(response.content)
            debug_print(f"Downloaded {img_name} to {img_path}")
        else:
            with open(download_info_file, 'a') as df:
                df.write(f"Error downloading {img_name}: {img_url}\n")
    except Exception as e:
        with open(download_info_file, 'a') as df:
            df.write(f"Error downloading {img_name}: {e}\n")

# Get images for a chapter (synchronous version)
def get_images(session, url, folder, download_info_file):
    response = requests.get(url)
    if response.status_code != 200:
        with open(download_info_file, 'a') as df:
            df.write(f"Error fetching page: {url}\n")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    img_tags = soup.find_all("img")

    for img in img_tags:
        src = img.get("src")
        if src and "logo.2c1c1f72.webp" not in src:
            download_image(session, src, folder, download_info_file)

    next_button = soup.find("a", class_="btn btn-primary btn-navigation btn-next")
    if next_button and next_button.get("href"):
        next_url = "https://mangaita.io" + next_button["href"]
        debug_print(f"Next page URL: {next_url}")
        get_images(session, next_url, folder, download_info_file)

# Create PDF from images in a folder
def create_pdf_from_images(folder):
    if not config_data.get("create_pdf", False):
        print("PDF creation is disabled in the config file.")
        return

    images = []
    sorted_files = sorted(
        folder.iterdir(),
        key=lambda x: float(re.search(r'(\d+\.\d+|\d+)', x.name).group()) if re.search(r'(\d+\.\d+|\d+)', x.name) else float('inf')
    )

    for file in sorted_files:
        if file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
            try:
                im = Image.open(file)
                if im.mode != "RGB":
                    im = im.convert("RGB")
                images.append(im)
                debug_print(f"Image {file.name} added to PDF list.")
            except Exception as e:
                print(f"Error processing image {file}: {e}")
    
    if images:
        pdf_path = folder / "chapter.pdf"
        try:
            images[0].save(pdf_path, save_all=True, append_images=images[1:])
            print(f"PDF created for chapter: {pdf_path}")
        except Exception as e:
            print(f"Error creating PDF in folder {folder}: {e}")
    else:
        print(f"No valid images found in folder {folder} for PDF creation.")

# Download manga or chapter (synchronous version)
def get_manga(args):
    url = args.url
    start_chapter = args.start_chapter
    end_chapter = args.end_chapter if args.end_chapter else float('inf')  # Se end_chapter non è specificato, va fino all'ultimo capitolo
    
    if "https://mangaita.io/" not in url:
        print("Invalid URL, please use https://mangaita.io/")
        return

    manga_name = Path(url.split("/")[-1])

    # Use the custom manga folder or the default one
    manga_dir = create_manga_folder_structure() / manga_name
    scan_dir = create_scan_folder_structure(manga_dir)
    
    manga_dir.mkdir(parents=True, exist_ok=True)

    download_info_path = manga_dir / 'download_info.txt'
    with open(download_info_path, 'w') as df:
        df.write(f"Download started for manga: {manga_name}\n")

    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to retrieve the webpage")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    chapter_divs = soup.find_all("div", class_="col-chapter")
    if config_data.get("latest_first", False):
        chapter_divs = reversed(chapter_divs)

    for chapter in chapter_divs:
        link_tag = chapter.find("a")
        title_tag = chapter.find("h5")
        if link_tag and title_tag:
            chapter_title = Path(title_tag.text.strip().split("\n")[0])
            chapter_url = "https://mangaita.io" + link_tag["href"]

            # Estrai il numero del capitolo
            chapter_number = int(re.search(r'\d+', str(chapter_title)).group())

            # Se il capitolo è nel range specificato, scaricalo
            if start_chapter <= chapter_number <= end_chapter:
                chapter_dir = scan_dir / chapter_title
                chapter_dir.mkdir(parents=True, exist_ok=True)

                print(f"Processing chapter: {chapter_title}")
                with open(download_info_path, 'a') as df:
                    df.write(f"Processing chapter: {chapter_title}\n")
                get_images(None, chapter_url, chapter_dir, download_info_path)
                create_pdf_from_images(chapter_dir)

            # Se il capitolo supera l'intervallo, interrompi
            if chapter_number > end_chapter:
                break

    print("Download finished.")

# Main function
def main():
    global args
    args = get_args()
    get_manga(args)

if __name__ == "__main__":
    main()
