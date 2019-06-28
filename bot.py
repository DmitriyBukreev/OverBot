from discord.ext import commands
from discord import File, Game
import sqlite3 as db
import asyncio
import pickle
from io import BytesIO
import tools.extractor as e
from tools.extractor import log
import tools.plot as p
from datetime import datetime

TOKEN = None
PREFIX = '!'
DATABASE = 'trackers.db'


def get_file_to_send(image):
    filelike = BytesIO()
    image.save(filelike, format='png')
    filelike.seek(0)
    return filelike


class CustomBot(commands.Bot):
    @staticmethod
    @commands.command()
    async def track(ctx, tag):
        tag = '-'.join(tag.split('#'))
        public, res = await e.check_profile(tag)

        if not res:
            log.info(f'Failed to start track for {tag} at {ctx.channel}')
            await ctx.send(f"Can't get profile page for {tag}")
            return

        log.info(f'Started tracking for {tag} at {ctx.channel}')
        if public:
            await ctx.send(f'Started tracking for {tag} in this channel')
        else:
            await ctx.send(f'Started tracking for {tag} in this channel\n'
                           f'But profile is private')
        ctx.bot.add_tracker(ctx.channel.id, tag)


    @staticmethod
    @commands.command()
    async def untrack(ctx, tag):
        tag = '-'.join(tag.split('#'))
        if ctx.bot.is_tracked(tag):
            ctx.bot.remove_tracker(ctx.channel.id, tag)
            log.info(f'No longer tracking {tag} at {ctx.channel}')
            await ctx.send(f'No longer tracking {tag} in this channel')
        else:
            log.info(f"Tag {tag} wasn't tracked before")
            await ctx.send(f"Tag {tag} wasn't tracked before")

    async def on_command_error(self, ctx, exception):
        log.exception(exception)
        await ctx.send(exception)

    def add_tracker(self, id, tag):
        self.updater.execute("""INSERT OR IGNORE INTO trackers (id, tag)
                                VALUES (?, ?)""", (id, tag))
        self.updater.execute("""INSERT OR IGNORE INTO infos (tag)
                                VALUES (?)""", (tag,))
        self.db.commit()

    def remove_tracker(self, id, tag):
        self.updater.execute("""DELETE FROM trackers
                                WHERE id=? AND tag=?""", (id, tag))
        self.db.commit()

    def get_infos(self):
        return self.iterator.execute('SELECT tag, info FROM infos')

    def is_tracked(self, tag):
        self.iterator.execute('SELECT * FROM trackers WHERE tag=?', (tag,))
        if self.iterator.fetchone():
            return True
        else:
            return False

    def get_channels(self, tag):
        return self.updater.execute('SELECT id FROM trackers WHERE tag=?', (tag,))

    def update_info(self, tag, info):
        self.updater.execute("""UPDATE infos 
                                SET info=?, last_update=?
                                WHERE tag=?""", (info, datetime.now(), tag))
        self.db.commit()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize commands
        self.add_command(self.track)
        self.add_command(self.untrack)

        # Create and connect to database
        self.db = db.connect(DATABASE)
        self.iterator = self.db.cursor()
        self.updater = self.db.cursor()
        self.updater.executescript(
            ''' CREATE TABLE IF NOT EXISTS trackers (
                id INTEGER,
                tag TEXT,
                PRIMARY KEY (id, tag));

                CREATE TABLE IF NOT EXISTS infos (
                tag TEXT,
                info BLOB DEFAULT NULL,
                amount INTEGER DEFAULT 1,
                last_update date,
                PRIMARY KEY (tag));
                
                CREATE TRIGGER IF NOT EXISTS add_tracker AFTER INSERT ON trackers
                BEGIN
                    UPDATE infos SET amount=amount+1 WHERE infos.tag=NEW.tag;
                END;
                
                CREATE TRIGGER IF NOT EXISTS remove_tracker AFTER DELETE ON trackers
                BEGIN
                    UPDATE infos SET amount=amount-1 WHERE infos.tag=OLD.tag;
                END;
                
                CREATE TRIGGER IF NOT EXISTS remove_info AFTER UPDATE ON infos WHEN NEW.amount=0
                BEGIN
                    DELETE FROM infos WHERE infos.tag=NEW.tag;
                END;
            ''')
        self.num_accounts = self.iterator.execute('SELECT COUNT(*) FROM infos').fetchone()[0]
        self.loop.create_task(self.task())

    async def task(self):
        try:
            await self.background()
        except:
            log.exception('Error occured in background task')

    async def aw_process_tracker(self, tag, info):
        try:
            await self.process_tracker(tag, info)
        except:
            log.exception(f'Error occured while processing tracker for {tag}')

    async def send_posts(self, post, channel_id):
        try:
            channel = self.get_channel(*channel_id)
            await channel.send(file=File(post, filename='stats.png'))
            post.seek(0)
        except:
            log.exception(f'Error occured while sending post to {channel_id}')

    async def process_tracker(self, tag, info):
        await self.change_presence(activity=Game(f'Checking...'))
        if not info:
            log.info(f'Retrieving info about {tag} for the first time')
            old_info = await e.parse(tag)
            if old_info is None:
                log.error('Failed to retrieve info')
                return
            e.log_parsed(old_info, 'NEW')
            info = pickle.dumps(old_info)
            self.update_info(tag, info)
        else:
            old_info = pickle.loads(info)
            e.log_parsed(old_info, 'OLD')

            new_info = await e.parse(tag)
            if new_info is None:
                log.error('Failed to retrieve info')
                return
            e.log_parsed(new_info, 'NEW')
            diff = e.extract(old_info, new_info)
            if diff:
                e.log_extracted(diff)
                info = pickle.dumps(new_info)
                self.update_info(tag, info)
                img = p.make_post(diff)
                post = get_file_to_send(img)
                awaitables = [self.send_posts(post, channel_id) for channel_id in self.get_channels(tag)]
                await asyncio.wait(awaitables)
            else:
                log.info(f'No updates for {tag}')

    async def background(self):
        sleeptime = 60
        await self.wait_until_ready()
        log.info('Tracking initialized')
        while True:
            cursor = self.get_infos()
            infos = cursor.fetchmany(size=100)
            while infos:
                awaitables = [self.aw_process_tracker(tag, info) for tag, info in infos]
                await asyncio.wait(awaitables)
                infos = cursor.fetchmany(size=100)
            log.info('Going to sleep... Zzz...')
            await self.change_presence(activity=Game('Sleeping...'))
            await asyncio.sleep(sleeptime)


if __name__ == '__main__':
    bot = CustomBot(PREFIX)
    bot.run(TOKEN)
