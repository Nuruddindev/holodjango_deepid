"""
Minimal, framework-agnostic views. These use plain Django JsonResponse
rather than requiring Django REST Framework, so this package doesn't
force a dependency choice on consuming projects. Projects using DRF
are encouraged to write their own thin serializer-based views calling
the same `services` functions instead.
"""

import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from . import services


@login_required
@require_POST
def issue_first_sync_token(request):
    token = services.issue_first_sync_token(request.user)
    return JsonResponse(
        {
            "token": token.token,
            "expires_at": token.expires_at.isoformat(),
        }
    )


@csrf_exempt
@require_POST
def consume_first_sync_token(request):
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    token_value = payload.get("token")
    if not token_value:
        return JsonResponse({"error": "Missing 'token'."}, status=400)

    try:
        result = services.consume_first_sync_token(token_value)
    except services.InvalidTokenError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    return JsonResponse(
        {
            "user_id": result.user_id,
            "external_id": result.external_id,
        }
    )
