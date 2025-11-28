# assets/middleware.py
from django.http import JsonResponse

class RBACMiddleware:
    """
    Adds request.base_filter for COMMANDER role and restricts LOGISTICS for endpoints.
    Keep simple — for demo only.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            if hasattr(user, "role") and user.role == "ADMIN":
                return self.get_response(request)

            if hasattr(user, "role") and user.role == "COMMANDER":
                request.base_filter = user.base

            if hasattr(user, "role") and user.role == "LOGISTICS":
                # allow purchases and transfers; deny other modifications
                path = request.path.lower()
                if not (path.startswith("/api/purchase") or path.startswith("/api/transfer") or path.startswith("/admin")):
                    # allow safe GETs
                    if request.method not in ("GET", "POST", "PUT", "PATCH", "DELETE"):
                        return self.get_response(request)
                    # for this demo, logistics only allowed on purchase and transfer endpoints
                    return JsonResponse({"detail": "Access denied for this role."}, status=403)

        return self.get_response(request)
