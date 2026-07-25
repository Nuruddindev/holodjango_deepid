# holodjango_deepid

The Django-side identity authority adapter for [`hc_deepid`](https://github.com/Nuruddindev/hc_deepid) — a reusable Holochain zome for multi-device identity anchored to an external identity authority.

> **Status:** early scaffold / work in progress. Core models, service layer, and a minimal API are in place; not yet published to PyPI. Extracted and generalized from the identity flow proven in [NFB Den](https://nfb.digital).

## What this is

`hc_deepid` anchors multi-device Holochain identity to `ExternalHash(external_id)` — but something has to actually issue that `external_id` and vouch for who owns it. That's this package's job: a pip-installable, reusable Django app that a Django project drops into `INSTALLED_APPS` to become a `hc_deepid`-compatible identity authority.

It does **not** know about `AgentPubKey`s, devices, or DHT state — that's entirely `hc_deepid`'s responsibility on the Holochain side. `holodjango_deepid` only owns two things:

1. **Issuing ephemeral, single-use first-sync tokens** — short-lived tokens that authorize a Holochain agent to pull a user's identity into the DHT for the first time. Following the pattern proven in NFB Den, these tokens are used once and then discarded; they are never a long-term credential.
2. **Exposing a stable `external_id`** per Django user — the identifier `hc_deepid` anchors its `ExternalHash` on.

## Installation

```bash
pip install holodjango-deepid  # not yet published — install from source for now
```

Add to your Django project:

```python
INSTALLED_APPS = [
    ...
    "holodjango_deepid",
]
```

```python
# project urls.py
urlpatterns = [
    ...
    path("deepid/", include("holodjango_deepid.urls")),
]
```

Then run migrations:

```bash
python manage.py migrate
```

## Usage

### Issuing a first-sync token

```python
from holodjango_deepid import services

token = services.issue_first_sync_token(request.user)
# hand token.token to the client, which passes it to the Holochain-side
# first-sync flow
```

Or via the built-in endpoint: `POST /deepid/first-sync/issue/` (requires an authenticated Django session).

### Consuming a token (called from your Holochain-facing sync endpoint)

```python
from holodjango_deepid import services

try:
    result = services.consume_first_sync_token(token_value)
    # result.user_id, result.external_id
except services.InvalidTokenError:
    # token missing, expired, or already used
    ...
```

Or via: `POST /deepid/first-sync/consume/` with `{"token": "..."}`.

### Looking up a user's external ID

```python
from holodjango_deepid import services

external_id = services.get_external_id(user)  # None if never synced
```

## Configuration

Optional Django setting:

```python
HOLODJANGO_DEEPID_TOKEN_TTL_SECONDS = 300  # default: 5 minutes
```

## Models

- **`FirstSyncToken`** — an ephemeral, single-use token tied to a user, with an expiry and a consumed timestamp. Not meant to be queried directly by consuming code; use the `services` module.
- **`DeepIdentity`** — the stable `external_id` anchor for a user, plus first/last sync timestamps. One-to-one with your `AUTH_USER_MODEL`.

Run `python manage.py prune_first_sync_tokens` periodically (e.g. via cron or Celery beat) to clear out expired/consumed token rows — they carry no long-term value by design.

## Framework choice

Views in this package use plain Django (`JsonResponse`), not Django REST Framework, so installing this app doesn't force a REST framework choice on your project. If you use DRF, ninja, or something else, write thin serializer views calling the same `holodjango_deepid.services` functions instead of using the built-in views.

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Related

- [`hc_deepid`](https://github.com/Nuruddindev/hc_deepid) — the Holochain-side zome this package pairs with.
- Planned: equivalent adapters for other stacks (npm/JavaScript, PHP).

## License

MIT — see [LICENSE](./LICENSE).
# holodjango_deepid
