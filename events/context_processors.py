def role_context_processor(request):
    user = request.user
    if user.is_authenticated:
        roles = [group.name for group in user.groups.all()]
    else:
        roles = []
    return {
        'user_roles': roles
    }