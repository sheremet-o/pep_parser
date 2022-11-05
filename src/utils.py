from bs4 import BeautifulSoup
from requests import RequestException

from exceptions import ParserFindTagException

FIND_TAG_ERROR = 'Не найден тег {tag} {attrs}.'
REQUEST_ERROR = 'Возникла ошибка при загрузке страницы {}.'


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        raise ConnectionError(REQUEST_ERROR.format(url))


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        raise ParserFindTagException(
            FIND_TAG_ERROR.format(tag=tag, attrs=attrs)
        )
    return searched_tag


def cook_soup(session, url):
    response = get_response(session, url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    return soup
