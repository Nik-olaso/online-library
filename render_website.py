import os
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
import codecs
from livereload import Server
from more_itertools import chunked
from dotenv import load_dotenv


def on_reload():
    env = Environment(
        loader=FileSystemLoader("."), autoescape=select_autoescape(["html", "xml"])
    )
    template = env.get_template("template.html")

    pages_path = "pages"
    os.makedirs(pages_path, exist_ok=True)

    books_folder = os.getenv("BOOKS_FOLDER")

    with codecs.open(f"{books_folder}/books_params.json", "r", "utf_8_sig") as books_file:
        books_params = json.load(books_file)
    books_on_page = 10
    books_params = list(chunked(books_params, books_on_page))
    for page_number, book_params in enumerate(books_params, 1):
        filename = f"index{page_number}.html"
        books_on_str = 2
        book_params = list(chunked(book_params, books_on_str))
        rendered_page = template.render(
            all_books=book_params,
            page_number=page_number,
            pages_count=len(books_params),
        )

        with open(f"{pages_path}/{filename}", "w", encoding="utf8") as file:
            file.write(rendered_page)


def main():
    load_dotenv()
    on_reload()
    server = Server()
    server.watch("template.html", on_reload)
    server.serve(root=".")


if __name__ == "__main__":
    main()
