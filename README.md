# WOW API DOCUMENTATION

This API was designed as part of a training project for developing android mobile app and interacting with a remote API server.
> **Warning:** Don't use for **Production**.

# Setup flask server
**Create virtual env**
``python3 -m venv flask_venv && source flask_venv/bin/activate``

**Install dependencies**
``pip3 install -r requirements``

**Start server**
``python3 main.py``
Server  running on http://localhost:5000

# Endpoints

## [POST]: /register
### body
    {
    	"fullname":"Yves Mousouba",
    	"password":"1234",
    	"phone":"+33758657147"
    }
### result
    {
    	"message": "User registered successfully"
    }

## [POST]: /login
### body
    {
    	"password":"1234",
    	"phone":"+33758657147"
    }
### result
    {
		"access_token": "<jwt_access_token>",
		"fullname": "Yves Mousouba",
		"id": 1,
		"phone": "+33758657147"
	}

## [GET]: /balance
### headers
    {
    	"Authorization":"Bearer <jwt_access_token>"
    }
### result
    {
		"id": 1,
		"balance": "500 XOF"
	}
	
## [POST]: /transaction
### headers
    {
    	"Authorization":"Bearer <jwt_access_token>"
    }
### body
    {
		"receiver_phone": "<receiver_phone>",
		"amount": "500"
	}
### result
    {
		"message": "Money sent successfully"
	}
	
## [GET]: /transactions
### headers
    {
    	"Authorization":"Bearer <jwt_access_token>"
    }
### result
    [
		{
			"amount": "-500 XOF",
			"id": 1,
			"message": "A <receiver_fullname>",
			"sent_at": "2024-01-04"
		},
		{
			"amount": "+250 XOF",
			"id": 2,
			"message": "De <sender_fullname>",
			"sent_at": "2024-01-04"
		},
		...
	]
