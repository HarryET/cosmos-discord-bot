---
description: >-
  A plugin to serve and manage customized static or animated GIF Welcome
  Banners.
---

# Banner

Welcome Banner is PNG or GIF image file which is generated and sent when any member joins the server.
It can be customized by adding a custom text message which is written over it. Moreover the border color can

### banner

Displays previously configured welcome banner.

```yaml
Usage:
;welcome banner
```

#### set

Configure and set server welcome banner.
You should specify direct URL of the banner template which can be either JPEG or PNG. Prime servers can use

```yaml
Usage:
;welcome banner set <banner_url> [channel] <text>
```

#### enable

Enable sending welcome banners in channel.

```yaml
Usage:
;welcome banner enable 
```

#### disable

Disable sending welcome banner in channel.

```yaml
Usage:
;welcome banner disable
```
