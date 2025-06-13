import os
import secrets
import sqlite3
import uuid

from flask import g, json
from werkzeug.security import generate_password_hash, check_password_hash
class Db:
    DATABASE = "customer.db"

    @staticmethod
    def get_db():
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(Db.DATABASE)
            db.row_factory = sqlite3.Row
        return db

    @staticmethod
    def init_db():
        db = Db.get_db()
        _cursor = db.cursor()

        # Create users tables 
        _cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                fullname TEXT NOT NULL,        
                email TEXT NOT NULL,
                salt TEXT NOT NULL,
                password TEXT NOT NULL,
                active INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP            
            )
        ''')

        # Create roles tables 
        _cursor.execute('''
            CREATE TABLE IF NOT EXISTS roles (
                id TEXT PRIMARY KEY,
                roleName TEXT NOT NULL,        
                description TEXT,
                active INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP              
            )
        ''')
        
        # Create userInRoles tables 
        _cursor.execute('''
            CREATE TABLE IF NOT EXISTS userInRoles (
                id TEXT PRIMARY KEY,        
                userId TEXT NOT NULL,
                roleId TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP                 
            )
        ''')

        # Create products tables 
        _cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                price DECIMAL(10, 2),
                sku TEXT UNIQUE,
                category TEXT,
                isActive BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP                  
            )''')

        # Create lead_prods_Interested tables 
        _cursor.execute('''
            CREATE TABLE IF NOT EXISTS lead_prods_Interested (
                id TEXT PRIMARY KEY,
                lead_id TEXT,
                product_id TEXT,        
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP                  
            )''')

        # Create orders tables 
        _cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                customerId TEXT NOT NULL,
                orderDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                totalAmount REAL NOT NULL,
                status TEXT NOT NULL, -- e.g., 'Pending', 'Completed', 'Cancelled'
                shippingAddressId TEXT, -- Reference to an address in the addresses table
                billingAddressId TEXT, -- Reference to an address in the addresses table
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customerId) REFERENCES customers(id),
                FOREIGN KEY (shippingAddressId) REFERENCES addresses(id),
                FOREIGN KEY (billingAddressId) REFERENCES addresses(id)
            )''')

        # Create order_items tables 
        _cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
            id TEXT PRIMARY KEY,
            orderId TEXT NOT NULL,
            productId TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unitPrice DECIMAL(10, 2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (orderId) REFERENCES orders(id),
            FOREIGN KEY (productId) REFERENCES products(id)
        )''')
        
        # Create leads tables 
        # represent potential customers who have shown interest but haven't yet been qualified or converted. 
        # The leads table can store details about how they were acquired and their current status.
        _cursor.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id TEXT PRIMARY KEY,        
                firstName TEXT NOT NULL,
                lastName TEXT NOT NULL, 
                email TEXT NOT NULL, 
                mobile TEXT,        
                source TEXT,      
                status TEXT,          
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP                    
            )
        ''')

        # Create opportunities tables 
        # The opportunities table stores potential sales or deals tied to a customer.
        # Opportunities include potential value, projected close date, and stage in the sales process 
        _cursor.execute('''
            CREATE TABLE IF NOT EXISTS opportunities (
                id TEXT PRIMARY KEY,        
                lead_id TEXT,
                current_stage VARCHAR(50),
                expected_value DECIMAL(10, 2),
                closure_date DATE,      
                converted BOOLEAN DEFAULT FALSE,        
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP                    
            )
        ''')  

        # Create customer tables 
        _cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id TEXT PRIMARY KEY,        
                firstName TEXT NOT NULL,
                lastName TEXT NOT NULL, 
                address TEXT,
                email TEXT NOT NULL, 
                mobile TEXT,      
                customer_typeId TEXT,          
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP                    
            )
        ''')

        # Create addresses tables 
        _cursor.execute('''
                CREATE TABLE IF NOT EXISTS addresses (
                id TEXT PRIMARY KEY,
                customerId TEXT NOT NULL,
                addressLine1 TEXT NOT NULL,
                addressLine2 TEXT,
                city TEXT NOT NULL,
                state TEXT,
                postalCode TEXT NOT NULL,
                country TEXT NOT NULL,
                addressType TEXT, -- e.g., 'Billing', 'Shipping', 'Home', 'Work'
                isPrimary BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customerId) REFERENCES customers(id)
            )''')

        # Create customerType tables 
        # possible data can be stored in (e.g., Regular, VIP)
        _cursor.execute('''
            CREATE TABLE IF NOT EXISTS customerType (
                id TEXT PRIMARY KEY,        
                typeName TEXT NOT NULL,        
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP                    
            )
        ''')


        # Create interactions tables  OR LOG 
        # This table records every interaction with your customers, 
        # from emails sent to follow-up calls or purchases made. 
        # It helps track the history of communications and activities related to each customer.
        _cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id TEXT PRIMARY KEY,        
                customer_id TEXT,
                interaction_type VARCHAR(50),
                date TIMESTAMP,
                notes TEXT,   
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP                    
            )
        ''')              
        db.commit()

    @staticmethod
    def seedAccount():
        roleId = Db.seedRole()

        fullname = 'Administrator'
        email = 'admin@gmail.com'
        password = os.getenv("ADMIN_PASSWORD")
    
        user = Db.getCurrentUser(email)
        if not user:
            salt = secrets.token_urlsafe(16)
            hashed_password = generate_password_hash(password + salt)
            userid = Db.createUser(fullname,email,salt,hashed_password)
            if userid:
                Db.activeUser(userid)
                if roleId:
                    Db.addUserInRoles(roleId,userid) 

    @staticmethod
    def seedRole():
        id = None
        roles = Db.getRole('Admin')
        if not roles:
            roleName = 'Admin' 
            description = 'An administrator role.'
            active = 1
            id = Db.createRole(roleName,description,active) 
        return id     

    @staticmethod
    def SeedCustomers():  
        customers = Db.getCustomers()
        if not customers:  
            data_path = os.path.join("static", "data", "MOCK_DATA.json")
            with open(data_path, "r") as f:
                customers = json.load(f)
                for cust in customers:
                    Db.createCustomer(cust['first_name'], cust['last_name'], cust['email'], cust['mobile'])

    @staticmethod
    def seedLeads():
        leads = Db.getLeads()
        if not leads:
            data_path = os.path.join("static", "data", "MOCK_DATA.json")
            with open(data_path, "r") as f:
                leads = json.load(f)
                for lead in leads:
                    Db.createLead(lead['first_name'], lead['last_name'], lead['email'], lead['mobile'] ,'Unknown','Unknown')

    @staticmethod
    def getCustomers():
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id, firstName,lastName , email, mobile, created_at, updated_at FROM customers')
         
        return cursor.fetchall()
    
    @staticmethod
    def getCustomer(id):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id, firstName,lastName , email, mobile, created_at, updated_at FROM customers Where id = ?', (id,))
         
        return cursor.fetchone()
    
    @staticmethod
    def getCustomerBy(fistName, lastName):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id FROM customers WHERE firstName COLLATE NOCASE = ? AND lastName COLLATE NOCASE = ?', (fistName,lastName,))
         
        return cursor.fetchone()

    @staticmethod
    def createCustomer(firstName,lastName,email,mobile):
        db = Db.get_db()
        cursor = db.cursor()
        id = str(uuid.uuid4())
        cursor.execute('INSERT INTO customers (id, firstName,lastName,email,mobile) VALUES (?,?,?,?,?)', (id,firstName,lastName,email,mobile,))
        db.commit()
        return id
    
    @staticmethod
    def covertLeadToCustomer(id,firstName,lastName,email,mobile):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO customers (id, firstName,lastName,email,mobile) VALUES (?,?,?,?,?)', (id,firstName,lastName,email,mobile,))

        cursor.execute('DELETE FROM leads WHERE id = id')
        db.commit()
        return id 
    
    @staticmethod
    def updateCustomer(id,firstName,lastName,email,mobile):
        db = Db.get_db()
        cursor = db.cursor()

        cursor.execute('''UPDATE customers SET 
                            firstName = ?,
                            lastName = ?,
                            email = ?, 
                            mobile = ?
                            WHERE id = ?'''
                            , (firstName,lastName,email,mobile,id,))
        db.commit()
        return id

    @staticmethod
    def getOpportunities(leadId):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('''
            SELECT 
                l.id as lead_id,           
                o.current_stage,
                o.expected_value,
                o.closure_date,
                o.converted,       
                o.created_at,
                o.updated_at               
            FROM opportunities o
            JOIN leads l ON o.lead_id = l.id AND l.id = ?
        ''', (leadId,))
        return cursor.fetchall() 
    
    @staticmethod
    def createOpportunities(lead_id,current_stage,expected_value,closure_date,converted):
        id = str(uuid.uuid4())
        db = Db.get_db()
        cursor = db.cursor() 
        cursor.execute('''
                        INSERT INTO opportunities(id,lead_id,current_stage,expected_value,closure_date,converted) 
                        VALUES (?,?,?,?,?,?) ''', (id,lead_id,current_stage,expected_value,closure_date,converted,))
        db.commit()

        if converted == 'Yes':
            Db.updateLeadStatus(lead_id, "Converted")
        return id

    @staticmethod
    def updateOpportunities(id,lead_id,current_stage,expected_value,closure_date,converted):
        db = Db.get_db()
        cursor = db.cursor()

        cursor.execute('''UPDATE opportunities SET 
                            lead_id = ?,
                            current_stage = ?,
                            expected_value = ?,
                            closure_date = ?,
                            converted = ?
                       WHERE id = ?
                       ''', (id,lead_id,current_stage,expected_value,closure_date,converted,))
        
        db.commit()
        if converted == 'Yes':
            Db.updateLeadStatus(lead_id, "Converted")

    @staticmethod
    def getLeads():
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('''
            SELECT 
                id,        
                firstName,
                lastName, 
                email, 
                mobile,
                source,      
                status,          
                created_at,
                updated_at 
            FROM leads        
        ''')
        return cursor.fetchall() 
     
    @staticmethod
    def getLeadBy(firstName,lastName):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('''
            SELECT 
                id,        
                firstName,
                lastName, 
                email, 
                source,      
                status,          
                created_at,
                updated_at 
            FROM leads
            WHERE firstName =? AND lastName =?            
        ''', (firstName,lastName,))
        return cursor.fetchone() 
    
    @staticmethod
    def getLead(id):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('''
            SELECT 
                id,        
                firstName,
                lastName, 
                email, 
                mobile,       
                source,      
                status,          
                created_at,
                updated_at 
            FROM leads       
        ''', (id,))
        return cursor.fetchone() 
    
    @staticmethod
    def getLeadConverted(id):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('''
            SELECT 
                id,        
                firstName,
                lastName, 
                email, 
                mobile,       
                source,      
                status,          
                created_at,
                updated_at 
            FROM leads
            WHERE id =? and status = 'Converted'            
        ''', (id,))
        return cursor.fetchone() 

        
    @staticmethod
    def createLead(firstName,lastName, email, mobile,source,status):
        id = str(uuid.uuid4())
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('''INSERT INTO leads 
                            (id,firstName,lastName, email, mobile, source,status) 
                            VALUES (?,?,?,?,?,?,?)
                       ''', (id,firstName,lastName,email,mobile,source,status,))
        db.commit()
        return id

    @staticmethod
    def updateLead(id,firstName,lastName, email, mobile, source,status):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('''UPDATE leads SET 
                                firstName = ?,
                                lastName = ?, 
                                email = ?,
                                mobile = ?,
                                source = ?,
                                status = ?
                            WHERE id = ?''', 
                        (firstName,lastName,email,mobile,source,status,id,))
        db.commit()
        return id

    @staticmethod
    def updateLeadStatus(id,status):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('''UPDATE leads SET 
                                status = ?
                            WHERE id = ?''', 
                        (status,id,))
        db.commit()
        return id


    @staticmethod
    def getCurrentUsers():
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id, fullname, email, active, created_at, updated_at FROM users')
         
        return cursor.fetchall()

    @staticmethod
    def getCurrentUser(id):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('SELECT fullname, email FROM users WHERE id = ?', (id,))
        return cursor.fetchone()

    @staticmethod
    def getCurrentActiveUser(email):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('''SELECT id,fullname,email,password,salt 
                        FROM users 
                        WHERE email = ?
                        AND active = 1''',(email,))
        user = cursor.fetchone()
        if user:
            roles = Db.getUserRoles(user['id'])
            
            user = dict(user)
            _roles = [dict(r) for r in roles]
            user['roles'] = [r['roleName'] for r in _roles]
        return user

    @staticmethod
    def createUser(fullname,email,salt,password):
        db = Db.get_db()
        cursor = db.cursor()
        userid = str(uuid.uuid4())
        cursor.execute('INSERT INTO users (id,fullname,email,salt,password) VALUES (?,?,?,?,?)', (userid,fullname,email,salt,password,))
        db.commit()
        return userid

    @staticmethod
    def UpdateUser(userId,fullname,email,active):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('''UPDATE users SET 
                            fullname = ?,
                            email = ?, 
                            active = ?
                            WHERE id = ?'''
                            , (fullname,email,active,userId,))
        db.commit()
        return True

    @staticmethod
    def activeUser(userId):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('UPDATE users SET active = 1 WHERE id = ?', (userId,))
        db.commit()
        return True

    @staticmethod
    def inactiveUser(userId):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('UPDATE users SET active = 0 WHERE id = ?', (userId,))
        db.commit()
        return True

    @staticmethod
    def getAssignedUserRoles(roleId):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute(f''' 
                       SELECT u.id, u.fullname, u.email,
                            CASE WHEN ur.roleId IS NOT NULL THEN 1 ELSE 0 END AS assigned
                        FROM users u
                        LEFT JOIN userInRoles ur ON u.id = ur.userId AND u.active = 1 AND ur.roleId = ?
                        ''', (roleId,))
        roles = cursor.fetchall()
        return roles

    @staticmethod
    def getUserRoles(userId):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute(f''' 
                        SELECT r.id,r.roleName 
                        FROM roles r
                        JOIN userInRoles ur ON r.id = ur.roleId
                        WHERE (ur.userId = ?)
                        AND r.active = 1
                        ''', (userId,))
        roles = cursor.fetchall()
        return roles
    
    @staticmethod
    def getRole(roleName):
        db = Db.get_db()
        cursor = db.cursor()
        if roleName:
            cursor.execute(f''' SELECT id,roleName,
                            description,active,
                            created_at,updated_at
                            FROM roles 
                            WHERE roleName = ? and active = 1
                        ''', (roleName,))
            return cursor.fetchone()
        return None

    @staticmethod
    def getRoles(id = None):
        db = Db.get_db()
        cursor = db.cursor()
        if id:
            cursor.execute(f''' SELECT id,roleName,
                            description,active,
                            created_at,updated_at
                            FROM roles 
                            WHERE id = ?
                        ''', (id,))
            roles = cursor.fetchone()
        else:    
            cursor.execute(f''' SELECT id,roleName,
                                description,active,
                                created_at,updated_at
                                FROM roles 
                            ''')
            roles = cursor.fetchall()
        return roles

    @staticmethod
    def createRole(roleName,description,active):
        db = Db.get_db()
        cursor = db.cursor()
        id = str(uuid.uuid4())
        cursor.execute('INSERT INTO roles (id,roleName,description,active) VALUES (?,?,?,?)', (id,roleName,description,active,))
        db.commit()
        return id
    
    @staticmethod
    def UpdateRole(id,roleName,description,active):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('''UPDATE users SET 
                            roleName = ?,
                            description = ?, 
                            active = ?
                            WHERE id = ?'''
                            , (roleName,description,active,id,))
        db.commit()
        return True
    
    @staticmethod
    def addUserInRoles(roleId,userId):
        _id = str(uuid.uuid4())
        db = Db.get_db()
        cursor = db.cursor()
        
        cursor.execute('INSERT INTO userInRoles (id, roleId, userId) VALUES (?,?,?)', (_id,roleId,userId,))
        db.commit()
        return True

    @staticmethod
    def deleteUserRoles(roleid, userId):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('DELETE FROM userInRoles WHERE roleId = ? AND userId = ?', (roleid,userId,))
        db.commit()
        return True