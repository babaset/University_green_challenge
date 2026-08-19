# University Green Challenge

Run the project from this folder:

```powershell
py -3 -m pip install -r requirements.txt
py -3 university_green_challenge.py
```

The desktop interface uses CustomTkinter and the supplied Green Challenge logo
to closely follow the Figma layout while keeping the application's Python data
and validation logic.

## Project structure

| File | Responsibility |
| --- | --- |
| `university_green_challenge.py` | Starts the application only. |
| `green_challenge/constants.py` | Password, eco-actions, icons, and allowed image formats. |
| `green_challenge/models.py` | Simple structures for students, claims, and pending requests. |
| `green_challenge/store.py` | Data and core rules: registration, claims, review, and leaderboard sorting. |
| `green_challenge/persistence.py` | Saves and restores data from the JSON data file. |
| `green_challenge/views.py` | Builds the CustomTkinter screens, navigation, fields, cards, and tables. |
| `green_challenge/styles.py` | Figma-derived colours, typography, and table styling. |
| `green_challenge/dialogs.py` | Reusable success, error, and information dialogs. |
| `green_challenge/app.py` | Connects the interface to the rules and controls login and screen updates. |

## Saved data

Data is saved automatically in `green_challenge_data.json` whenever a student
is registered, a claim is submitted, or an administrator reviews a claim.
The application restores this data automatically the next time it starts.

Each submitted evidence image is recorded with a SHA-256 fingerprint. The same
image cannot be reused for another claim, even if its filename is changed.

To reset the project completely, delete `green_challenge_data.json` while the
application is closed.
