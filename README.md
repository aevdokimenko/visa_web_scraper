# U.S. visa appointment scrapper

A fork of the [Ed1123/visa_web_scraper](https://github.com/Ed1123/visa_web_scraper).

This scraper is made for checking the https://ais.usvisa-info.com site at regular intervals. It logs you in and scrapes the payment site. When an appointment becomes available (a change from the original site where there are no appointments), it will notify you through a Telegram bot.


## Main improvements/changes

- Checks for appointment availability more complex than in the original code;
- Add handling for multiple exceptions, like the network is not available, etc.
- Provisions to look for appointments in several countries; you have to have several applications, one for each country;
- Expanded rescheduling section, that allows you to search for an appointment earlier than you specified;
- Plays sound on the local machine when a new appointment is found, simpleaudio library added to requirements;
- Each run is timestamped, heartbeat before the next run is shown in the command line;
- Flow clean up.
