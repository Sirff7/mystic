# API Endpoints:

## POST /users — Handle Signup
Request body:
  - email (string, max 100 characters): Should be unique
  - password (string, max 255 characters)
Responses:
  201: signup ok, returns user_id (integer)
  400: email format not valid (regex validation)
  409: email not unique
  422: missing or invalid request body fields

## POST /users/login — Handle Login
Request body:
  - email (string, max 100 characters)
  - password (string, max 255 characters)
Responses:
  200: login ok, returns user_id (integer)
  401: unauthenticated
  422: missing or invalid request body fields

## PUT /profiles/{id} - Update Profile
Request body:
  - display_name (string, max 20 characters): Should be unique
  - bio (string, max 1000 characters)
  - zodiac (string, max 20 characters): only valid zodiac names in Latin (see list below)
Responses:
  200: profile updated
  422: missing or invalid request body fields
  400: invalid zodiac name
  409: display_name not unique
  404: profile not found

Zodiac names: 'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius','Capricorn', 'Aquarius', 'Pisces'

### GET /profiles/{id} - Show Profile
Path parameter:
  - profile_id (integer)
Responses:
   200: returns profile_id (integer), display_name (string), bio (string), zodiac (string)
  404: profile not found

### DELETE /users/{id} - Delete Account
Path parameter:
  - user_id (integer)
Responses:
  200: user and profile deleted
  404: user not found

## GET /discoveries/{id} - Discover
Path parameter:
  - profile_id (integer)
Responses:
  200: returns next compatible profile (profile_id (integer), display_name (string), bio (string), zodiac (string))
  200: no more compatible profiles available
  404: profile not found

## POST /likes - Handle Likes
Request body: 
  - liker (integer): profile_id of the profile doing the liking
  - liked (integer): profile_id of the profile being liked
  - likes_status (integer): 1 = like, 0 = dislike
Responses:
  201: like registered
  404: profile_id not found
  409: like or dislike already registered
  422: missing or invalid request body fields

### GET /couples/{id} - Present Couples
Path parameter:
  - profile_id (integer)
Responses:
  200: no mutual likes yet
  200: returns profile_1 (integer), profile_2 (integer)
  404: profile not found
