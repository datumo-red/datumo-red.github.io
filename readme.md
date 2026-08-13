# Selectstar Safety Research Team Website

The static website for the Selectstar Safety Research Team, hosted as GitHub Pages.

The site contents live in a private Google Sheets document rather than in this repository. A scheduled GitHub Actions job reads that document every 30 minutes, rebuilds the site into the *[docs](docs)* folder, and commits the result.

## How does this website work?

The build is defined in *[.github/workflows/builder.yml](.github/workflows/builder.yml)*. It runs every 30 minutes and on every push to *master*.

**Do NOT edit anything inside the *[docs](docs)* folder.** That folder is deleted and regenerated on every build, so changes made there are lost on the next run. Edit the Google Sheets document instead — or the templates in *[builder/templates](builder/templates)* for layout changes.

## Configuration

Both values are read from repository secrets (Settings → Secrets and variables → Actions) and are passed to the builder as action inputs. Neither is stored in this repository.

| Secret | Description |
| --- | --- |
| `API_KEY` | Google API key with the Google Sheets API enabled. |
| `DATA_URL` | URL of the Google Sheets document holding the site contents. |

The Sheets API is accessed with an API key, which only works on documents shared as *Anyone with the link – Viewer*. Keeping `DATA_URL` in a secret keeps the document from being advertised on the site; it is not an access control. Do not put anything in the document that must stay private.

### Building locally

```sh
pip install -r requirements.txt
API_KEY=<your-key> DATA_URL=<your-sheet-url> python3 build.py
```

The build fails immediately with a readable message if either value is missing.

## Data source layout

The builder expects these tabs, and reads the ranges listed in *[builder/loader.py](builder/loader.py)*:

`Website` `Announcements` `Members` `Research` `Tags` `Links` `Pages` `Redirects` `Personal`

A tab that is missing entirely makes the whole request fail with a 400; an empty tab is fine.

The `Members` tab groups people by column A, so rows sharing a value in column A are rendered as one section:

| A | B | C | D | E | F | G | H |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Section title | Name | Email | Image | Description | Links | Degree | Year |

Rows with a value in `Year` are rendered as alumni.

## Static files

Put images and other static files in the *[assets](assets)* folder. Everything in it is copied to *docs/assets* on each build, so reference them from the sheet as site-root paths such as `/assets/images/members/name.png`.

## Acknowledgements

Built on [research-group-static-web](https://github.com/jmbyun/research-group-static-web) by Jeongmin Byun, used under the MIT License. The original work was supported and funded by [JinYeong Bak](https://github.com/nosyu).
