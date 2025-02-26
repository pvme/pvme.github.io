# PVME-Docs

[PVME-Docs](https://pvme.io) is a static site that is generated from the [pvme-guides](https://github.com/pvme/pvme-guides) repository. 

The site is generated using the [Material for Mkdocs theme](https://squidfunk.github.io/mkdocs-material/).

## Changelog

[Changelog](https://github.com/pvme/pvme.github.io/blob/master/docs/home/changelog.md)

## Requirements

**Python**

Install the python version specified in the `Pipfile` `[requires]` section.

**Pipenv**

```commandline
pip install pipenv
```

[Pipenv](https://pypi.org/project/pipenv/)  is used to create virtual environments from a `Pipfile`  and `Pipfile.lock`

## Installation

```commandline
pipenv sync
```

This will setup a virtual environment and install packages from `Pipfile.lock`.

*note: use `pipenv --rm` to reset the old environment in case of any installation issues.*

## Development

**Clone pvme-guides**

```commandline
git clone --depth 1 https://github.com/pvme/pvme-guides.git
```

**Building the site**

```commandline
pipenv run mkdocs build
```

This will build the site locally under the `site/` folder.

**Updating packages**

```commandline
pipenv update
```

Updates packages in `Pipfile.lock` to the latest version according to the versions specified in `Pipfile`.

**Installing new packages**

```commandline
pipenv install package
```

This adds the package to the `Pipfile` and `Pipfile.lock`.

**Debugging**

```commandline
pipenv run python gen_pages.py
```

This will write the generated `.md` files to the `docs/pvme-guides` folder. This is useful for comparing builds.

*Note: You might need to remove the `docs/pvme-guides` folder before building the site.*

**Viewing Changes**

Build the site and open a live server using:

```commandline
pipenv run mkdocs serve
```

Alternatively, after running `pipenv run mkdocs build`, open `/site/index.html` using a live server. 