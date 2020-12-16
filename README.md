# PVME-Docs

PVME-Docs ([pvme.github.io](pvme.github.io)) is a static site that is generated from the [pvme-guides](https://github.com/pvme/pvme-guides) repository. 

The site is generated using the [Material for Mkdocs theme](https://squidfunk.github.io/mkdocs-material/).

## TODO

:red_circle:TODO or won't be implemented

:construction: ongoing

:white_check_mark:done

| **Task**                             | **Status**         |
| ------------------------------------ | ------------------ |
| Embed: open graph for unknown links  | :red_circle:       |
| Embed: open graph for all links (*)  | :red_circle:       |
| Embed: wiki links                    | :construction:     |
| Embed: google docs                   | :construction:     |
| Discord user mentions (*)            | :white_check_mark: |
| Discord channels (*)                 | :white_check_mark: |
| Discord roles (*)                    | :white_check_mark: |
| Embed: include character before link | :white_check_mark: |

*Through work-around where the conversion is stored in a `.txt` file which is manually has to be updated whenever new types of channel links are added.

## Requirements

**Python**

Install the python version that is required in `Pipfile`

**Pipenv**

```
pip install pipenv
```

[Pipenv](https://pypi.org/project/pipenv/)  is used to create virtual environments from a `Pipfile`  and `Pipfile.lock`

## Installation

**Setup**

```
pipenv install
```

This will the packages and their dependencies (fixed version number) using `Pipfile.lock`.

**Environment variables**

The following environment variables <u>can</u> be set in order to test API functionality locally:

```
GS_URL
GS_PRIVATE_KEY
GS_CLIENT_EMAIL
GS_TOKEN_URI
```

*It's not mandatory to set the environment variables.

## Development

It's suggested to follow the steps described in: `.github/workflows/ci.yml` for an overview on how to clone the [pvme-guides](https://github.com/pvme/pvme-guides) repository and run tests etc. 

**Installing new packages**

```
pipenv install package
```

This will update the `Pipfile` and `Pipfile.lock` with the new package requirement.

**Previewing changes**

Changes can be previewed in 2 ways:

*Build site*

```
pipenv run mkdocs build
```

*Automatically updated site*

```
pipenv run mkdocs serve
```

*Automatically updating the site is a bugged as is sometimes doesn't update when rebuilding the sources.

## Troubleshooting

**Installation issues**

The simplest way to resolve installation issues is to remove and reinstall the virtual environment:

```
pipenv --rm
pipenv install
```

**Missing dependencies**

The following command shows a dependency graph of all packages:

```
pipenv graph
```