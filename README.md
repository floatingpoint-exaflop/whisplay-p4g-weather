# Whisplay Persona 4 Weather UI

The PiSugar Whisplay HAT is incredibly versatile, but I only see people doing like two or three things with it, despite it having an excellent UI, a surprisingly loud onboard speaker, and equally surprising dual MEMS mic input. 

This isn't a review; I've just noticed this thing is so new that the doco for it can be hard to find still! Half the reviews say it's hard to set up. I don't disagree, so I spent some time reverse engineering the official stuff from [the official whisplay repo](https://github.com/PiSugar/whisplay) and some of [hemna's much more impressive whisplay weather app](https://github.com/hemna/pisugar-wx).

Anyway, I played Persona 4 Golden this past year and really enjoyed it. The game has a remake, Persona 4 Revival, dropping later this year (2026) and in honor of the hype I put together a Whisplay app that gives you a mini-HUD in the style of Persona 4 Golden's weather and time of day corner splash. Some assets are from Golden, some are not; I probably will try to fix this.

The project was also a good chance to learn tiling and aseprite; I have included my project files in case you have it too, but you don't need it to run the app as it exists in version 1. I developed this using a Pi500+, and this hat mounted to the GPIO on the Adafruit cyberdeck bonnet honestly looks incredible.

## Features
- Cute Yasogami High Hallway/Weather News loading screen with startup and UI sounds from the game, configured to play from the Whisplay's onboard speaker.
- Live OpenWeather API integration
  - Displays some information from the current local weather (courtesy of OpenWeather API.
  - You'll need to register for a free key at [their site](https:www.openweather.org) ).
  - Note that because the game doesn't display the temperature, I don't either - it's not meant to be practical lol!
- Time-of-day transitions
  - App keeps the time, and displays it in general time-of-day descriptions (morning, lunchtime, after school, etc.), a classic element of Persona games.
  - Exact time currently isn't displayed (to keep the feel game-accurate), but no reason it couldn't be.
- Dynamic weather backgrounds of the Dojima Residence, including sunny, cloudy, rainy, snowy, snowing currently, clear night, and foggy.
  - This is on a big-ass tile picture and I've thought about, ahem, generating some more variants for immersion (there is, I think, one 'night' image of the Dojima Residence that I did try GPT for), but for now the selection we have works pretty well.
- Dynamic weather icons - same deal as above, meant to look like the game.
  - I want to adjust these a bit for look and feel accuracy, because good ones were hard to come by, but they're very convincing for a v1.
- Ambient rain/thunder audio
  - YES YOU READ THIS RIGHT, when it rains outside it plays the rain audio from inside Yu's bedroom in the Dojima residence!
    - This feature currently plays for ten minutes; I think I forgot to loop it so I maybe gotta fix that!!
  - Also, if it's stormy out it plays game UI thunder sounds randomly!
- Persona-inspired UI overlays (See the disclaimer; it's really more than just 'inspired')

## Planned Features
- Improved UI options and expanded use of P4G menu UI sound assets
- Consistency in P4G text/digit asset use, or maybe an option to cleanly toggle (they're png tiles, not placed ttf text).
- Persona 3 Royal-style moon phase added in corner, optional.
  - Most of the code for this is in there already but it's broken and moon phase never shows at all.
- Enhance responsiveness of weather transitions
- More game-accurate weather icons and time-accurate background changes
- Game-accurate 5-day forecast screen
- I will publish my service that launches this app on pi startup every time, and my switcher that (will, when it works) allow toggle between several whisplay apps cleanly, including the Whisplay AI Chatbot app.
- I think I might've embedded the API key as an environment variable in my system; in theory a .env would work too. I'll check up on that so folks don't run into issues.

## Disclaimer

- Pretty much everything displayed on this app is either directly lifted or manually recreated from Persona 4/Golden.
  - Persona and all related visual/audio assets are property of ATLUS / SEGA.
  - I, as a huge fan, just put in the work cutting them up and stitching them together.
- Fontsona 4 Golden, currently used on the error modal when Weather API fails, was created/distributed by Reddit user why_do_i__even_exist.

This repository is a non-commercial fan project created for educational and personal enjoyment purposes. No ownership of original Persona assets is claimed - that would be insane!

## (My) Hardware
- Raspberry Pi 500+
- 2x Pi Monitor
- Adafruit Cyberdeck Bonnet
- Whisplay AI IO Display/Audio HAT (WM8960 audio chipset)


