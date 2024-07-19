from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from library import download_txt, download_image, parse_book_page, check_for_redirect
import time
import argparse
import json


def main():
    parser = argparse.ArgumentParser(
        description="Это скрипт создан для скачивания книг с онлайн-библиотеки"
    )
    parser.add_argument(
        "--start_page", type=int, default=1, help="С какой страницы начинать скачивание"
    )
    parser.add_argument(
        "--end_page",
        type=int,
        default=702,
        help="С какой страницы закончить скачивание",
    )
    parser.add_argument(
        "--skip_txt",
        action="store_true",
        help="Пропустить скачивание текста книг или нет. Если пропустить - просто введите название параметра: '--skip_txt', в ином случае не вводите параметр",
    )
    parser.add_argument(
        "--skip_img",
        action="store_true",
        help="Пропустить скачивание картинки книг или нет. Если пропустить - просто введите название параметра: '--skip_img', в ином случае не вводите параметр",
    )
    parser.add_argument(
        "--dest_folder",
        default="all_folders",
        help="Название общей папки для текста книг, их картинок и json-файла с параметрами книги",
    )
    args = parser.parse_args()
    start_page = args.start_page
    end_page = args.end_page
    skip_txt = args.skip_txt
    skip_img = args.skip_img
    dest_folder = args.dest_folder
    all_books_params = []
    for number in range(start_page, end_page):
        try:
            scifi_url = f"https://tululu.org/l55/{number}"
            response = requests.get(scifi_url)
            response.raise_for_status()
            check_for_redirect(response)
            soup = BeautifulSoup(response.text, "lxml")
            books_cards = soup.select(".d_book")
            for book_card in books_cards:
                try:
                    book_id = book_card.select_one("a")["href"]
                    book_id = book_id.split("/")[1][1:]
                    payload = {
                        "id": book_id,
                    }
                    downloading_url = "https://tululu.org/txt.php"
                    downloading_response = requests.get(downloading_url, params=payload)
                    downloading_response.raise_for_status()
                    check_for_redirect(downloading_response)

                    book_url = book_card.select_one("a")["href"]
                    book_url = urljoin(scifi_url, book_url)
                    book_response = requests.get(book_url)
                    book_response.raise_for_status()
                    check_for_redirect(book_response)

                    book_params = parse_book_page(book_response)
                    book_name = book_params["book_name"]
                    book_picture_url = book_params["picture_url"]
                    all_books_params.append(book_params)

                    if not skip_txt:
                        book_path = download_txt(
                            downloading_response, f"{book_name}", dest_folder
                        )
                        book_params["book_path"] = book_path
                    image_url = urljoin(book_url, book_picture_url)
                    if not skip_img:
                        image_path = download_image(image_url, dest_folder)
                        book_params["img_src"] = image_path
                    book_params.pop("picture_url")

                except requests.HTTPError:
                    print("К сожалению запрос по этой книге оказался неудачным\n")
                    next
                except requests.ConnectionError:
                    print(
                        "Что-то произошло с подключением к интернету, повторяется запрос.\n"
                    )
                    time.sleep(3)
                    continue
        except requests.HTTPError:
            print("К сожалению запрос по этой книге оказался неудачным\n")
            next
        except requests.ConnectionError:
            print("Что-то произошло с подключением к интернету, повторяется запрос.\n")
            time.sleep(3)
            continue
    with open(f"{dest_folder}/books_params.json", "a", encoding="utf8") as json_file:
        json.dump(all_books_params, json_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
