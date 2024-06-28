---
hide_actions: true
---
# Changelog

Updates for the website.

For bugs or feature requests, message me on Discord (Pleb#0025) or create an issue on [Github](https://github.com/pvme/pvme.github.io).

## June 28, 2024
- Added "edit this guide" button
- Change #user -> @user

## June 15, 2024
- Fixed issue with duplicate titles and improved headings

## May 3, 2024
- Updated mkdocs and other dependencies to latest version

## April 2, 2024
- Fixed markdown links with )) not being formatted correctly

## November 9, 2023
- Updated social card
- New PVME logo

## April 16, 2023
- Urls and other formatting now disabled when text is in `inline code field`

## April 6, 2023

- Added "Editor Info" and "Mastery" categories
- Updated logo
- Fixed some roles that weren't rendered because of a different ID length

## November, 13, 2022

- Reorganized about and home page (improves navigation on mobile).
- Better alias support
  - Alias for forums/words/extra channels
  - Category emojis

## November, 5, 2022

- New site structure:
    - Categories now on the top of the page.
    - Added category aliases
    - Updated "about" page
    - Added "how the site works" page
    - Included changelog to the site itself
- Generated pages are now appended to mkdocs.yaml `nav` instead of fully overwriting it.

## November, 1, 2022

- Moved `"(Courtesy of)"` to the line below headings to clean up the ToC on the side
- New logo
- Removed various mentions of ToC in pins (only relevant to Discord)

## November, 1, 2022

- Fixed some broken headings

## October, 30, 2022

- Implemented new site generation
    - By default, guides are sorted alphabetically
    - All guides will be included, even when the [pvme-guides repository](https://github.com/pvme/pvme-guides) structure changes
- Fixed remaining broken links (will continue to work in the future)

## September, 6, 2022

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
- bugfix with incorrect channel urls: [issue](https://github.com/pvme/pvme.github.io/issues/9)

## September, 1, 2022

- Code blocks in embeds now shown correctly

## August, 31, 2022

- Empty lines are now shown correctly

## August, 30, 2022

- PVME settings are now all obtained from pvme-settings and will be kept up to date mostly automatically and otherwise more frequently (users is still manual)
- Various refactoring for PVME settings migration

## August, 15, 2022

- Prices now updated correctly in embeds

## July, 4, 2022

- added Zamorak category

## June, 20, 2022

Thanks to emmet-shark:

- Added new category structure and guide names. The guide structure and names now always match the category + channel names in Discord 
- Reduced spacing
- embed fixes
    - fix links inside embeds
    - remove nonexistent footer embed icons

## June, 15, 2022

Thanks to emmet-shark:

- Removed unnecessary ToC embed at the bottom of the page
- Fixed a bunch of non-clickable urls

## August, 9, 2021

- Updated invalid Discord channels
- Added invite link url to home page

## August, 6, 2021

- Added invalid discord channels as non-clickable links (WiP)
- Added search suggestions
- Added search highlighting
- Added "back to top" button
- Updated channels and users

## July, 7, 2021

- Updated users and roles

## June, 30, 2021

- Added Solak category and updated channels

## June, 25, 2021

- Fixed bug with imgur.mp4 and imgur.jpg not being rendered

## June, 10, 2021

- Added support for discord embeds [vorago-trio-hm](https://pvme.io/pvme-guides/vorago/vorago-trio-hm/#safe-phases-10-11)

## May 20, 2021

- fixed broken channel links
- updated missing roles/channels/users
- bugfix imgur links
- light/dark mode switch

## April 16, 2021

- Added new categories (same structure as PVME Discord)

## March 22, 2021

- Added support for emojis (standard discord emojis)
- Updated missing roles/channels/users
- Removed note for survey

## March 15, 2021

- Updated missing roles/channels/users
- Added note for survey

## January 9, 2021

- Added colored roles
- Updated missing Discord links
- Added WiP Slayer Category

## January 4, 2021

- Added, and enabled by default, debug logging to quickly check missing Discord links (check daily build log)

## December 18, 2020

- "last updated on" only on "Home" page (since the page is updated daily)

## December 17, 2020

- Added support for ~~strike-through~~ text
- Added changelog

## December 16, 2020

- Initial release
