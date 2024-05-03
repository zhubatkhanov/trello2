import requests
import uuid

ENDPOINT = "http://127.0.0.1:8000/api/v1"


def test_user_register():
    payload = new_user_payload()
    create_user_response = create_user(payload)
    assert create_user_response.status_code == 200
    
def test_user_login():
    payload = new_user_payload()
    create_user_response = create_user(payload)
    assert create_user_response.status_code == 200
    
    data = create_user_response.json()
    email = data["email"]
    password = "12345678"
    login_user_response = login_user(
        {
            "email": email,
            "password": password
        }
    )
    assert login_user_response.status_code == 200
    jwt_token = login_user_response.json()["jwt"]
    return jwt_token
    
def test_info_user():
    jwt = test_user_login()
    info_user_response = info_user(jwt)
    assert info_user_response.status_code == 200
    
def test_create_bord():
    jwt = test_user_login()
    
    board_payload = new_board_payload()
    create_board_response = create_board(board_payload, jwt)
    assert create_board_response.status_code == 200
    
    data = create_board_response.json()
    board_id = data["id"]
    get_board_response = get_board(board_id, jwt)
    assert get_board_response.status_code == 200
    get_board_data = get_board_response.json()
    assert get_board_data["name"] == board_payload["name"] 



def create_user(payload):
    return requests.post(ENDPOINT + "/register", json=payload)
    
def login_user(payload):
    return requests.post(ENDPOINT + "/login", json=payload)

def info_user(jwt):
    cookies = {"jwt": jwt}
    return requests.get(ENDPOINT + "/user", cookies=cookies)

def create_board(payload, jwt):
    cookies = {"jwt": jwt}
    return requests.post(ENDPOINT + "/board", json=payload, cookies=cookies)

def get_board(board_id, jwt):
    cookies = {"jwt": jwt}
    return requests.get(ENDPOINT + f"/boards/{board_id}",  cookies=cookies)


def new_user_payload():
    email = f"test_email_{uuid.uuid4().hex}@gmail.com"
    username = f"test_username_{uuid.uuid4().hex}"
    payload = {
            "username": username,
            "email": email,
            "password": "12345678"
    }
    return payload

def new_board_payload():
    name = f"test_board_{uuid.uuid4().hex}"
    payload = {
        'name': name,
    }
    return payload


def new_board_name():
    return f"test_board_{uuid.uuid4().hex}"