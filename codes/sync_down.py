import requests
from PIL import Image
from bs4 import BeautifulSoup
from pathlib import Path
import argparse
import json
import re
from termcolor import colored

# Load config
config_path = Path.cwd() / 'config/config.json'
with open(config_path, 'r') as config_file:
    config_data = json.load(config_file)

# Argument parsing
def get_args():
    parser = argparse.ArgumentParser(description='Download Manga from https://mangaita.io/')
    parser.add_argument('-u', '--url', help='URL of the website', required=True)
    parser.add_argument('-d', '--debug', help='Enable debug mode', action='store_true')
    parser.add_argument('-s', '--start_chapter', type=int, help='Start chapter number', default=1)
    parser.add_argument('-e', '--end_chapter', type=int, help='End chapter number', default=None)
    return parser.parse_args()

# Debug print
def debug_print(message):
    if args.debug:
        print(colored(f"Debug: {message}", 'yellow'))

# Download image function
def download_image(img_url, folder, post_index, download_info_file):
    if not img_url.startswith("http"):
        img_url = "https://mangaita.io" + img_url  # Adjust URL if needed

    img_name = Path(img_url.split("?")[0]).name
    img_path = folder / img_name

    try:
        debug_print(f"Downloading {img_name} from {img_url}")
        img_data = requests.get(img_url)
        if img_data.status_code == 200:
            img_path.write_bytes(img_data.content)
            debug_print(f"Downloaded {img_name} to {img_path}")
        else:
            download_info_file.write(f"Error downloading {img_name}: {img_url}\n")
            print(f"Error downloading {img_name}: {img_url}")
    except Exception as e:
        download_info_file.write(f"Error downloading {img_name}: {e}\n")
        print(f"Error downloading {img_name}: {e}")

# Get images for a chapter
def get_images(url, folder, post_index, download_info_file):
    response = requests.get(url)
    if response.status_code != 200:
        download_info_file.write(f"Error fetching post {post_index}: Failed to retrieve the webpage\n")
        print(f"Error fetching post {post_index}: Failed to retrieve the webpage")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    img_tags = soup.find_all("img")

    for img in img_tags:
        src = img.get("src")
        if src and "logo.2c1c1f72.webp" not in src:  # Exclude the logo
            try:
                download_image(src, folder, post_index, download_info_file)
            except Exception as e:
                download_info_file.write(f"Error downloading image from {src}: {e}\n")
                print(f"Error downloading image from {src}: {e}")

    next_button = soup.find("a", class_="btn btn-primary btn-navigation btn-next")
    if next_button and next_button.get("href"):
        next_url = "https://mangaita.io" + next_button["href"]
        debug_print(f"Next page URL: {next_url}")
        get_images(next_url, folder, post_index + 1, download_info_file)

# Create PDF from images in a folder
def create_pdf_from_images(folder):
    if not config_data.get("create_pdf", False):
        print("PDF creation is disabled in the config file.")
        return
    
    images = []
    sorted_files = sorted(
        folder.iterdir(),
        key=lambda x: int(re.search(r'(\d+)', x.name).group()) if re.search(r'(\d+)', x.name) else float('inf')
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

# Download manga or chapter
def get_manga(args):
    url = args.url
    start_chapter = args.start_chapter
    end_chapter = args.end_chapter if args.end_chapter else float('inf')  # se end_chapter non è specificato, va fino all'ultimo capitolo
    
    if "https://mangaita.io/" not in url:
        print("Invalid URL, please use https://mangaita.io/")
        return

    manga_name = url.split("/")[-1]
    manga_dir = Path.cwd() / 'Manga' / manga_name
    manga_dir.mkdir(parents=True, exist_ok=True)
    download_info_path = manga_dir / 'download_info.txt'
    
    with open(download_info_path, 'w') as download_info_file:
        download_info_file.write(f"Download started for manga: {manga_name}\n")
        
        if "/scan/" in url:
            get_images(url, manga_dir, 0, download_info_file)
            create_pdf_from_images(manga_dir)
            print("Download finished.")
            return

        response = requests.get(url)
        if response.status_code != 200:
            print("Failed to retrieve the webpage")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        chapter_divs = soup.find_all("div", class_="col-chapter")

        if config_data.get("latest_first", False):
            chapter_divs = reversed(chapter_divs)

        post_index = 0
        for chapter in chapter_divs:
            link_tag = chapter.find("a")
            title_tag = chapter.find("h5")
            
            if link_tag and title_tag:
                chapter_title = title_tag.text.strip().split("\n")[0]
                chapter_url = "https://mangaita.io" + link_tag["href"]
                
                # Estrai il numero del capitolo
                chapter_number = int(re.search(r'\d+', chapter_title).group())

                # Se il capitolo è nel range specificato, scaricalo
                if start_chapter <= chapter_number <= end_chapter:
                    chapter_dir = manga_dir / chapter_title
                    chapter_dir.mkdir(parents=True, exist_ok=True)
                    
                    try:
                        print(f"Processing chapter: {chapter_title}")
                        get_images(chapter_url, chapter_dir, post_index, download_info_file)
                        create_pdf_from_images(chapter_dir)
                    except Exception as e:
                        print(f"Error processing chapter {chapter_title}: {e}")
                    
                    post_index += 1
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
