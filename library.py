import os
import requests
from pathvalidate import sanitize_filepath
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import argparse


def check_for_redirect(response):
    if response.history:
        if response.url == 'https://tululu.org/':
            raise requests.HTTPError


def download_txt(response, filename, folder='books/'):
    os.makedirs(folder, exist_ok=True)
    filepath = sanitize_filepath(os.path.join(folder, f'{filename}.txt'))
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def download_image(image_url, folder='images/'):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(image_url)
    response.raise_for_status()   
    filename = os.path.basename(image_url)
    filepath = sanitize_filepath(os.path.join(folder, f'{filename}'))
    with open(filepath, 'wb') as file:
        file.write(response.content)


def parse_book_page(number):
    url = f"https://tululu.org/b{number+1}/"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    book = soup.find('h1').text.split('::')
    book_name = book[0].strip()
    book_author = book[1].strip()
    picture = soup.find('div', class_='bookimage').find('img')['src']
    comments = soup.find_all('div', class_='texts')
    book_genres = []
    genres = soup.find_all('span', class_='d_book')
    for genre in genres:
        genres = genre.find_all('a')
        for genre in genres:
            book_genres.append(genre.text)
    book_params = {
        'book_name' : book_name,
        'book_author' : book_author,
        'picture' : picture,
        'comments' : comments,
        'book_genres': book_genres,
    }
    return book_params


def main():
    parser = argparse.ArgumentParser(description="Это скрипт создан для скачивания книг с онлайн-библиотеки")
    parser.add_argument("--start_id", default = 0, help="С книги с каким ID начинать скачивание")
    parser.add_argument("--end_id", default = 10, help="С книги с каким ID закончить скачивание")
    args = parser.parse_args()
    start_id = args.start_id
    end_id = args.end_id
    for number in range(int(start_id)-1, int(end_id)+1):     
        try:
            url = f"https://tululu.org/txt.php?id={number+1}"
            response = requests.get(url)
            response.raise_for_status() 
            check_for_redirect(response)
            book_params = parse_book_page(number)
            book_name = book_params['book_name']
            book_author = book_params['book_author']
            book_picture = book_params['picture']
            book_comments = book_params['comments']
            book_genres = book_params['book_genres']
            download_txt(response, f'{number+1}. {book_name}', folder='txt/')
            image_url = urljoin(url, book_picture)
            download_image(image_url)
            print(f'\nНазвание книги: {book_name}')
            print(f'Автор: {book_author}\n')
            if book_comments:
                for comment in book_comments:
                    comment_text = comment.find('span', class_='black').text
                    print(f'Комментарий: {comment_text} \n')
            print(f'Жанры книги: {book_genres} \n\n')
        except requests.HTTPError:
            next
            

if __name__ == '__main__':
    main()
