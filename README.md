# Cordex
Cordex is a Discord bot tailored and designed specifically for the server "The Goobers" with advanced moderation, utilities, and more. Usage outside this server is not recommended. (See below.)
## Forking Notice
Forking this project for purposes other than direct contribution is highly discouraged. To make this bot usable for your own server, you will need to make major reforms across numerous undocumented files.
### Why?
There are minimal configuration options and many things are hardcoded, like roles, users, and channels. There are also minimal to no safety checks implemented into the bot as the bot expects the administrator permission.
### I'm going to anyway.
Sigh. Should you intend do use the bot regardless of this warning, please give the bot the administrator permission for the reason stated above. Change instances of "The Goobers", "Cordex", "Directors", etc, change the EMOJIs and stuff in constants. Make sure you put `TOKEN=...` in a `.env` file.
## Built with...
* python 3.14
* discord.py 2.7.1
* basedpyright - All rules enabled*
  * *The `reportUnusedCallResult` rule has been turned off, as it is boilerplate for the discord.py library.
* ruff - All rules enabled*
  * The following rules have been disabled as they either do not conform to the code style in the repository or are deprecated: D, BLE, PD011, CPY001, PLR6301, E203, E221, E222, E241, E251, E252 E271, E272, E302, E501
## Contributing
Contributions are welcome, but in a solid grey area. Please read CONTRIBUTION.md.