# XYZ – MINI-CRM Platform

**MINI-CRM** is a learning curve project, Where we can build a real-world CRM platform  
and This tool offers an interactive dashboard (in a nearest future) to keep track of Lead, Customer,
Sale opportunities and invoices information, I also keep my eyes on machine learning, how to use it to anaylize information,
and potential failures — all without needing access to a real production line.

## 🔍 Overview

The app Mini-CRM environment with:

- **User/Roles track**
- **Laad/Customers track**
- **Laad VOIP**
- **Salepersons track**
- **Tasks & Push notifications**
- **Products track**
- **Order invoice**
- **Authentication system with login/register**

**** Note: Safari on macOS does not currently support the 'notificationclick' event in service workers.
This event works in Chrome and Firefox, but not in Safari as of 2024.
There is no workaround to make 'notificationclick' work in Safari on macOS at this time.**** (THAT'S LIES)

It is perfect for engineers, students, or anyone interested in Customer Relationsip systems.

## ✨ Features

- 📊 **User/Roles track** – Tracking User and Roles record (add/edit).
- ⚙️ **Laad/Customers track** – Tracking Lead record and convert them to customers when it qualifies. 
- 🚀 **Invoice** – Createing invoice to customer when it ready for shipping.
- 🔐 **Authentication System** – Supports sign-in, registration, and protected dashboard access.
- 🌐 **Modular UI** – Built with a clean, tabbed navigation system for Lead, Customer, Products, and Invooice views.

## 🧰 Tech Stack

- **Frontend**: flask/jinjar/javascript 
- **Backend**: Python
- **Testing Framework**: Behave (Will be add in nesest future) 
- **Deployment**: Local or cloud-ready,docker

## 🚀 Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/Chananantachot/Mini-CRM.git
   cd Mini-CRM/src
   
2. on your termianl -> follow instructions of this link https://flask.palletsprojects.com/en/stable/installation/#create-an-environment
   or if you have it run
   ```bash
   . .venv/bin/activate
   
3.  ```bash
    pip install -r requirements.txt
    
4.  ```bash
    ./start.sh

5. Login loging with
   Username: admin@gmail.com
   Password: @dmin!23456

6. In order to setup Tasks push notifications automatically, you'll need to do the following bash command lines
  ```bash
      crontab -e


7. then Press i (swich to INSERT mode) and copy & paste this line script below in it
   ```bash
     0 9 * * * /usr/bin/python3 <FULL PATH>/scripts/notify_due_tasks.py
     
8. Press :wg to save and exit.     



