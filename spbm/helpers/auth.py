def user_allowed_society(usr, soc):
    if usr.is_superuser:
        return True

    if usr.spfuser.society == soc:
        return True

    return False

def user_society(request):
    return request.user.spfuser.society