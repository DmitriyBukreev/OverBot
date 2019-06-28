import tools.extractor as p
from asyncio import get_event_loop
import pprint
import bs4
from io import BytesIO
rc = get_event_loop().run_until_complete


def fetch_and_save(tag, filename):
    _, soup = rc(p.check_profile(tag))
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(str(soup))


def load(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
    return bs4.BeautifulSoup(text, 'lxml')


def get_parsed(state, soup):
    return rc(p.parse_soup(state, soup))


prefix = {None: '', True: '{', False: '}'}


def print_level(level, opening=None, spaces=4):
    print(f'\n{" "*level*spaces}{prefix[opening]}', end='')


def print_recursively(data, level=0):
    print_level(level, opening=True)
    last_key = list(data.keys())[-1]
    for k, v in data.items():
        print_level(level)
        print(f"'{k}': ", end='')
        if isinstance(v, dict):
            print(end='')
            print_recursively(v, level=level+1)
        elif isinstance(v, BytesIO):
            print('None', end='')
        elif isinstance(v, str):
            print(f"'{v}'", end='')
        else:
            print(f'{v}', end='')
        if k != last_key:
            print(',', end='')

    print_level(level, opening=False)


def load_and_print(state, filename):
    soup = load(filename)
    parsed = get_parsed(state, soup)
    print_recursively(parsed)


if __name__ == '__main__':
    priv = get_parsed(False, load('../input/PRIVATE.html'))
    pub = get_parsed(True, load('../input/NEW.html'))
    pub['Tag'] = 'Test'
    priv['Tag'] = 'Test'
    extr = p.extract(pub, priv)
    pprint.pprint(extr)
