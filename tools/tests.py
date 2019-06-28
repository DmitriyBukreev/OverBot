import asyncio
import unittest as u
import bs4
from io import BytesIO
import tools.extractor as e
import tools.plot as p
import datetime

OLD = {
                    'Tag': 'AbCdEfGhIjK#21855',
                    'Public': True,
                    'Icon': None,
                    'Level':
                        {
                            'Border': None,
                            'Value': 99
                        },
                    'Endorsment':
                        {
                            'Level': 4,
                            'Shot Caller': 19,
                            'Good Teammate': 56,
                            'Sportsmanship': 24
                        },
                    'Quickplay':
                        {
                            'Time Played':
                                {
                                    'Hanzo': '16:35:55',
                                    'McCree': '15:54:36',
                                    'Reinhardt': '12:29:55',
                                    'Moira': '11:56:53',
                                    'Ana': '11:28:34',
                                    'Pharah': '10:26:13',
                                    'Widowmaker': '09:09:10',
                                    'D.Va': '08:31:47',
                                    'Genji': '07:53:03',
                                    'Zarya': '07:41:45',
                                    'Zenyatta': '06:43:17',
                                    'Ashe': '06:06:36',
                                    'Lúcio': '05:48:11',
                                    'Roadhog': '05:42:56',
                                    'Orisa': '05:06:38',
                                    'Soldier: 76': '04:41:00',
                                    'Junkrat': '04:14:48',
                                    'Reaper': '04:13:38',
                                    'Symmetra': '03:17:53',
                                    'Torbjörn': '03:15:18',
                                    'Tracer': '03:00:50',
                                    'Winston': '02:21:29',
                                    'Mercy': '01:53:34',
                                    'Mei': '01:50:18',
                                    'Brigitte': '01:34:09',
                                    'Bastion': '01:32:00',
                                    'Baptiste': '01:31:03',
                                    'Sombra': '01:01:52',
                                    'Wrecking Ball': '49:20',
                                    'Doomfist': '41:48'
                                }
                        },
                    'Competitive':
                        {
                            'Time Played':
                                {
                                    'Hanzo': '09:16:39',
                                    'McCree': '07:28:50',
                                    'Ana': '05:37:12',
                                    'Reinhardt': '03:29:21',
                                    'Zarya': '02:34:45',
                                    'Reaper': '02:00:44',
                                    'D.Va': '01:38:50',
                                    'Junkrat': '01:32:48',
                                    'Soldier: 76': '01:26:36',
                                    'Pharah': '01:22:36',
                                    'Symmetra': '01:18:11',
                                    'Orisa': '01:11:50',
                                    'Widowmaker': '01:08:38',
                                    'Moira': '54:34',
                                    'Zenyatta': '48:53',
                                    'Baptiste': '48:10',
                                    'Winston': '44:28',
                                    'Bastion': '43:48',
                                    'Roadhog': '37:42',
                                    'Mei': '31:50',
                                    'Lúcio': '30:54',
                                    'Torbjörn': '25:51',
                                    'Brigitte': '18:47',
                                    'Tracer': '06:50',
                                    'Sombra': '04:59',
                                    'Mercy': '02:13',
                                    'Ashe': '02:10',
                                    'Wrecking Ball': '0'
                                }
                        }
                    }
PUBLIC = NEW = {
                    'Tag': 'AbCdEfGhIjK#21855',
                    'Public': True,
                    'Icon': 'input/icons/Icon.png',
                    'Level':
                        {
                        'Border': 'input/icons/Border.png',
                        'Rank': 'input/icons/Rank.png',
                        'Value': 1
                        },
                    'Endorsment':
                        {
                        'Level': 3,
                        'Shot Caller': 21,
                        'Good Teammate': 56,
                        'Sportsmanship': 23
                        },
                    'Rank':
                        {
                        'Icon': 'input/icons/CP_rank.png',
                        'Value': 2524
                        },
                    'Quickplay':
                        {
                        'Time Played':
                            {
                            'Hanzo': '16:40:00',
                            'McCree': '15:55:40',
                            'Reinhardt': '12:29:55',
                            'Moira': '12:00:00',
                            'Ana': '11:45:00',
                            'Pharah': '10:30:00',
                            'Widowmaker': '09:09:10',
                            'D.Va': '08:31:47',
                            'Genji': '07:53:03',
                            'Zarya': '07:41:45',
                            'Zenyatta': '06:43:17',
                            'Ashe': '06:06:36',
                            'Lúcio': '05:48:11',
                            'Roadhog': '05:42:56',
                            'Orisa': '05:06:38',
                            'Soldier: 76': '04:41:00',
                            'Junkrat': '04:14:48',
                            'Reaper': '04:13:38',
                            'Symmetra': '03:17:53',
                            'Torbjörn': '03:15:18',
                            'Tracer': '03:00:50',
                            'Winston': '02:21:29',
                            'Mercy': '01:53:34',
                            'Mei': '01:50:18',
                            'Brigitte': '01:34:09',
                            'Bastion': '01:32:00',
                            'Baptiste': '01:31:03',
                            'Sombra': '01:01:52',
                            'Wrecking Ball': '49:20',
                            'Doomfist': '50:00'
                            }
                        },
                    'Competitive':
                        {
                        'Time Played':
                            {
                            'Hanzo': '09:16:39',
                            'McCree': '07:30:55',
                            'Ana': '05:45:00',
                            'Reinhardt': '03:29:21',
                            'Zarya': '02:34:45',
                            'Reaper': '02:00:44',
                            'D.Va': '01:38:50',
                            'Junkrat': '01:32:48',
                            'Soldier: 76': '01:26:36',
                            'Pharah': '01:22:36',
                            'Symmetra': '01:18:11',
                            'Orisa': '01:11:50',
                            'Widowmaker': '01:08:38',
                            'Moira': '54:34',
                            'Zenyatta': '48:53',
                            'Baptiste': '48:10',
                            'Winston': '44:28',
                            'Bastion': '43:48',
                            'Roadhog': '37:42',
                            'Mei': '31:50',
                            'Lúcio': '30:54',
                            'Torbjörn': '25:51',
                            'Brigitte': '18:47',
                            'Tracer': '06:50',
                            'Sombra': '04:59',
                            'Mercy': '02:13',
                            'Ashe': '02:10',
                            'Genji': '00:59',
                            'Wrecking Ball': '10:00'
                            }
                        }
                    }
PRIVATE = {
          'Public': False,
          'Icon': 'input/icons/Icon.png',
          'Level':
              {
              'Border': 'input/icons/Border.png',
              'Value': 91
              },
          'Endorsment':
              {
              'Level': 3,
              'Shot Caller': 15,
              'Good Teammate': 50,
              'Sportsmanship': 34
              },
          'Tag': 'AbCdEfGhIjK#21855'
          }
PRIVATE_TO_PUBLIC = {
                    'Endorsment':
                        {
                        'Good Teammate': '56 (+6)',
                        'Level': '3',
                        'Shot Caller': '21 (+6)',
                        'Sportsmanship': '23 (-11)'
                        },
                    'Icon': 'input/icons/Icon.png',
                    'Level':
                        {
                        'Border': 'input/icons/Border.png',
                        'Rank': 'input/icons/Rank.png',
                        'Value': '1 (+10)'
                        },
                    'Public': True,
                    'Tag': 'AbCdEfGhIjK#21855'
                    }
PUBLIC_TO_PRIVATE = {
                    'Endorsment':
                        {
                        'Good Teammate': '50 (-6)',
                        'Level': '3',
                        'Shot Caller': '15 (-6)',
                        'Sportsmanship': '34 (+11)'
                        },
                    'Icon': 'input/icons/Icon.png',
                    'Level':
                        {
                        'Border': 'input/icons/Border.png',
                        'Value': '91 (+90)'
                        },
                    'Public': False,
                    'Tag': 'AbCdEfGhIjK#21855'
                    }

EXTRACTED = {
                    'Public': True,
                    'Competitive':
                        {
                        'Ana': datetime.timedelta(0, 468),
                        'Genji': datetime.timedelta(0, 59),
                        'McCree': datetime.timedelta(0, 125),
                        'Wrecking Ball': datetime.timedelta(0, 600)},
                    'Endorsment':
                        {
                        'Good Teammate': '56',
                        'Level': '3 (-1)',
                        'Shot Caller': '21 (+2)',
                        'Sportsmanship': '23 (-1)'
                        },
                    'Icon': 'input/icons/Icon.png',
                    'Level':
                        {
                        'Border': 'input/icons/Border.png',
                        'Rank': 'input/icons/Rank_3.png',
                        'Value': '1 (+2)'
                        },
                    'Quickplay':
                        {
                        'Ana': datetime.timedelta(0, 986),
                        'Doomfist': datetime.timedelta(0, 492),
                        'Hanzo': datetime.timedelta(0, 245),
                        'McCree': datetime.timedelta(0, 64),
                        'Moira': datetime.timedelta(0, 187),
                        'Pharah': datetime.timedelta(0, 227)
                        },
                    'Tag': 'AbCdEfGhIjK#21855',
                    'Rank':
                        {
                        'Icon': 'input/icons/CP_rank.png',
                        'Value': '2524 (+2524)'
                        }
                    }
EXTRACTED_1 = {
                    'Public': True,
                    'Endorsment':
                        {
                        'Good Teammate': '56 (-1)',
                        'Level': '3 (-1)',
                        'Shot Caller': '21 (+2)',
                        'Sportsmanship': '23 (-1)'
                        },
                    'Icon': 'input/icons/Icon.png',
                    'Level':
                        {
                        'Border': 'input/icons/Border.png',
                        'Value': '100 (+10)'
                        },
                    'Quickplay':
                        {
                        'Ana': datetime.timedelta(0, 986),
                        'Doomfist': datetime.timedelta(0, 492),
                        'Hanzo': datetime.timedelta(0, 245),
                        'McCree': datetime.timedelta(0, 64),
                        'Moira': datetime.timedelta(0, 187),
                        'Pharah': datetime.timedelta(0, 227)
                        },
                    'Tag': 'AbCdEfGhIjK#21855',
                    }
EXTRACTED_2 = {
                    'Public': False,
                    'Endorsment':
                        {
                        'Good Teammate': '56',
                        'Level': '3',
                        'Shot Caller': '21',
                        'Sportsmanship': '23'
                        },
                    'Icon': 'input/icons/Icon.png',
                    'Level':
                        {
                        'Border': 'input/icons/Border_3.png',
                        'Value': '1 (+2)'
                        },
                    'Rank':
                        {
                            'Icon': 'input/icons/CP_rank_2.png',
                            'Value': '2530 (+6)'
                        },
                    'Tag': 'AbCdEfGhIjK#21855'
                    }

OLD_FILE = 'input/old.html'
NEW_FILE = 'input/new.html'
BROKEN_PORTRAIT_FILE = 'input/broken_portrait.html'
NO_PORTRAIT_FILE = 'input/no_portrait.html'
PRIVATE_FILE = 'input/PRIVATE.html'

POST = 'output/post.png'
RANK = 'output/rank.png'
LEVEL = 'output/level.png'
POST_1 = 'output/post_1.png'
LEVEL_1 = 'output/level_1.png'
POST_2 = 'output/post_2.png'


class ParserTestCase(u.TestCase):
    def setUp(self) -> None:
        self.rc = asyncio.get_event_loop().run_until_complete

    def parse_local(self, state, name):
        with open(name, 'r', encoding='utf-8') as f:
            soup = bs4.BeautifulSoup(f.read(), 'lxml')
        parsed = self.rc(e.parse_soup(state, soup))
        if parsed:
            parsed['Tag'] = 'AbCdEfGhIjK#21855'
        return parsed

    def check_keys_recursively(self, src, dst):
        src_keys = set(src.keys())
        dst_keys = set(dst.keys())
        self.assertSetEqual(src_keys, dst_keys, f'\nSrc: {src_keys}\nDst: {dst_keys}')
        for k, v in src.items():
            if type(v) is dict:
                self.check_keys_recursively(src[k], dst[k])
            elif not isinstance(v, BytesIO):
                self.assertEqual(v, dst[k])

    def check_data(self, src, dst):
        self.check_keys_recursively(src, dst)

    def test_old_data(self):
        parsed = self.parse_local(True, OLD_FILE)
        self.check_data(parsed, OLD)

    def test_new_data(self):
        parsed = self.parse_local(True, NEW_FILE)
        self.check_data(parsed, NEW)

    def test_broken_portrait(self):
        parsed = self.parse_local(True, BROKEN_PORTRAIT_FILE)
        self.assertIsNone(parsed)
        parsed = self.parse_local(False, BROKEN_PORTRAIT_FILE)
        self.assertIsNone(parsed)

    def test_no_portrait(self):
        parsed = self.parse_local(True, NO_PORTRAIT_FILE)
        self.assertIsNone(parsed)
        parsed = self.parse_local(False, NO_PORTRAIT_FILE)
        self.assertIsNone(parsed)

    def test_private(self):
        parsed = self.parse_local(False, PRIVATE_FILE)
        self.check_data(parsed, PRIVATE)

    def test_extractor(self):
        tocheck = e.extract(OLD, NEW)
        self.check_data(tocheck, EXTRACTED)

    def test_private_to_public(self):
        tocheck = e.extract(PRIVATE, PUBLIC)
        self.check_data(tocheck, PRIVATE_TO_PUBLIC)

    def test_public_to_private(self):
        tocheck = e.extract(PUBLIC, PRIVATE)
        self.check_data(tocheck, PUBLIC_TO_PRIVATE)


class PlotTestCase(u.TestCase):
    def setUp(self) -> None:
        pass

    def test_plot(self):
        rank = p.make_rank(EXTRACTED['Rank'])
        rank.save(RANK)
        self.assertTrue(True, 'Failed to make image for rank')

        level = p.make_level(EXTRACTED['Level'])
        level.save(LEVEL)
        self.assertTrue(True, 'Failed to make image for level')

        post = p.make_post(EXTRACTED)
        post.save(POST)
        self.assertTrue(True, 'Failed to make image for post')

    def test_plot_1(self):
        level = p.make_level(EXTRACTED_1['Level'])
        level.save(LEVEL_1)
        self.assertTrue(True, 'Failed to make image for level')

        post = p.make_post(EXTRACTED_1)
        post.save(POST_1)
        self.assertTrue(True)

    def test_plot_2(self):
        post = p.make_post(EXTRACTED_2)
        post.save(POST_2)
        self.assertTrue(True)


if __name__ == '__main__':
    u.main()
