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
    
    firstnames = ['anders','bente', 'cordelia', 'dennis','egon',
             'filip','gudrun','holli','inge','jakob',
             'kurt', 'lone', 'molly', 'neil', 'ove',
             'pia', 'quentin', 'rasmus', 'sussy', 'tove',
             'ulrik', 'vera', 'xerxes', 'yrsa', 'zoro'
             ]
    surnames = ['andersen', 'bruun', 'christensen', 'dahl','eg',
             'frederiksen','godtfredsen','hansen','ipsen','jakobsen',
             'kurtsen', 'lidegaard', 'madsen', 'nielsen', 'olsen',
             'poulsen', 'quist', 'rasmussen', 'sørensen', 'thomsen'
            ]  
    bios0 = ['kind', 'brave', 'sad',
             'quiet', 'happy', 'happy-go-lucky', 'not so elegant', 'lazy',
             'creative', 'curious', 'optimistic', 
             'chaotic', 'restless', 'inddecisive',
             'confused', 'recovering', 'tired but trying',
             'mostly harmless', 'sleepy', 'soft', 'cheerful', 'unconventional'
             ]
    bios1 = ['hiking', 'coffee', 'book', 'film', 'cat',
             'basket', 'gym', 'food', 'music', 'travel',
             'computer', 'morning', 'evening', 'everyday', 'energy',
             'chaos', 'main character', 'life', 'lifestyle',
             'tv', 'routine', 'garden', 'knitting', 'water', 'zoo', 'nature',
             'architecture', 
            ]
    bios2 = ['lover', 'addict', 'agent', 'fan', 'scholar', 'collector',
             'nerd', 'person', 'professional', 'coach', 'persona', 'observer',
             'connoisseur'
            ]
    bios3 = [' gone wrong', ' at heart', ' in training', ' in denial',
             '', '', '', '', '', '', '', '', '', '', '', '', '', ''
            ]
    bios4 = ['loves', 'adores', 'dislikes', 'fond of', 'prefers', 'loves', 'believes in',
             'likes', 'is done with', 'will defend', 'gave up on', 'never understood',
              'is obsessed with', 'is suspicios of', 'is here for', 'has strong opinions on'
            ]   
    bios5 = ['sunshine', 'discipline', 'copenhagen', 'funny hats', 'high standards', 'high goals', 'bad jokes',
             'kindness', 'a cozy mind', 'mindfulness', 'peaceful mornings', 'sleeping', 'singing',
             'big dreams', 'kindness', 'learning', 'boring content', 'pretty things',
             'photos', 'inspirational quotes', 'painting', 'overthinking', 'airplane mode', 'good company',
             'country music', 'politics', 'park life', 'a good laugh', 'ufos', 'birds', 'fishing', 'fitness'
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
    

    profiles = [(i, f"{firstnames[i % len(firstnames)]} {random.choice(surnames)}",
                 f"{random.choice(bios0)} {random.choice(bios1)} {random.choice(bios2)}{random.choice(bios3)}, {random.choice(bios4)} {random.choice(bios5)}",
                 random.choice(zodiacs)) for i in range(1, n+1)]
    raw_users = [(i, f"{firstnames[i % len(firstnames)]}_{i}@mail.com", f"password{i}") for i in range(1, n+1)]
    zodiac_lookup = {id:zodiac for id, name , bio, zodiac in profiles}
    likes = [
        (liker, liked, random.choice([0, 1]))
        for liker, liked in [(i, 1) for i in range(2, n+1)] + [(1, i) for i in range(2, n+1) if i%2 == 0]
        if (zodiac_lookup[liker], zodiac_lookup[liked]) in valid_matches
    ]
    return  raw_users, profiles, likes

# raw_users, profiles, likes = generate_users(100)
# print ([(b, c) for a, b, c, d in profiles])




    
