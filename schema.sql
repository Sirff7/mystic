DROP TABLE IF EXISTS Paired_with;
DROP TABLE IF EXISTS Likes;
DROP TABLE IF EXISTS Matches;
DROP TABLE IF EXISTS Profiles;
DROP TABLE IF EXISTS Zodiacs;
DROP TABLE IF EXISTS Sessions;
DROP TABLE IF EXISTS Users;


CREATE TABLE Users
    (user_id SERIAL,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    PRIMARY KEY (user_id));

CREATE TABLE Sessions
    (user_id INT,
    token UUID DEFAULT gen_random_uuid(),
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, token),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
        ON DELETE CASCADE);

CREATE TABLE Zodiacs
    (zodiac_name VARCHAR(20),
    PRIMARY KEY (zodiac_name));

CREATE TABLE Profiles
    (profile_id INT,
    display_name VARCHAR(255),
    bio VARCHAR(1000),
    zodiac VARCHAR(20),
    PRIMARY KEY (profile_id),
    FOREIGN KEY (profile_id) REFERENCES Users(user_id)
        ON DELETE CASCADE,
    FOREIGN KEY (zodiac) REFERENCES Zodiacs(zodiac_name)
        ON DELETE NO ACTION);

CREATE TABLE Matches
    (zodiac_1 VARCHAR(20),
    zodiac_2 VARCHAR(20),
    PRIMARY KEY (zodiac_1, zodiac_2),
    FOREIGN KEY (zodiac_1) REFERENCES Zodiacs(zodiac_name)
        ON DELETE CASCADE,
    FOREIGN KEY (zodiac_2) REFERENCES Zodiacs(zodiac_name)
        ON DELETE CASCADE);

CREATE TABLE Likes
    (liker INT,
    liked INT,
    likes_status INT NOT NULL,
    PRIMARY KEY (liker, liked),
    FOREIGN KEY (liker) REFERENCES Profiles(profile_id)
        ON DELETE CASCADE,
    FOREIGN KEY (liked) REFERENCES Profiles(profile_id)
        ON DELETE CASCADE);

CREATE TABLE Paired_with
    (profile_1 INT,
    profile_2 INT,
    PRIMARY KEY (profile_1, profile_2),
    FOREIGN KEY (profile_1) REFERENCES Profiles(profile_id)
        ON DELETE CASCADE,
    FOREIGN KEY (profile_2) REFERENCES Profiles(profile_id)
        ON DELETE CASCADE);

CREATE OR REPLACE FUNCTION check_mutual_likes()
RETURNS TRIGGER AS $$
BEGIN
    IF
    NEW.likes_status=1 AND EXISTS (
        SELECT 1 FROM Likes
        WHERE liker=NEW.liked
        AND liked=NEW.liker
        AND likes_status=1
        ) THEN
            INSERT INTO Paired_with (profile_1, profile_2)
            VALUES (NEW.liker, NEW.liked);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER create_couple_trigger 
AFTER INSERT ON Likes
FOR EACH ROW 
EXECUTE FUNCTION check_mutual_likes();

INSERT INTO Zodiacs(zodiac_name)
VALUES  ('Aries'),
        ('Taurus'),
        ('Gemini'),
        ('Cancer'),
        ('Leo'),
        ('Virgo'),
        ('Libra'),
        ('Scorpio'),
        ('Sagittarius'),
        ('Capricorn'),
        ('Aquarius'),
        ('Pisces');

INSERT INTO Matches (zodiac_1, zodiac_2)
VALUES  ('Aries', 'Leo'),
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
        ('Pisces', 'Scorpio')