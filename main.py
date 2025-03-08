import os
import subprocess
import time
import json

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_logo():
    logo = r"""
  __  __                         _ _          _       
 |  \/  | __ _ _ __   __ _  __ _(_) |_ __ _  (_) ___  
 | |\/| |/ _` | '_ \ / _` |/ _` | | __/ _` | | |/ _ \ 
 | |  | | (_| | | | | (_| | (_| | | || (_| |_| | (_) |
 |_|  |_|\__,_|_| |_|\__, |\__,_|_|\__\__,_(_)_|\___/ 
  ____               |___/              _             
 |  _ \  _____      _| | ___   __ _  __| | ___ _ __   
 | | | |/ _ \ \ /\ / / |/ _ \ / _` |/ _` |/ _ \ '__|  
 | |_| | (_) \ V  V /| | (_) | (_| | (_| |  __/ |     
 |____/ \___/ \_/\_/ |_|\___/ \__,_|\__,_|\___|_|     


 Created by Zenith
 Github: https://github.com/ZenithRealm   
 Discord: https://discord.gg/6KM5GkJAYP       
 Project Repository: https://github.com/ZenithRealm/Mangaita.io-Dowloader
    """
    clear_screen()
    print(logo)

config_path = os.path.join('config', 'config.json')

    # Load the configuration file
try:
    with open(config_path, 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    print("Error: Configuration file not found.")

if config['download_type'] == "sync":
    down = os.path.join('codes', 'sync_down.py')
else:
    down = os.path.join('codes', 'async_down.py')



def download_specific_posts():
    """Option to download specific posts"""
    clear_screen()
    print_logo()
    print("Download a specific post or multiple separate posts")
    print("------------------------------------")
    print("Choose the input method:")
    print("1 - Load links from a TXT file")
    print("2 - Enter the links manually")
    print("3 - Back to the main menu")
    choice = input("\nEnter your choice (1/2/3): ")

    links = []

    if choice == '1':
        file_path = input("Enter the path to the TXT file: ").strip()
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                links = content.split(',')
        else:
            print(f"Error: The file '{file_path}' was not found.")
            input("\nPress Enter to continue...")
            return
    elif choice == '2':
        print("Paste the links to the posts (separated by commas):")
        links = input("Links: ").split(',')
    elif choice == '3':
        return
    else:
        print("Invalid option. Returning to the previous menu.")
        input("\nPress Enter to continue...")
        return

    links = [link.strip() for link in links if link.strip()]

    # Check if the links are valid (must start with 'https://mangaita.io/scan/' or 'mangaita.io/scan/')
    invalid_links = [link for link in links if not (link.startswith('https://mangaita.io/scan/') or link.startswith('mangaita.io/scan/'))]
    if invalid_links:
        print("Invalid links detected. Only links starting with 'https://mangaita.io/scan/' or 'mangaita.io/scan/' are allowed:")
        for invalid_link in invalid_links:
            print(f"Invalid: {invalid_link}")
        input("\nPress Enter to continue...")
        return

    for link in links:
        try:
            subprocess.run(['python', down, '-u', link], check=True)

        except IndexError:
            print(f"Link format error: {link}")
        except subprocess.CalledProcessError:
            print(f"Error downloading the post: {link}")
        except Exception as e:
            print(f"Unexpected error: {link}, {str(e)}")

    input("\nPress Enter to continue...")

def download_chapters_range():
    while True:  # Loop per assicurarsi che l'utente possa scaricare in un singolo ciclo
        try:
            link = input("Enter the link of the manga: ")
            start_page = int(input("Enter the start chapter (0, 1, 2, etc.): "))
            end_page = input("Enter the final chapter (300, 350, 400): ")
            
            if end_page != "":
                end_page = int(end_page)
            else:
                end_page = start_page  # Imposta end_page uguale a start_page se non specificato
            
        except ValueError:
            print("Invalid input. Returning to the previous menu.")
            input("\nPress Enter to continue...")
            return

        if 'mangaita.io/' not in link:
            print("Invalid link. The link must contain 'mangaita.io/'")
            input("\nPress Enter to continue...")
            return

        if end_page < start_page:
            print("Invalid input. The end chapter must be greater than or equal to the start chapter.")
            input("\nPress Enter to continue...")
            return

        try:
            # Se end_page non è stato specificato, scarica solo il capitolo di partenza
            if end_page == start_page:
                subprocess.run(['python', down, '-u', link, '-s', str(start_page)], check=True)
            else:
                # Se end_page è specificato, scarica il range completo
                subprocess.run(['python', down, '-u', link, '-s', str(start_page), '-e', str(end_page)], check=True)

            # Dopo il download, chiedi se l'utente vuole scaricare altri capitoli
            print("Download completed successfully.")
            continue_choice = input("\nDo you want to download more chapters? (y/n): ").strip().lower()
            if continue_choice != 'y':
                break  # Esce dal ciclo e ritorna al menu

        except subprocess.CalledProcessError:
            print(f"Error downloading the chapters: {link}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
    
def customize_settings():
    """Option to customize settings."""
    config_path = os.path.join('config', 'config.json')

    # Load the configuration file
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Configuration file not found. Exiting...")
        return
    except json.JSONDecodeError:
        print("Error decoding configuration file. Please check the format.")
        return

    while True:
        clear_screen()
        print_logo()
        print("Customize Settings")
        print("------------------------")
        print(f"1 - Download latest posts first: {config['latest_first']}")
        print(f"2 - Create PDF for each chapter: {config['create_pdf']}")
        print(f"3 - Download type: {config['download_type']}")
        print(f"4 - Create Manga folder: {config['create_manga_folder']}")
        print(f"5 - Create Scan folder: {config['create_scan_folder']}")
        print(f"6 - Use custom path: {config['custom_save_path']}")
        print("7 - Back to the main menu")

        choice = input("\nChoose an option (1/2/3/4/5/6/7): ")
        
        if choice == '1':
            config['latest_first'] = not config['latest_first']
        elif choice == '2':
            config['create_pdf'] = not config['create_pdf']
        elif choice == '3':
            config['download_type'] = 'async' if config['download_type'] == 'sync' else 'sync'
        elif choice == '4':
            config['create_manga_folder'] = not config['create_manga_folder']
        elif choice == '5':
            config['create_scan_folder'] = not config['create_scan_folder']
        elif choice == '6':
            while True:
                clear_screen()
                print_logo()
                print("Customize Save Path")
                print("------------------------")
                print("1 - Disable custom path")
                print("2 - Enter custom path")
                print("3 - Back to the previous menu")
                choice = input("\nChoose an option (1/2/3): ")
                if choice == '1':
                    config['custom_save_path'] = False
                if choice == '2':
                    path = input("Enter the custom path: ")
                    if os.path.exists(path):
                        config['custom_save_path'] = path
                    else:
                        print("Invalid path. Please try again.")
                        input("Press enter to continue...")
                elif choice == '3':
                    break
                else:
                    print("Invalid option. Please try again.")


        elif choice == '7':
            print("Exiting settings menu...")
            break  # Esce dal ciclo e ritorna al main menu
        else:
            print("Invalid option. Please try again.")
        

        # Save the updated configurations to the file
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving configurations: {e}")

        time.sleep(0.1)


def main_menu():
    while True:
        clear_screen()
        print_logo()
        print("1 - Download all chapters of the manga")
        print("2 - Download a specific chapter")
        print("3 - Download chapters from a range of chapters")
        print("4 - Customize settings")
        print("5 - Exit from the program")
        choice = input("Enter your choice(1/2/3/4/5): ")

        if choice == "1":
            link = input("Link: ")
            
            if 'mangaita.io/' not in link:
                print("Invalid link. The link must contain 'mangaita.io/'")
                input("\nPress Enter to continue...")

            elif 'scan/' in link:
                print("Please use this link with the dedicated function.")
                input("\nPress Enter to continue...")
            else:
                try:
                    subprocess.run(['python', down, '-u', link], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Error occurred: {e}")
                    input("\nPress Enter to continue...")

        elif choice == "2":
            # code for choice 2
            download_specific_posts()
        
        elif choice == "3":
            # code for choice 3
            download_chapters_range()

        elif choice == "4":
            customize_settings()

        elif choice == "5":
            print("GoodBye")
            break

        else:
            print("Invalid choice, please try again.")
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main_menu()
