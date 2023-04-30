def get_most_played(hypixel_data_bedwars):
    solos = hypixel_data_bedwars.get('eight_one_games_played_bedwars', 0)
    doubles = hypixel_data_bedwars.get('eight_two_games_played_bedwars', 0)
    threes = hypixel_data_bedwars.get('four_three_games_played_bedwars', 0)
    fours =  hypixel_data_bedwars.get('four_four_games_played_bedwars', 0)
    findgreatest = {
        'Solos': solos,
        'Doubles': doubles,
        'Threes':  threes,
        'Fours': fours
    }
    return "N/A" if max(findgreatest.values()) == 0 else str(max(findgreatest, key=findgreatest.get))

def get_player_rank_info(hypixel_data):
    name = hypixel_data.get('displayname')
    rank_info = {
        'rank': hypixel_data.get('rank', 'NONE') if name != "Technoblade" else "TECHNO",
        'packageRank': hypixel_data.get('packageRank', 'NONE'),
        'newPackageRank': hypixel_data.get('newPackageRank', 'NONE'),
        'monthlyPackageRank': hypixel_data.get('monthlyPackageRank', 'NONE'),
        'rankPlusColor': hypixel_data.get('rankPlusColor', None) if name != "Technoblade" else "AQUA"
    }
    return rank_info

def get_level(xp):
    level = 100 * (xp // 487000) # prestige
    xp %= 487000 # exp this prestige
    xp_map = (0, 500, 1500, 3500, 7000)

    for index, value in enumerate(xp_map):
        if xp < value:
            factor = xp_map[index-1]
            return level + ((xp - factor) / (value - factor)) + (index -1)
    return level + (xp - 7000) / 5000 + 4

def get_progress(hypixel_data_bedwars):
    bedwars_level = get_level(hypixel_data_bedwars.get('Experience', 0))

    remainder = int(str(int(bedwars_level) / 100).split(".")[-1])
    remainder_map = {0: 500, 1: 1000, 2: 2000, 3: 3500}

    target = remainder_map.get(remainder, 5000)
    progress = float('.' + str(bedwars_level).split('.')[-1]) * target
    devide_by = target / 10
    progress_out_of_ten = round(progress / devide_by)

    return f'{int(progress):,}', f'{int(target):,}', progress_out_of_ten