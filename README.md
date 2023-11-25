A fork of the [Ed1123/visa_web_scraper](https://github.com/Ed1123/visa_web_scraper).

# Main improvements/changes

- Checks for appointment availability more complex than in the origianl code;
- Add handling for multiple exceptions, like network is not available etc.
- Provisions to look for appointments in several countries; you have to have several applications, one for each country;
- Expanded rescheduling section, that allows to search for an appointment earlier than you specified;
- Plays sound on the local machine when a new appointment found, simpleaudio library added to requirements;
- Each run is timestamped, heartbeat before next run is shown in the command line;
- Flow clean up.
