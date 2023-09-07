from celery import Celery
import requests
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "../.env"))

celery = Celery(
    "celery_tasks.tasks",
    broker=os.environ['REDIS_SRV'],
    backend=os.environ['REDIS_SRV']
)


def review_response(response):
    try:
        return response if response else ""
    except KeyError:
        return ""


@celery.task
def search_openlibrary(title: str):
    """
    Busqueda de libro por atributos en OpenLibrary
    :param title: atributo de busqueda
    :return: objeto encontrado
    """
    url = "https://openlibrary.org/search.json"
    response = requests.get(f"{url}?title={title}&fields=*,availability&limit=1").json()
    book_response = {
        "title": review_response(response['docs'][0]['title']),
        "subtitle": review_response(response['docs'][0]['title_sort']),
        "publish_date": review_response(response['docs'][0]['publish_year'][0]),
        "description": ' '.join(review_response(response['docs'][0]['subject'])),
        "thumbnail": f"https://covers.openlibrary.org/b/isbn/{review_response(response['docs'][0]['isbn'][1])}-S.jpg",
        "publisher": review_response(response['docs'][0]['publisher_facet'][0]),
        "authors": [
            {
                "name": review_response(response['docs'][0]['author_name'][0])
            }
        ],
        "genres": [
            {
                "name": review_response(response['docs'][0]['subject_key'][0])
            }
        ]
    }
    return book_response


@celery.task
def search_googlebook(title: str):
    """
    Busqueda de libro por atributos en Google Books
    :param title: atributo de busqueda
    :return: objeto encontrado
    """
    url = "https://www.googleapis.com/books/v1/volumes"
    response = requests.get(f"{url}?q={title}&maxResults=1&key={os.environ['API_GK']}").json()
    book_response = {
        "title": review_response(response['items'][0]['volumeInfo']['title']),
        "subtitle": review_response(response['items'][0]['volumeInfo']['title']),
        "publish_date": review_response(response['items'][0]['volumeInfo']['publishedDate']),
        "description": review_response(response['items'][0]['volumeInfo']['description']),
        "thumbnail": review_response(response['items'][0]['volumeInfo']['imageLinks']['smallThumbnail']),
        "publisher": review_response(response['items'][0]['volumeInfo']['publisher']),
        "authors": [
            {
                "name": review_response(response['items'][0]['volumeInfo']['authors'][0])
            }
        ],
        "genres": [
            {
                "name": review_response(response['items'][0]['volumeInfo']['categories'][0])
            }
        ]
    }
    return book_response

