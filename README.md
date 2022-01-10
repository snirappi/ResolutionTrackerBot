# ResolutionTrackerBot
Discord Bot for Tracking New Years Resolutions

# Features
* Set, View, and Give updates on a New Year's Resolution
* Users can either choose weekly participation or daily participation
* Shows everyone participating that has kept up to date with their resolution, for daily and weekly goals

## Details
Creates a json file to store resolutions in case the bot is stopped for whatever reason.
Uses a .env file looking for 
* DISCORD_TOKEN 
* JSON_FILE (name of file to use for storage)
* CHANNEL (channel id to post to)
* SUCCESS_EMOJI (user choice emoji)
* FAIL_EMOJI (user choice emoji)
* WEEKLY_CHECK_DAY (weekday day, number from 0-6 | Monday-Sunday )