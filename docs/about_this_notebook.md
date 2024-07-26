# About this notebook

\[**Deprecated**\] Everytime when you write a new note...
The following two lines are integrated into Github workflows and sync.sh...
```
mkdocs build
mkdocs gh-deploy
git add --all
git commit -m "blablabla"
git push   # add "-u origin main" for the first push
```

\[**Up to date**\] Just run:
```
./sync.sh
```

To preview the notebook locally...
```
mkdocs build
mkdocs serve
```

## About mkdocs...

For full documentation visit [mkdocs.org](https://www.mkdocs.org).

### Commands

* `mkdocs new [dir-name]` - Create a new project.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs -h` - Print help message and exit.

### Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.
