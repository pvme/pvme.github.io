# Changelog

## Release notes

### November, 1, 2022

- Moved "(Courtesy of)" to the line below the heading to clean up ToC on the side

### November, 1, 2022

- Fixed some broken headings

### October, 30, 2022

- Implemented new site generation
  - by default, guides are sorted alphabetically
  - all guides will be included, even when the discord (pvme-guides repo) structure changes
- Fixed remaining broken links (will continue to work in the future)

### September, 6, 2022

- Finished formatter rewrite
- Embed changes
  - increased max width (if content fits on discord, it will fit on the site)
  - fixed inline code formatting (correct font so width matches discord)
  - darkened background slightly
  - changed description font color to match that of the rest of the embed
  - light mode looks the same as dark mode
- Attachment url changes (videos/images)
  - removed autoplay option to improve page load time
  - all videos have the same control options
  - added more known url regexes to reduce build time
- bugfix with incorrect channel urls: https://github.com/pvme/pvme.github.io/issues/9

### September, 1, 2022

- Code blocks in embeds now shown correctly

### August, 31, 2022

- Empty lines are now shown correctly

### August, 30, 2022

- PVME settings are now all obtained from pvme-settings and will be kept up to date mostly automatically and otherwise more frequently (users is still manual)
- Various refactoring for PVME settings migration

### August, 15, 2022

- Prices now updated correctly in embeds

### July, 4, 2022

- added Zamorak category

### June, 20, 2022

Thanks to emmet-shark:

- Added new category structure and guide names. The guide structure and names now always match the category + channel names in Discord 
- Reduced spacing
- embed fixes
  - fix links inside embeds
  - remove nonexistent footer embed icons

### June, 15, 2022

Thanks to emmet-shark:

- Removed unnecessary ToC embed at the bottom of the page
- Fixed a bunch of non-clickable urls

### August, 9, 2021

- Updated invalid Discord channels
- Added invite link url to home page

### August, 6, 2021

- Added invalid discord channels as non-clickable links (WiP)
- Added search suggestions
- Added search highlighting
- Added "back to top" button
- Updated channels and users

### July, 7, 2021

- Updated users and roles

### June, 30, 2021

- Added Solak category and updated channels

### June, 25, 2021

- Fixed bug with imgur.mp4 and imgur.jpg not being rendered

### June, 10, 2021

- Added support for discord embeds [vorago-trio-hm](https://pvme.github.io/pvme-guides/vorago/vorago-trio-hm/#safe-phases-10-11)

### May 20, 2021

- fixed broken channel links
- updated missing roles/channels/users
- bugfix imgur links
- light/dark mode switch

### April 16, 2021

- Added new categories (same structure as PVME Discord)

### March 22, 2021

- Added support for emojis (standard discord emojis)
- Updated missing roles/channels/users
- Removed note for survey

### March 15, 2021

- Updated missing roles/channels/users
- Added note for survey

### January 9, 2021

- Added colored roles
- Updated missing Discord links
- Added WiP Slayer Category

### January 4, 2021

- Added, and enabled by default, debug logging to quickly check missing Discord links (check daily build log)

### December 18, 2020

- "last updated on" only on "Home" page (since the page is updated daily)

### December 17, 2020

- Added support for ~~strike-through~~ text
- Added changelog

### December 16, 2020

- Initial release
