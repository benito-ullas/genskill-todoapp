import requests
from requests.auth import HTTPBasicAuth
import pytest
import json

base_url = "http://localhost:5000"


def login(user,pas):
        url = base_url + "/login"
        
        r = requests.get(url,auth=HTTPBasicAuth(user, pas))
        return r

admin_token = login("admin","12345").json()['token']


#no username and password
def test_1():
        r = login("","")
        assert r.text == 'Could not verify'

#username and password not matching
def test_2():
        r = login("benito","123456")
        assert r.text == 'Could not verify! username and password not matching'
        
#check for token
def test_3():
        r = login("benito","12345")
        assert r.json()['token']
      
#creating a user
def test_4():
        url = base_url + "/auth/user"
        username = "test1"
        password = "test1"
        data = {"username": username, "password": password}
        r = requests.post(url,json=data)
        assert r.json()['message'] == f'new user {username} added'
        
#getting all users by admin       
def test_5():
        url = base_url + "/auth/user"
        headers = {"x-access-token": admin_token}
        r = requests.get(url,headers=headers)
        assert r.json()['users']

#getting all users by test1
def test_6():
        url = base_url + "/auth/user"
        test1_token = login("test1","test1").json()['token']
        headers = {"x-access-token": test1_token}
        r = requests.get(url,headers=headers)
        assert r.json()['message'] == 'cannot perform this task'
        
def get_public_id(un):
        url = base_url + "/auth/user"
        headers = {"x-access-token": admin_token}
        r = requests.get(url,headers=headers)
        users = r.json()['users']
        
        for i in users:
                if i['username'] == un:
                        return i['public_id']
        
        
# using test1 to admin data
def test_7():
        p_id = get_public_id("admin")
        url = base_url + f"/auth/user/{p_id}"
        test1_token = login("test1","test1").json()['token']
        headers = {"x-access-token": test1_token}
        r = requests.get(url,headers=headers)
        assert r.json()['message'] == 'cannot view this page'
        
# testing a user not on the database
def test_8():
        url = base_url + f"/auth/user/1"
        
        headers = {"x-access-token": admin_token}
        r = requests.get(url,headers=headers)

        assert r.json()['message'] == 'no such user! Enter valid id'
        
# using admin to see test1 data
def test_9():
        p_id = get_public_id("test1")
        url = base_url + f"/auth/user/{p_id}"
        headers = {"x-access-token": admin_token}
        r = requests.get(url,headers=headers)
        assert r.json()['username'] == 'test1'
        assert r.json()['public_id'] == p_id
        
# using test1 to see test1 data
def test_10():
        p_id = get_public_id("test1")
        url = base_url + f"/auth/user/{p_id}"
        test1_token = login("test1","test1").json()['token']
        headers = {"x-access-token": test1_token}
        r = requests.get(url,headers=headers)
        assert r.json()['username'] == 'test1'
        assert r.json()['public_id'] == p_id

# using test1 to promote himself to admin
def test_11():        
        p_id = get_public_id("test1")
        url = base_url + f"/auth/user/{p_id}"
        test1_token = login("test1","test1").json()['token']
        headers = {"x-access-token": test1_token}
        r = requests.put(url,headers=headers)
        assert r.json()['message'] == 'cannot perform this task'

# testing a user not on the database
def test_12():
        url = base_url + f"/auth/user/1"
        
        headers = {"x-access-token": admin_token}
        r = requests.put(url,headers=headers)

        assert r.json()['message'] == 'no such user! Enter valid id'
        
# using admin to promote test1 to admin
def test_13():
        p_id = get_public_id("test1")
        url = base_url + f"/auth/user/{p_id}"
        
        headers = {"x-access-token": admin_token}
        r = requests.put(url,headers=headers)
        
        assert r.json()['message'] == 'user now has admin privilages'
        
# using benito to delete test1
def test_14():
        p_id = get_public_id("test1")
        url = base_url + f"/auth/user/{p_id}"
        benito_token = login("benito","12345").json()['token']
        headers = {"x-access-token": benito_token}
        r = requests.put(url,headers=headers)
        assert r.json()['message'] == 'cannot perform this task'
        
# using test1 to delete test1
def test_15():
        p_id = get_public_id("test1")
        url = base_url + f"/auth/user/{p_id}"
        test1_token = login("test1","test1").json()['token']
        headers = {"x-access-token": test1_token}
        r = requests.delete(url,headers=headers)
        
        assert r.json()['message'] == 'user has been deleted'        
        
# trying to get test1 token again
def test_16():
        p_id = get_public_id("test1")
        url = base_url + f"/auth/user/{p_id}"
        r = login("test1","test1")
       
        assert r.text == 'Could not verify'
        
        
        
