from PIL import Image, ImageFont, ImageDraw

# POST
POST_COLOR = (255, 255, 255, 0)
POST_SIZE_FULL = (650, 550)
POST_SIZE_PART = (650, 275)

# ICON
ICON_POS = (10, 10)
ICON_SIZE = (96, 96)

# TAG
STATUS_POS = (115, 10)
TAG_POS = (115, 45)

# LEVEL
LVL_POS = (0, 120)  # IN POST
DEF_LVL_SIZE = (256, 256)
LVL_SIZE = (150, 150)
BORDER_CROP = (0, 10, *DEF_LVL_SIZE)
RANK_POS = (0, 128)
LVL_TEXT_POS = (75, 65)

# RANK
CP_RANK_POS = (165, 120)  # IN POST
CP_ICON_SIZE = (80, 80)
CP_ICON_POS = (24, 20)
CP_VALUE_POS = (64, 104)
CP_COMP_SIZE = (128, 140)

# ENDORSMENT
ENDORSMENT_POS = (330, 120)  # IN POST
ENDORSMENT_POS_NO_RANK = CP_RANK_POS  # IN POST
ENDORSMENT_SIZE = (300, 160)
ENDOSMENT_SPACING = 16
ENDORSMENT_VAL_OFFSET = 200

# TIME PLAYED
LEFT_TP_POS = (10, 280)  # IN POST
RIGHT_TP_POS = (330, 280)  # IN POST


# TEXT
def get_text_size(font, text='A'):
    comp = Image.new('RGBA', (10, 10))
    draw = ImageDraw.Draw(comp)
    return draw.textsize(text, font)


TEXT_COLOR = (255, 255, 255, 255)
OUTLINE = (0, 0, 0, 255)
FONT_PATH = 'Overwatch.ttf'
STATUS_FONT = ImageFont.truetype(FONT_PATH, size=30)
TAG_FONT = ImageFont.truetype(FONT_PATH, size=64)
LEVEL_FONT = ImageFont.truetype(FONT_PATH, size=25)
CP_RANK_FONT = ImageFont.truetype(FONT_PATH, size=28)
ENDORSMENT_FONT = ImageFont.truetype(FONT_PATH, size=35)
ENDORSMENT_FONT_HEIGHT, _ = get_text_size(ENDORSMENT_FONT)
ENDORSMENT_COLOURS = {
    'Shot Caller': (241, 149, 18, 255),
    'Good Teammate': (200, 26, 245, 255),
    'Sportsmanship': (64, 206, 68, 255)
}


def text_outline(draw, xy, text, fill=None, outline=None, font=None):
    if outline:
        draw.text((xy[0]-1, xy[1]-1), text, outline, font)
        draw.text((xy[0]+1, xy[1]-1), text, outline, font)
        draw.text((xy[0]+1, xy[1]+1), text, outline, font)
        draw.text((xy[0]-1, xy[1]+1), text, outline, font)
    draw.text(xy, text, fill, font)


def make_level(level):
    comp = Image.new('RGBA', DEF_LVL_SIZE)
    border = Image.open(level['Border'])
    border = border.crop(BORDER_CROP)
    comp.alpha_composite(border)
    if 'Rank' in level:
        rank = Image.open(level['Rank'])
        comp.alpha_composite(rank, RANK_POS)
    comp.thumbnail(LVL_SIZE)

    # Level
    draw = ImageDraw.Draw(comp)
    text = level['Value']
    level_size = draw.textsize(text, font=LEVEL_FONT)
    level_pos = (LVL_TEXT_POS[0]-level_size[0]/2,
                 LVL_TEXT_POS[1]-level_size[1]/2)
    text_outline(draw, level_pos, text, fill=TEXT_COLOR, outline=OUTLINE, font=LEVEL_FONT)
    return comp


def make_rank(rank):
    icon = Image.open(rank['Icon'])
    icon.thumbnail(CP_ICON_SIZE)

    text = rank['Value']
    value_size = get_text_size(CP_RANK_FONT, text)
    value_pos = (CP_VALUE_POS[0]-value_size[0]/2, CP_VALUE_POS[1])

    comp = Image.new('RGBA', CP_COMP_SIZE)
    draw = ImageDraw.Draw(comp)
    comp.alpha_composite(icon, CP_ICON_POS)
    text_outline(draw, value_pos, text, TEXT_COLOR, OUTLINE, CP_RANK_FONT)
    return comp


def make_endorsment(endorsment):
    comp = Image.new('RGBA', ENDORSMENT_SIZE)
    draw = ImageDraw.Draw(comp)

    h_pos = 0
    text = f'{"Endorsment Level"}: {endorsment["Level"]}'
    text_outline(draw, (0, h_pos), text, TEXT_COLOR, OUTLINE, ENDORSMENT_FONT)

    temp = endorsment.pop('Level')  # remove level data to print the rest
    for k, v in endorsment.items():
        h_pos += ENDORSMENT_FONT_HEIGHT + ENDOSMENT_SPACING
        name = f'{k}: '
        text_outline(draw, (0, h_pos), name, TEXT_COLOR, OUTLINE, ENDORSMENT_FONT)
        text_outline(draw, (ENDORSMENT_VAL_OFFSET, h_pos), v, ENDORSMENT_COLOURS[k], OUTLINE, ENDORSMENT_FONT)
    endorsment['Level'] = temp  # make sure this function doesn't change provided data
    return comp


def make_hero_icon(name, scale=0.6, background=(199, 199, 199, 255)):
    src = Image.open(name)
    src = src.convert('RGBA')
    size = int(src.height*scale)
    src = src.resize((size, size))
    size = (int(src.width*scale), int(src.height*scale))
    src.thumbnail(size)
    comp = Image.new('RGBA', size, background)
    comp.alpha_composite(src)
    return comp


def make_bars(diff, mode, fontsize=30, spacing=8, width=300):
    # Prepare the data
    pairs = diff[mode]
    pairs = sorted(pairs.items(), key=lambda x: x[1], reverse=True)
    heroes = [x[0] for x in pairs]
    time_labels = [f'+{x[1]}' for x in pairs]
    max_val = pairs[0][1].total_seconds()
    time_vals = [x[1].total_seconds()/max_val for x in pairs]
    thumbs = []
    for hero in heroes:
        # Filename can't have : in Windows OS
        if hero == 'Soldier: 76':
            hero = 'Soldier 76'
        thumbs.append(make_hero_icon(f'heroes/{hero}.png'))
    rows = len(heroes)

    # Making top 5
    if rows > 5:
        rows = 5
        heroes = heroes[:5]
        time_labels = time_labels[:5]
        time_vals = time_vals[:5]

    # Calculate image size
    font = ImageFont.truetype(FONT_PATH, size=fontsize + 10)
    _, text_height = get_text_size(font)
    thumb_height = thumbs[0].height
    thumb_width = thumbs[0].width
    height = 5*(thumb_height + spacing) + text_height + spacing
    comp = Image.new('RGBA', (width, height))
    draw = ImageDraw.Draw(comp)

    # Draw title
    text_outline(draw, (0, 0), mode, TEXT_COLOR, OUTLINE, font)
    pos = text_height + spacing

    # Draw thumbs, bars and labels
    font = ImageFont.truetype(FONT_PATH, size=fontsize)
    bar_color = (30, 120, 180, 255)
    for i in range(0, rows):
        comp.alpha_composite(thumbs[i], (0, pos))
        text_width, text_height = get_text_size(font, time_labels[i])
        rectangle = [thumb_width, pos,
                     (width-thumb_width)*time_vals[i]+thumb_width, pos+thumb_height]
        left_label = (rectangle[0] + 5, pos + (rectangle[3] - rectangle[1] - text_height) / 2)
        right_label = (width - text_width - 5, left_label[1])
        draw.rectangle(rectangle, fill=bar_color)
        text_outline(draw, left_label, heroes[i], TEXT_COLOR, OUTLINE, font)
        text_outline(draw, right_label, time_labels[i], TEXT_COLOR, OUTLINE, font)
        pos += thumb_height + spacing
    return comp


def make_post(diff):
    if 'Quickplay' in diff or 'Competitive' in diff:
        post_size = POST_SIZE_FULL
    else:
        post_size = POST_SIZE_PART

    post = Image.new('RGBA', post_size, color=POST_COLOR)
    draw = ImageDraw.Draw(post)

    # Player icon
    icon = Image.open(diff['Icon'])
    icon.thumbnail(ICON_SIZE)
    post.paste(icon, box=ICON_POS)

    # Battletag
    status = f'{"Public" if diff["Public"] else "Private"} Profile'
    text_outline(draw, STATUS_POS, status, fill=TEXT_COLOR, outline=OUTLINE, font=STATUS_FONT)
    text_outline(draw, TAG_POS, diff['Tag'], fill=TEXT_COLOR, outline=OUTLINE, font=TAG_FONT)

    # Level
    level = make_level(diff['Level'])
    post.alpha_composite(level, LVL_POS)

    # Rank
    if 'Rank' in diff:
        rank = make_rank(diff['Rank'])
        post.alpha_composite(rank, CP_RANK_POS)
        endorsment_pos = ENDORSMENT_POS
    else:
        endorsment_pos = ENDORSMENT_POS_NO_RANK

    # Endorsment
    endorsment = make_endorsment(diff['Endorsment'])
    post.alpha_composite(endorsment, endorsment_pos)

    # Time played
    if 'Quickplay' in diff and 'Competitive' in diff:
        qp = make_bars(diff, 'Quickplay')
        post.alpha_composite(qp, LEFT_TP_POS)

        cp = make_bars(diff, 'Competitive')
        post.alpha_composite(cp, RIGHT_TP_POS)
    elif 'Quickplay' in diff:
        qp = make_bars(diff, 'Quickplay', width=600)
        post.alpha_composite(qp, LEFT_TP_POS)
    elif 'Competitive' in diff:
        cp = make_bars(diff, 'Competitive', width=600)
        post.alpha_composite(cp, LEFT_TP_POS)
    return post
