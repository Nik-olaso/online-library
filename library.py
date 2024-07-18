import os
import requests
from pathvalidate import sanitize_filepath
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import argparse
import time


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_txt(response, filename, folder):
    new_folder = f"{folder}/books/"
    os.makedirs(new_folder, exist_ok=True)
    filepath = sanitize_filepath(os.path.join(new_folder, f"{filename}.txt"))
    with open(filepath, "wb") as file:
        file.write(response.content)
    return filepath


def download_image(image_url, folder):
    new_folder = f"{folder}/images/"
    os.makedirs(new_folder, exist_ok=True)
    response = requests.get(image_url)
    response.raise_for_status()
    check_for_redirect(response)
    filename = os.path.basename(image_url)
    filepath = sanitize_filepath(os.path.join(new_folder, f"{filename}"))
    with open(filepath, "wb") as file:
        file.write(response.content)
    return filepath


def parse_book_page(parse_response):
    soup = BeautifulSoup(parse_response.text, "lxml")
    book = soup.select_one("h1").text.split("::")
    book_name = book[0].strip()
    book_author = book[1].strip()
    picture_url = soup.select_one(".bookimage img")["src"]
    comments = soup.select(".texts")
    book_genres = [genre.text for genre in soup.select("span.d_book a")]
    book_params = {
        "book_name": book_name,
        "book_author": book_author,
        "picture_url": picture_url,
        "comments": [
            comment.select_one(".black").text for comment in comments
        ],  # Преобразование объектов Tag в строки
        "book_genres": book_genres,
    }
    return book_params


def main():
    parser = argparse.ArgumentParser(
        description="Это скрипт создан для скачивания книг с онлайн-библиотеки"
    )
    parser.add_argument(
        "--start_id", type=int, default=0, help="С книги с каким ID начинать скачивание"
    )
    parser.add_argument(
        "--end_id", type=int, default=10, help="С книги с каким ID закончить скачивание"
    )
    args = parser.parse_args()
    start_id = args.start_id
    end_id = args.end_id
    for number in range(start_id, end_id + 1):
        try:
            payload = {
                "id": number,
            }
            downloading_url = "https://tululu.org/txt.php"
            response = requests.get(downloading_url, params=payload)
            response.raise_for_status()
            check_for_redirect(response)
            parsing_url = f"https://tululu.org/b{number}/"
            parsing_response = requests.get(parsing_url)
            parsing_response.raise_for_status()
            check_for_redirect(parsing_response)
            book_params = parse_book_page(parsing_response)
            book_name = book_params["book_name"]
            book_author = book_params["book_author"]
            book_picture_url = book_params["picture_url"]
            book_comments = book_params["comments"]
            book_genres = book_params["book_genres"]
            download_txt(response, f"{number}. {book_name}", folder="all_books/")
            image_url = urljoin(parsing_url, book_picture_url)
            download_image(image_url, folder="all_books/")
            print(f"\nНазвание книги: {book_name}")
            print(f"Автор: {book_author}\n")
            if book_comments:
                for comment in book_comments:
                    print(f"Комментарий: {comment} \n")
            print(f"Жанры книги: {book_genres} \n\n")
        except requests.HTTPError:
            print(
                "К сожалению запрос по этой книге оказался неудачным, такое часто бывает на этом сайте, попробуйте выбрать другие книги.\n"
            )
            next
        except requests.ConnectionError:
            print("Что-то произошло с подключением к интернету, повторяется запрос.\n")
            time.sleep(3)
            continue


if __name__ == "__main__":
    main()
