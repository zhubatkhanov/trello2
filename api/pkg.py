import jwt

def checkJWT(request):
    token = request.COOKIES.get('jwt')
        
    if not token:
        return False
    
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except:
        return False
    
    return True