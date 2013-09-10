"""
Creates the civilopedia_v.css file based on icons and portraits

This file is created from the Civ5 game databases Civ5DebugDatabase.db
This file is typically stored in ~/My Documents/My Games/Civilization V/cache

This script is intended to run with Python2.7
"""

import os

import civ5


OUTCSS = '''.{key} {{
    background: transparent url({filename}) -{xpos}px -{ypos}px no-repeat;
}}
'''

FONT_ICONS_SQL = '''
  SELECT
    IconName AS "key",
    IconMapping AS "position",
    LOWER(IconFontTextureFile) AS "filename"
  FROM IconFontMapping ifm
    INNER JOIN IconFontTextures ift
      ON ifm.IconFontTexture = ift.IconFontTexture
  ORDER BY IconFontTextureFile, IconMapping
'''

TECHNOLOGY_ICONS_SQL = '''
  SELECT
    Type AS "key",
    PortraitIndex AS "position",
    LOWER(Filename) AS "filename",
    IconsPerRow,
    IconsPerColumn
  FROM Technologies
    INNER JOIN IconTextureAtlases
      ON Atlas = IconAtlas
  WHERE IconSize = 256
  ORDER BY Cost
'''

def create_css(db_dir, outfile='civilopedia_v.css'):
    # Initialize gamedata database
    game_db = civ5.GamedataDB(
        os.path.join(db_dir, civ5.DATABASES['Gamedata']))

    with open(outfile, 'w') as writer:
        with game_db.conn:
            for row in game_db.conn.execute(FONT_ICONS_SQL):
                xpos = int((row['position'] - 1) % 11) * 22
                ypos = int((row['position'] - 1) / 11) * 22
                writer.write(OUTCSS.format(key=row['key'],
                                           filename=row['filename'] + '.png',
                                           xpos=xpos, ypos=ypos))
            for row in game_db.conn.execute(TECHNOLOGY_ICONS_SQL):
                xpos = int(row['position'] % int(row['IconsPerRow'])) * 256
                ypos = int(row['position'] / int(row['IconsPerRow'])) * 256
                writer.write(OUTCSS.format(key=row['key'],
                                           filename=row['filename'].replace('.dds', '.png'),
                                           xpos=xpos, ypos=ypos))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=
                                     'Create the civilopedia CSS.')
    parser.add_argument('--cachedir', dest='cachedir', required=True,
                        help='Path to the cache directory containing *.db')
    args = parser.parse_args()

    #  Perform a sanity check that the databases exist
    for fn in civ5.DATABASES.values():
        path = os.path.join(args.cachedir, fn)
        if not os.path.isfile(path):
            parser.error('{} not found in {}'.format(path, args.cachedir))

    create_css(args.cachedir)