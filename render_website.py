import os
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
import codecs
from livereload import Server
from more_itertools import chunked


def on_reload():
    env = Environment(
        loader=FileSystemLoader("."), autoescape=select_autoescape(["html", "xml"])
    )
    template = env.get_template("template.html")

    pages_path = "pages"
    os.makedirs(pages_path, exist_ok=True)

    books_file = codecs.open("all_folders/books_params.json", "r", "utf_8_sig")
    books_params = books_file.read()
    books_file.close()
    books_params = json.loads(books_params)
    books_params = list(chunked(books_params, 10))
    for page_number, book_params in enumerate(books_params, 1):
        filename = f"index{page_number}.html"
        book_params = list(chunked(book_params, 2))
        rendered_page = template.render(
            all_books=book_params,
            page_number=page_number,
            pages_count=len(books_params),
        )

        with open(f"{pages_path}/{filename}", "w", encoding="utf8") as file:
            file.write(rendered_page)


on_reload()
server = Server()
server.watch("template.html", on_reload)
server.serve(root=".")
