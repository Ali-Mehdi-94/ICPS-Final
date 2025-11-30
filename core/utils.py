# core/utils.py
from django.db import transaction
from django.db.models import Q
from .models import CustomUser

ROUND_ROBIN_CACHE_KEY = "_last_ops_user_id"  # simple in-DB tracker alternative

def _get_ops_qs():
    # Only active Ops (and optionally CEO if you want them eligible; currently not)
    return CustomUser.objects.filter(is_active=True, role="Ops").order_by("id")

def _get_tracker():
    # Use a single-row settings-ish storage on the CustomUser table via a harmless trick:
    # We'll store the last id in the user with username '__ops_rr_tracker__' (no real user).
    # If you prefer a real model, we can add it later; this works without migrations.
    return CustomUser.objects.filter(username="__ops_rr_tracker__").first()

@transaction.atomic
def next_ops_user():
    ops_users = list(_get_ops_qs().values_list("id", flat=True))
    if not ops_users:
        return None  # no Ops users configured yet

    tracker = _get_tracker()
    last_id = None
    if tracker:
        # store last id in first_name field to avoid migrations (cheap but effective for now)
        try:
            last_id = int(tracker.first_name) if tracker.first_name else None
        except ValueError:
            last_id = None

    # find next index
    if last_id in ops_users:
        idx = ops_users.index(last_id)
        next_idx = (idx + 1) % len(ops_users)
    else:
        next_idx = 0

    next_id = ops_users[next_idx]

    # upsert tracker
    if not tracker:
        tracker = CustomUser.objects.create(
            username="__ops_rr_tracker__",
            is_active=False,
            is_staff=False,
            is_superuser=False,
            first_name=str(next_id),
        )
    else:
        tracker.first_name = str(next_id)
        tracker.save(update_fields=["first_name"])

    # return the user instance
    return CustomUser.objects.filter(id=next_id).first()
