import random

def generate_users (n:int):
    random.seed(42)
    zodiacs = ['Aries',
        'Taurus',
        'Gemini',
        'Cancer',
        'Leo',
        'Virgo',
        'Libra',
        'Scorpio',
        'Sagittarius',
        'Capricorn',
        'Aquarius',
        'Pisces']
    names = ['anders',
             'bente',
             'cordelia',
             'dennis',
             'egon',
             'filip',
             'gudrun',
             'holli',
             'inge',
             'jakob',
             'kurt'
             ]
    bios1 = ['hiking',
            'coffee',
            'book',
            'film',
            'cat',
            'basket',
            'gym',
            'food',
            'music',
            'travel',
            'computer'
    ]
    bios2 = ['lover',
             'addict',
             'worm',
             'nerd',
             'person',
    ]
    valid_matches = [('Aries', 'Leo'),
        ('Aries', 'Sagittarius'),
        ('Taurus', 'Virgo'),
        ('Taurus', 'Capricorn'),
        ('Gemini', 'Libra'),
        ('Gemini', 'Aquarius'),
        ('Cancer', 'Scorpio'),
        ('Cancer', 'Pisces'),
        ('Leo', 'Aries'),
        ('Leo', 'Sagittarius'),
        ('Virgo', 'Capricorn'),
        ('Virgo', 'Taurus'),
        ('Libra', 'Gemini'),
        ('Libra', 'Aquarius'),
        ('Scorpio', 'Cancer'),
        ('Scorpio', 'Pisces'),
        ('Sagittarius', 'Aries'),
        ('Sagittarius', 'Leo'),
        ('Capricorn', 'Taurus'),
        ('Capricorn', 'Virgo'),
        ('Aquarius', 'Gemini'),
        ('Aquarius', 'Libra'),
        ('Pisces', 'Cancer'),
        ('Pisces', 'Scorpio')]
    
    
    profiles = [(i, names[i % len(names)], f"{random.choice(bios1)} {random.choice(bios2)} bla bla bla", random.choice(zodiacs)) for i in range(1, n+1)]
    raw_users = [(i, f"{names[i % len(names)]}_{i}@mail.com", f"password{i}") for i in range(1, n+1)]
    zodiac_lookup = {id:zodiac for id, name , bio, zodiac in profiles}
    # likes = [(i, 1, random.choice(likes_status)) for i in range(2,n+1)]+[(1, i, random.choice(likes_status)) for i in range(2,n+1) if i%2 == 0]
    likes = [
        (liker, liked, random.choice([0, 1]))
        for liker, liked in [(i, 1) for i in range(2, n+1)] + [(1, i) for i in range(2, n+1) if i%2 == 0]
        if (zodiac_lookup[liker], zodiac_lookup[liked]) in valid_matches
    ]
    return  raw_users, profiles, likes




    
