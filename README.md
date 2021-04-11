# Geyser Autoupdater
This script automatically fetches the newest build from the GeyserMC jenkins site
and pushes it to a Minecraft Paper/Spigot server with FTP.

I wrote this in like 20 minutes, so it's not very good and security is abysmal.
Use at your own risk.

Also feel free to modify my code however you wish, its mildly reusable.

## Config
It's pretty self-explanatory I think, just put in your FTP address, username,
and password, and run the script. Don't mess with the Jenkis URL unless you know what you're doing.

If it breaks just like, make an issue or something and I *might* fix it.

## Notes
* Password stored in plain text. Again, use at your own risk. I highly recommend
setting strict permissions on `host.json`
* Old downloads will stick around, but the script deletes them if it gets over 100MB
