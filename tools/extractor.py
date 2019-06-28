from bs4 import BeautifulSoup
from datetime import timedelta
import aiohttp
from io import BytesIO
import logging.config

LOGGER_CONFIG = {
    'version': 1,
    'root': {
            'handlers': ['consoleHandler', 'fileHandler'],
            'level': 'NOTSET'
    },
    'handlers': {
        'consoleHandler': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'default'
        },
        'fileHandler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/log.txt',
            'mode': 'w',
            'maxBytes': 1024*1024*100,
            'backupCount': 3,
            'level': 'INFO',
            'formatter': 'default',
            'encoding': 'utf-8'
        }
    },
    'formatters': {
        'default': {
            'format': '%(asctime)s [%(levelname)s]: %(message)s',
            'datefmt': '%H:%M:%S %d.%m.%Y'
        }
    }
}

logging.config.dictConfig(LOGGER_CONFIG)
log = logging.getLogger(__name__)


async def fetch(url, raw=False):
    try:
        async with aiohttp.ClientSession() as client:
            async with client.get(url) as resp:
                if resp.status == 200:
                    if raw:
                        return await resp.read()
                    return await resp.text()
    except:
        log.exception('Error occured while fetching url')
        return None


async def get_filelike(url):
    img = await fetch(url, True)
    if img is None:
        log.error("Couldn't retrieve an image")
        return None
    return BytesIO(img)


def parse_endorsment_type(soup, typename):
    e_type = soup.find('svg', attrs={'class': f'EndorsementIcon-border--{typename}'})
    if e_type is None:
        log.error(f"Couldn't find {typename} value")
        return None
    return int(float(e_type['data-value']) * 100)


async def check_profile(tag):
    """ Checks if profile is available and PUBLIC
    :param tag: Tag in '-' or '#' notation
    :return: Is Public, bs4 object
    """
    text = await fetch(f'https://playoverwatch.com/en-us/career/pc/{tag}')
    if text is None:
        log.error(f"Couldn't retrieve page for {tag}")
        return False, None

    log.info(f'HTML page for {tag} retrieved')
    soup = BeautifulSoup(text, 'lxml')
    not_found = soup.find('body', attrs={'class': 'ErrorPage'})
    if not_found:
        log.error("But such profile doesn't exist")
        return False, None

    permission = soup.find('p', attrs={'class': 'masthead-permission-level-text'})
    return not permission.text.split(' ')[0] == 'Private', soup


async def parse(tag):
    public, soup = await check_profile(tag)
    result = await parse_soup(public, soup)
    if result:
        result['Tag'] = '#'.join(tag.split('-'))
    return result


async def parse_soup(public, soup):
    result = {}
    result['Public'] = public

    # result['Icon']
    try:
        icon = soup.find('img', attrs={'class': 'player-portrait'})
        icon = await get_filelike(icon['src'])
        if icon is None:
            return None
    except:
        log.exception('Failed to get file for portrait')
        return None
    result['Icon'] = icon

    # result['Level']['Border']
    # result['Level']['Rank'] <- optional
    # result['Level']['Value']
    try:
        level = {}
        level_tag = soup.find('div', attrs={'class': 'player-level'})
        icon = level_tag['style'].split(' ')[1]
        icon = await get_filelike(icon)
        if icon is None:
            return None
        level['Border'] = icon

        icon = level_tag.find('div', attrs={'class': 'player-rank'})
        if icon:
            icon = icon['style'].split(' ')[1]
            icon = await get_filelike(icon)
            if icon is None:
                return None
            level['Rank'] = icon
        level['Value'] = int(level_tag.find('div').text)
        result['Level'] = level
    except:
        log.exception("Error occured while parsing level")
        return None

    # result['Endorsment']['Level'tag]
    # result['Endorsment']['Shot Caller']
    # result['Endorsment']['Good Teammate']
    # result['Endorsment']['Sportsmanship']
    endorsment = {}
    level = soup.find('div', class_='endorsement-level')
    if level is None:
        log.error('Error occured while parsing endorsment level')
        return None
    try:
        level = int(level.find('div', class_='u-center').text)
    except:
        log.exception("Couldn't retrieve endorsment level info")
        return None
    endorsment['Level'] = level
    endorsment['Shot Caller'] = parse_endorsment_type(soup, 'shotcaller')
    endorsment['Good Teammate'] = parse_endorsment_type(soup, 'teammate')
    endorsment['Sportsmanship'] = parse_endorsment_type(soup, 'sportsmanship')

    if None in endorsment.values():
        log.error("Couldn't retrieve endorsment value")
        return None
    result['Endorsment'] = endorsment

    if not public:
        return result

    # Optional
    # result['Rank']['Icon']
    # result['Rank']['Value']
    rank = {}
    rank_tag = soup.find('div', class_='competitive-rank')
    if rank_tag is not None:
        try:
            img = rank_tag.find('img')['src']
        except:
            log.exception("Couldn't retrieve rank icon")
            return None
        img = await get_filelike(img)
        if img is None:
            return None
        rank['Icon'] = img

        try:
            value = int(rank_tag.find('div').text)
        except:
            log.exception("Couldn't retrieve rank value")
            return None
        rank['Value'] = value
        result['Rank'] = rank
    else:
        log.error("Couldn't find tag containing rank info")

    # Extracts all info, but we need only time played
    # option_tags = soup.find('select', {'data-js': 'career-select'})
    # if option_tags is None:
    #     log.error("Couldn't find selectors")
    #     return None
    # option_tags = option_tags.children
    # options = {}
    # for option_tag in option_tags:
    #     options[option_tag.text] = option_tag['value']
    options = {'Time Played': '0x0860000000000021'}

    # Optional
    # result['Quickplay']['hero1']
    # ...
    # result['Quickplay']['heroN']
    qp = soup.find('div', id='quickplay')
    if qp is not None:
        result['Quickplay'] = parse_mode(qp, options)
        if result['Quickplay'] is None:
            log.error('Error occured while parsing quickplay')
            return None

    # Optional
    # result['Competitive']['hero1']
    # ...
    # result['Competitive']['heroN']
    cp = soup.find('div', id='competitive')
    if cp is not None:
        result['Competitive'] = parse_mode(cp, options)
        if result['Competitive'] is None:
            log.error('Error occured while parsing competitive')
            return None

    return result


def parse_mode(mode, options):
    result = {}
    for key, value in options.items():
        result_per_option = {}
        tag = mode.find('div', {'data-category-id': value})
        if tag is None:
            return None
        for hero in tag:
            name = hero.find('div', class_='ProgressBar-title')
            if name is None:
                return None
            name = name.text
            info = hero.find('div', class_='ProgressBar-description')
            if info is None:
                return None
            info = info.text
            result_per_option[name] = info
        result[key] = result_per_option
    return result


def extract(old, new):
    result = {}
    do_return = False

    result['Tag'] = new['Tag']

    result['Icon'] = new['Icon']

    level = new['Level'].copy()
    diff = new['Level']['Value'] - old['Level']['Value']

    # Let's assume you can't get 100 levels in a single session
    if diff < 0:
        diff += 100
    if diff:
        level['Value'] = f"{level['Value']} ({diff:+})"
        do_return = True
    else:
        level['Value'] = f"{level['Value']}"
    result['Level'] = level

    result['Endorsment'] = {}
    for k, v in new['Endorsment'].items():
        diff = new['Endorsment'][k] - old['Endorsment'][k]
        if diff:
            result['Endorsment'][k] = f'{v} ({diff:+})'
            do_return = True
        else:
            result['Endorsment'][k] = f'{v}'

    result['Public'] = new['Public']
    if old['Public'] != new['Public']:
        do_return = True

    if not new['Public'] or not old['Public'] and new['Public']:
        # Don't perform further operations if profile is closed
        # or was closed during previous check
        return result if do_return else None

    if 'Rank' in new:
        rank = new['Rank'].copy()
        if 'Rank' in old:
            diff = new['Rank']['Value'] - old['Rank']['Value']
        else:
            diff = new['Rank']['Value']
        if diff:
            do_return = True
            rank['Value'] = f"{rank['Value']} ({diff:+})"
        result['Rank'] = rank

    mode = 'Quickplay'
    qp = get_diff_time(old, new, mode)
    if qp:
        do_return = True
        result[mode] = qp

    mode = 'Competitive'
    cp = get_diff_time(old, new, mode)
    if cp:
        do_return = True
        result[mode] = cp

    return result if do_return else None


def get_diff_time(old, new, mode):
    old_heroes = old[mode]['Time Played']
    new_heroes = new[mode]['Time Played']
    result = {}
    for key, value in new_heroes.items():
        new_time = get_timedelta(value)
        if key in old_heroes:
            old_time = get_timedelta(old_heroes[key])
            diff = new_time - old_time
        else:
            diff = new_time
        if diff:
            result[key] = diff
    return result


def get_timedelta(str):
    tokens = str.split(':')
    if len(tokens) > 2:
        hours = int(tokens[0])
        minutes = int(tokens[1])
        seconds = int(tokens[2])
    elif len(tokens) == 2:
        hours = 0
        minutes = int(tokens[0])
        seconds = int(tokens[1])
    else:
        return timedelta(0)

    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


def log_parsed(info, type):  # pragma: no cover
    log.info(f'------ {type} info: ------')
    # info['Tag']
    log.info(f'Tag: {info["Tag"]}')

    # info['Public']
    log.info(f'Type: {info["Public"]}')

    # info['Level']['Value']
    log.info(f'Level: {info["Level"]["Value"]}')

    # info['Rank']['Value'] <- optional
    if 'Rank' in info:
        log.info(f'Rank: {info["Rank"]["Value"]}')

    # result['Endorsment']['Level'tag]
    # result['Endorsment']['Shot Caller']
    # result['Endorsment']['Good Teammate']
    # result['Endorsment']['Sportsmanship']
    tolog = []
    if 'Endorsment' in info:
        log.info(f'Endorsment:')
        for k, v in info['Endorsment'].items():
            log.info(f'\t{k}: {v}')

    # Optional
    # result['Quickplay']['hero1']
    # ...
    # result['Quickplay']['heroN']
    if 'Quickplay' in info:
        tolog.append('Quickplay')

    # Optional
    # result['Competitive']['hero1']
    # ...
    # result['Competitive']['heroN']
    if 'Competitive' in info:
        tolog.append('Competitive')

    for mode in tolog:
        log.info(f'{mode}')
        if 'Time Played' in info[mode]:
            mode = info[mode]['Time Played']
            for k, v in mode.items():
                log.info(f'\t{k}: {v}')
    log.info('\n')


def log_extracted(diff):  # pragma: no cover
    log.info('------ Difference ------')
    # diff['Tag']
    log.info(f'Tag: {diff["Tag"]}')

    # diff['Public'] <- optional
    if 'Public' in diff:
        log.info(f'Type: {diff["Public"]}')

    # diff['Level']['Value']
    # diff['Level']['Diff'] <- optional
    log.info(f'Level: {diff["Level"]["Value"]}')
    if 'Diff' in diff['Level']:
        log.info(f'Level diff: {diff["Level"]["Diff"]}')

    # Optional
    # diff['Rank']['Value']
    # diff['Rank']['Diff']
    if 'Rank' in diff:
        log.info(f'Rank: {diff["Rank"]}')
        if 'Diff' in diff['Rank']:
            log.info(f'Rank diff: {diff["Rank"]["Diff"]}')

    # diff['Endorsment']['Level']
    # diff['Endorsment']['Shot Caller']
    # diff['Endorsment']['Good Teammate']
    # diff['Endorsment']['Sportsmanship']
    # Optional
    # diff['Endorsment']['Diff']['Level']
    # diff['Endorsment']['Diff']['Shot Caller']
    # diff['Endorsment']['Diff']['Good Teammate']
    # diff['Endorsment']['Diff']['Sportsmanship']
    log.info(f'Endorsment:')
    for k, v in diff['Endorsment'].items():
        log.info(f'\t{k}: {v}')

    tolog = []
    # Optional
    # diff['Quickplay']['hero1']
    # ...
    # diff['Quickplay']['heroN']
    if 'Quickplay' in diff:
        tolog.append('Quickplay')

    # Optional
    # diff['Competitive']['hero1']
    # ...
    # diff['Competitive']['heroN']
    if 'Competitive' in diff:
        tolog.append('Competitive')

    for mode in tolog:
        log.info(f'{mode}')
        mode = diff[mode]
        for k, v in mode.items():
            log.info(f'\t{k}: {v}')
    log.info('\n')
