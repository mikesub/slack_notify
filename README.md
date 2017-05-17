# slack notification on open PRs and possibly stuck issues in JIRA

* rename `_config.py` to `config.py` and fill it with your settings 
* `./main.py SLACK` will use slack, all other configurations will use stdout.
* anything not `SLACK` as an arg will trigger debug mode.
