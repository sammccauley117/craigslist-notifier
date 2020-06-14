# Craigslist Notifier
I've been trying to find roommates in the Bay Area because rent prices there are wild. I got tired of checking the new posts every day, so I wrote this bot to automatically check for new posts every 15 minutes and text them to you. Just give the bot the specific URL of what you're looking for (ex: max & min price, radius around a ZIP code, private room, private bath, etc.). The URL could also direct to craigslist posts for cars, computer parts, or just about anything else.

Currently, I have this running on a Google Cloud Platform VM. Cronjobs seem to be a little weird on GCP VMs, so instead I have it serving up a Flask server and use the GCP "Cloud Scheduler" service to run trigger the `check_posts` method every 15 minutes: `*/15 * * * *`.

To run the server indefinitely and to restart on crashes, run the following command:
```bash
$ nohup ./monitor.sh &
```
