# Innovaccer SDE-Intern Assignment
> Entry Management software

## Table of contents
* [Installation](#installation)
* [Database](#database-structure)
* [Tech Stack](#tech-stack)
* [Approach](#approach)
* [Routes](#server-routes)
* [Screenshots](#screenshots)

## Installation

1. Install PIP with `sudo apt-get install python3-pip`

2. Clone the repo:

   ```bash
   git clone https://github.com/zeeshanhussain/Entry-Management
   cd Entry-Management
   ```
3. Set up the virtual environment

   ```
   virtualenv venv
   .venv/bin/activate
   ```
4. Install dependencies with
   ```
   pip3 install -r requirements.txt
   ```
5. Setup Environment Variables for Email and Sms services
   ```
   #Smtp Configs

   MAIL_SERVER = 'smtp.xxxxx.com'
   MAIL_USERNAME = 'xxxxxx@xxxxx.xxx'
   MAIL_PASSWORD = 'xxxxxxxxxxx'
   SENDER_USERNAME = 'xxxxxx@xxxxx.xxx'

   #Twilio Configs
   ACCOUNT_SID = 'accountsid'
   AUTH_TOKEN = 'authtoken'
   TWILIO_NUMBER=+xxyyyyyyyyyy
   ```

6. Run the server with `python3 app.py`

7. Navigate to http://localhost:5000


## Database Structure

Database ```Em``` consists of 2 Collections

> Host Collection
```
{
  _id: ObjectId,
  name: String,
  email: String,
  password: Binary,
  number: String,
  address: String,
  available: Boolean
}
```
> Visitor Collection

```
{
  _id: ObjectId,
  name: String,
  host_id: String,
  email: String,
  number: String,
  checkin: Int32,
  checkout: Int32
}
```

## Tech Stack
> Backend
* Flask
* MongoDB
> Frontend
* Html
* Css
* Bootstrap
> Dependencies
* Flask-wtf
* Wtf-forms
* Twilio
* Flask_pymongo
* Flask-Mail

## Approach

* Hosts can register themselves using Register Form and can login themselves using Login Form. For now, anyone can register and become a host. Complete Validation of forms is done using Flask-WTF. Hosts details will be stored in the host collection of the database.

* When a visitor comes at the office, he/she can select a host to visit from the list of available hosts. A host will not be available if he/she is attending a visitor. Email and Sms will be sent to the host when someone checks in using flask-mail and Twilio Services. The visitor's details will be stored in the visitor collection of the database and the host document will be updated to make him not available.

* Visitors can checkout using their email address. Visitors will be sent an email providing all the details of his visit. The visitor's checkout time will be updated in the database. The host will be updated as available when the visitor checks out.

* Hosts can see details of all his active and past visitors.



## Server Routes

* `{baseURL}/home`

   * If the Host is logged in, then this will show a table of his Active and Past Visitors.
   * If the Host is logged off, then this will show the home page.

* `{baseURL}/login`

   * If the Host is logged in, then this will redirect to `/home`.
   * Login form will be rendered using the GET method of request.
   * Login form will be submitted and validated using the Post method of request.

* `{baseURL}/register`

   * If the Host is logged in, then this will redirect to `/home`.
   * Register form will be rendered using the GET method of request.
   * Register form will be submitted and validated using the Post method of request.

* `{baseURL}/checkin`

  * If the Host is logged in, then this will redirect to `/home`.
  * Check In form will be rendered using the GET method of request.
  * Check In form will be submitted and validated using the Post method of request.
  * Email and Sms will be sent through flask-mail and Twilio services.

* `{baseURL}/checkout`

  * If the Host is logged in, then this will redirect to `/home`.
  * Check Out form will be rendered using the GET method of request.
  * Check Out form will be submitted and validated using the Post method of request.
  * Email and Sms will be sent through flask-mail and Twilio services.

* `{baseURL}/logout`

  * If the Host is logged in, then this will logout host and redirect to `/home`.
  * If the Host is logged off, then this will redirect to `/home`.

## ScreenShots

> Home Page

![ScreenShot](/screenshots/home.png)

> Check-In Page (Available hosts can be selected from the dropdown)

![ScreenShot](/screenshots/visitor_checkin.png)

> Check-Out Page

![ScreenShot](/screenshots/visitor_checkout.png)

> Host Login Page

![ScreenShot](/screenshots/host_login.png)

> Host Register Page

![ScreenShot](/screenshots/host_register.png)

> Visitor Details Page (the host can see details of his current and past visitors)

![ScreenShot](/screenshots/visitors_details.png)
