<img src="assets/logo.png" alt="App Logo" width="128">

# Installation Guide

How to install the app and manage your installation day-to-day. For deployment beyond localhost (network access, custom compose stacks, production configuration), see [Deployment Options](Deployment.md).

## Prerequisites

- **Docker** - installed and running ([Get Docker](https://docs.docker.com/get-docker/))
- **Python 3.11+** - for secure credential generation (usually pre-installed)

## Quick Installation

**One command gets you running in 30 seconds:**

```shell
curl -fsSL https://raw.githubusercontent.com/cassandra/zzz-app/master/install.sh | bash
```

**What it does:**
- Verifies Docker is running
- Creates data directories in `~/.zzz/`
- Generates secure admin credentials
- Downloads and starts the application
- Shows your login URL and credentials

**Result:** Visit [http://localhost:8666](http://localhost:8666) and sign in with the displayed credentials.

**Data location:**
- Database: `~/.zzz/database/`
- Files: `~/.zzz/media/`

## Managing your installation

Manage the running app with standard Docker commands:

```shell
docker logs zzz          # view logs (add -f to follow)
docker stop zzz          # stop the app
docker start zzz         # start it again
docker restart zzz       # restart (e.g. after changing the env file)
docker ps | grep zzz     # status / health
```

**Your files:**

- Configuration: `~/.zzz/env/local.env`
- Database: `~/.zzz/database/`
- Uploaded media: `~/.zzz/media/`

## Updates

Run the update script — it pulls the latest image and recreates the container, preserving your data:

```shell
curl -fsSL https://raw.githubusercontent.com/cassandra/zzz-app/master/update.sh | bash
```

## Environment Variable Changes

Edit your configuration file at `~/.zzz/env/local.env`, then restart the app to pick up the changes:

```shell
docker restart zzz
```

If you changed network settings such as `ZZZ_EXTRA_HOST_URLS`, see the [Deployment Options](Deployment.md) guide for related configuration.

## Removing your installation

```shell
docker stop zzz
docker rm zzz
```

To also remove your data and configuration (this is permanent):

```shell
rm -rf ~/.zzz/
```

## Troubleshooting

### Common Issues

**Can't access from other devices on your network?**

By default, the app only accepts requests to `localhost`. To access it from other devices (including by IP address), you need to tell the app which URLs are allowed:

- Set `ZZZ_EXTRA_HOST_URLS` to the URL(s) you'll use to access the app, including the scheme and port
- Example: `ZZZ_EXTRA_HOST_URLS="http://192.168.1.100:8666"` (use your server's actual IP)
- Multiple URLs can be space-separated: `ZZZ_EXTRA_HOST_URLS="http://192.168.1.100:8666 http://myserver.local:8666"`
- For standalone Docker: edit `$HOME/.zzz/env/local.env` and run `docker restart zzz`

If you see `Invalid HTTP_HOST header` errors in the logs, this is the setting you need. However, note that this setting requires the full URL location, not just a hostname.

**Email alerts not working?**
Configure email settings in `$HOME/.zzz/env/local.env`:
```shell
ZZZ_EMAIL_HOST=smtp.gmail.com
ZZZ_EMAIL_PORT=587
ZZZ_EMAIL_HOST_USER=your-email@gmail.com
ZZZ_EMAIL_HOST_PASSWORD=your-app-password
ZZZ_EMAIL_USE_TLS=true
```

**User login issues?**
- Ensure email is configured (login requires "magic codes" sent via email)
- Disable authentication temporarily: `ZZZ_SUPPRESS_AUTHENTICATION="true"`

### More Help

- **Deployment beyond localhost** (network access, auto-start, custom compose stack, user management): [Deployment Options](Deployment.md)
- **Detailed troubleshooting:** [FAQ](FAQ.md)
