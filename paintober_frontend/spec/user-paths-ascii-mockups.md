# Paintober User Paths

This is a basic walkthrough of the frontend user journeys, shown as simple page and screen mockups.

## 1. Landing Page

Route: `/`

The user learns what Paintober does and chooses to start creating.

```text
+----------------------------------------------------------------+
| PAINTOBER                         Start Creating   History     |
+----------------------------------------------------------------+
|                                                                |
|                 Turn your photo into a                        |
|                 paint-by-numbers kit                           |
|                                                                |
|                 [ Start Creating ]                             |
|                                                                |
|          [ BEFORE image ]       [ AFTER image ]                |
|                                                                |
+----------------------------------------------------------------+
| HOW IT WORKS                                                   |
|   1. Upload          2. Choose colours       3. Paint          |
+----------------------------------------------------------------+
| PERFECT FOR EVENT HOSTS                                        |
|   parties   workshops   team events                            |
+----------------------------------------------------------------+
|                 [ Create Your Kit ]                            |
+----------------------------------------------------------------+
```

Primary path: select `Start Creating` or another creation CTA -> `/studio`.

## 2. Upload Page

Route: `/studio`

The user starts a new kit by uploading an image.

```text
+----------------------------------------------------------------+
| PAINTOBER                         Start Creating   History     |
+----------------------------------------------------------------+
|                         CREATE YOUR KIT                        |
|                                                                |
|  +----------------------------------------------------------+  |
|  |                         [ Upload icon ]                  |  |
|  |                                                          |  |
|  |                  Drop your image here                    |  |
|  |                    or click to browse                    |  |
|  |                                                          |  |
|  |                    [ Choose File ]                       |  |
|  |                                                          |  |
|  |              JPG, PNG, or WEBP - up to 50 MB              |  |
|  +----------------------------------------------------------+  |
|                                                                |
|                  [ Continue ]                                 |
+----------------------------------------------------------------+
```

The user can use the file picker or drag and drop. The frontend validates the file type and size before continuing.

## 3. Configure: Automatic Palette

The automatic palette is the default option after an image is selected.

```text
+----------------------------------------------------------------+
| CREATE YOUR KIT                                                |
|                                                                |
|  Selected file: holiday-photo.jpg                             |
|                                                                |
|  PALETTE                                                       |
|  (o) Automatic palette                                         |
|  ( ) Preset paint set                                          |
|  ( ) Bring your own palette                                    |
|                                                                |
|  [ Advanced settings v ]                                       |
|                                                                |
|                  [ Generate Kit ]                              |
+----------------------------------------------------------------+
```

Path: upload image -> optionally adjust advanced settings -> `Generate Kit`.

## 4. Configure: Preset Paint Set

The user chooses from predefined colour sets.

```text
+----------------------------------------------------------------+
| CREATE YOUR KIT                                                |
|                                                                |
|  Selected file: holiday-photo.jpg                             |
|                                                                |
|  PALETTE                                                       |
|  ( ) Automatic palette                                         |
|  (o) Preset paint set                                          |
|  ( ) Bring your own palette                                    |
|                                                                |
|  CHOOSE A PAINT SET                                            |
|  +----------------+  +----------------+  +----------------+   |
|  | Classic        |  | Bright         |  | Earthy         |   |
|  | [colours]      |  | [colours]      |  | [colours]      |   |
|  | [ Select ]      |  | [ Select ]      |  | [ Select ]      |   |
|  +----------------+  +----------------+  +----------------+   |
|                                                                |
|                  [ Generate Kit ]                              |
+----------------------------------------------------------------+
```

Path: upload image -> choose `Preset paint set` -> select a set -> `Generate Kit`.

## 5. Configure: Bring Your Own Palette

The user supplies the colours that should be used in the generated kit.

```text
+----------------------------------------------------------------+
| CREATE YOUR KIT                                                |
|                                                                |
|  Selected file: holiday-photo.jpg                             |
|                                                                |
|  PALETTE                                                       |
|  ( ) Automatic palette                                         |
|  ( ) Preset paint set                                          |
|  (o) Bring your own palette                                    |
|                                                                |
|  YOUR COLOURS                                                  |
|  [ + Add colour ]                                              |
|  [red] [blue] [yellow] [green]                                |
|                                                                |
|  [ ] Allow colours to be reused                                |
|                                                                |
|                  [ Generate Kit ]                              |
+----------------------------------------------------------------+
```

Path: upload image -> choose `Bring your own palette` -> add or remove hex colours -> `Generate Kit`.

## 6. Processing Page

After submission, the job receives an ID and the URL becomes `/studio/:jobId`.

```text
+----------------------------------------------------------------+
| PAINTOBER                         Start Creating   History     |
+----------------------------------------------------------------+
|                                                                |
|                    GENERATING YOUR KIT                         |
|                                                                |
|                           (  O  )                              |
|                                                                |
|                    Processing...                              |
|                                                                |
|                    Job: abc123                                 |
|                                                                |
|              Please keep this page open                        |
+----------------------------------------------------------------+
```

The frontend polls the job status until the job is complete or fails.

## 7. Results Page

When processing succeeds, the user can inspect and download the generated files.

```text
+----------------------------------------------------------------+
| PAINTOBER                         Start Creating   History     |
+----------------------------------------------------------------+
|                         YOUR KIT IS READY                      |
|                                                                |
|  +------------------+  +------------------+  +----------------+
|  | OUTLINE          |  | COLOUR FILL      |  | PALETTE        |
|  |                  |  |                  |  |                |
|  |    [ preview ]   |  |    [ preview ]   |  |  [ swatches ]  |
|  |                  |  |                  |  |                |
|  | [Download PNG]   |  | [Download PNG]   |  | [Download PNG] |
|  +------------------+  +------------------+  +----------------+
|                                                                |
|                    [ Download ZIP ]                            |
|                                                                |
|                    [ Create Another Kit ]                      |
+----------------------------------------------------------------+
```

Paths from here:

- Select an individual `Download PNG` action.
- Select `Download ZIP` for the complete kit.
- Select `Create Another Kit` -> `/studio` for a new upload.
- Open `History` to view previous completed jobs.

## 8. Failed Generation

If the backend reports a failed job, the Studio shows an error state.

```text
+----------------------------------------------------------------+
| PAINTOBER                         Start Creating   History     |
+----------------------------------------------------------------+
|                                                                |
|                    SOMETHING WENT WRONG                        |
|                                                                |
|              We could not generate your kit.                   |
|              [ readable error message ]                        |
|                                                                |
|                       [ Try Again ]                            |
+----------------------------------------------------------------+
```

Path: select `Try Again` -> reset the current job and return to the upload/configuration flow.

## 9. History Panel

The `History` control is available from the shared header. It opens a panel from the right side of the current page.

```text
+---------------------------------------+------------------------+
| PAINTOBER                             | HISTORY             X  |
|                                       |                        |
|                                       | [done] 08/19  Kit 1  |
|                                       |        Open result    |
|                                       |                        |
|                                       | [done] 08/18  Kit 2  |
|                                       |        Open result    |
|                                       |                        |
|                                       | [processing] Kit 3   |
|                                       |        In progress    |
+---------------------------------------+------------------------+
```

- Completed jobs are selectable and reopen at `/studio/:jobId`.
- Processing, queued, and failed jobs are currently display-only.
- The panel can be closed with `X` or by using its close behavior.

## Overall Path Map

```text
[ Landing / ]
       |
       v
[ Upload /studio ]
       |
       +--> [ Automatic palette ] --+
       |                             |
       +--> [ Preset paint set ] ----+--> [ Generate Kit ]
       |                             |
       +--> [ Bring your own ] ------+
                                     |
                                     v
                         [ Processing /studio/:jobId ]
                              |                 |
                              | success         | failure
                              v                 v
                         [ Results ]       [ Try Again ]
                              |
                              v
                       [ New kit /studio ]

[ History ] --> [ Completed job ] --> [ Results /studio/:jobId ]
```

## Current Boundaries

- There is no dedicated account or sign-in path.
- There is no explicit 404 page for unknown routes.
- History is session-based, so a job URL may not work in another browser session.
- Preset and custom-palette selection should be validated before generation; the current UI may allow submission without a selected preset or custom colour.
