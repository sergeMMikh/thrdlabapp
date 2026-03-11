## Django Template

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/GB6Eki?referralCode=U5zXSw)

### Recent updates

* Added client‑side availability checks for both equipment and furnace bookings. When a date/equipment combination is already taken, a red warning appears beneath the form before submission explaining why the request will fail.  Backend still enforces uniqueness so double submissions remain impossible.

### Testing notes

* The project defaults to using **PostgreSQL** in normal operation.  During automated tests (either via `manage.py test` or `pytest`) the settings module will switch to an in‑memory SQLite database.  This avoids failures on CI runners or developer machines where the configured Postgres hostname may not be reachable.  The same behaviour is triggered when the environment variable `CI` is set (GitHub Actions and other systems provide this automatically).
* If you really need to run tests against Postgres, you can override the behaviour by unsetting `CI` and invoking Django with a custom settings module that does not perform the switch.



