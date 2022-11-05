import logging
import re
import requests_cache

from urllib.parse import urljoin

from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR, DOWNLOADS_URL, MAIN_DOC_URL, PEP_URL, EXPECTED_STATUS,
)
from outputs import control_output
from utils import cook_soup, find_tag


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = cook_soup(session, whats_new_url)

    sections_by_python = soup.select(
        '#what-s-new-in-python div.toctree-wrapper li.toctree-l1')

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in sections_by_python:
        version_a_tag = section.find('a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        soup = cook_soup(session, version_link)
        h1 = find_tag(soup, 'h1')
        dl_text = soup.find('dl').text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )
    return results


def latest_versions(session):
    soup = cook_soup(session, MAIN_DOC_URL)
    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise LookupError('Ничего не нашлось')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )
    return results


def download(session):
    soup = cook_soup(session, DOWNLOADS_URL)

    main_tag = find_tag(soup, 'div', {'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')}
        )
    archive_url = urljoin(DOWNLOADS_URL, pdf_a4_tag['href'])
    filename = archive_url.split('/')[-1]

    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)

    logging.info(f'Архив был загружен и сохранён: {archive_path}')
    print(archive_url)


def pep(session):
    status_sum = {}
    pep_sum = 0

    soup = cook_soup(session, PEP_URL)

    pep_section_tag = find_tag(
        soup, 'section', attrs={'id': 'numerical-index'})
    pep_body_tag = find_tag(pep_section_tag, 'tbody')
    pep_tags = pep_body_tag.find_all('tr')

    results = [('Статус', 'Количество')]

    for pep_tag in pep_tags:
        status_tag = find_tag(pep_tag, 'td')
        general_status = status_tag.text[1:]
        a_tag = find_tag(pep_tag, 'a')
        href = a_tag['href']

        pep_link = urljoin(PEP_URL, href)
        soup = cook_soup(session, pep_link)

        info_tags = soup.find_all('dt')

        for info_tag in info_tags:
            if info_tag.text == 'Status:':
                pep_sum += 1
                status = info_tag.find_next_sibling().string
                if status in status_sum:
                    status_sum[status] += 1
                if status not in status_sum:
                    status_sum[status] = 1
                if status not in EXPECTED_STATUS[general_status]:
                    error_msg = (
                        'Несовпадающие статусы:\n'
                        f'{pep_link}\n'
                        f'Статус в карточке: {status}\n'
                        f'Ожидаемые статусы: {EXPECTED_STATUS[general_status]}'
                    )
                    logging.warning(error_msg)
    for status in status_sum:
        results.append((status, status_sum[status]))
    results.append(pep_sum)
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
