---
hide_actions: true
---
# How The Site Works

Full process on [Github](https://github.com/pvme/pvme.github.io), and in short:

1. Gather the `.txt` guides from the [pvme-guides repository](https://github.com/pvme/pvme-guides).
2. Format `.txt` -> `.md`.
3. Build the website from the `.md` files using [MKDocs Material](https://squidfunk.github.io/mkdocs-material).

## Limitations

First and foremost, the guides on the website are always up-to-date with the PvME Discord Server.

This is because both are using the `.txt` guides from the [pvme-guides repository](https://github.com/pvme/pvme-guides).

With that being said, the `.txt` formatting is primarily aimed at Discord which can lead to some content showing incorrectly:

- References to social Discord exclusive channels (<a href="" class="inactiveLink">#pvm-help</a>)
- Mentions of `$linkmsg`

I try to stay ahead of this by adding formatting rules that exclude or change Discord-only content.

If you find any formatting issues, please message me on Discord (Pleb#0025) or create an issue on [Github](https://github.com/pvme/pvme.github.io).