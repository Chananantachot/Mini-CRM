import os
import secrets
import sqlite3
import uuid

from flask import g, json
from werkzeug.security import generate_password_hash, check_password_hash
class Db:
    DATABASE = "crm.db"

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
                sku TEXT,
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
                invoiceNO TEXT NOT NULL,
                customerId TEXT NOT NULL,
                orderDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                amount DECIMAL(10, 2) NOT NULL,      
                tax DECIMAL(10, 2) NOT NULL,           
                total DECIMAL(10, 2) NOT NULL,
                status TEXT NOT NULL, -- e.g., 'Pending', 'Completed', 'Cancelled'
                shippingAddress TEXT,
                billingAddress TEXT, 
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customerId) REFERENCES customers(id)
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
                salesPersonId TEXT, -- Optional: to link to a salesperson      
                firstName TEXT NOT NULL,
                lastName TEXT NOT NULL, 
                email TEXT NOT NULL, 
                mobile TEXT,        
                source TEXT,      
                status TEXT,          
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (salesPersonId) REFERENCES sales(id)                            
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
                expected_value DECIMAL(10, 2), -- this will be calculated based on the deal value and conversion probability: deal_value × conversion_probability
                deal_value DECIMAL(10, 2),        
                conversion_probability DECIMAL(5,2) DEFAULT 0.00 CHECK (conversion_probability BETWEEN 0 AND 1), -- (%) value
                closure_date DATE,         
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

        # Creating your new salespeople table
        _cursor.execute('''CREATE TABLE IF NOT EXISTS sales (
            id TEXT PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(150) UNIQUE,
            phone VARCHAR(20),
            region VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

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
                customer_id TEXT NOT NULL,
                product_id TEXT NOT NULL, -- if applicable, to track interactions related to specific products
                interaction_type VARCHAR(50), -- e.g., 'Email', 'Call', 'Meeting', 'Purchase'
                date_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT NOT NULL, -- any notes or details about the interaction
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP                    
            )
        ''')              
        
        # _cursor.execute('DELETE FROM orders')
        # _cursor.execute('DELETE FROM order_items')
        # _cursor.execute('DELETE FROM lead_prods_Interested')
        
        db.commit()

    @staticmethod
    def seedAccount():
        users = Db.getCurrentUsers()
        if users:
            return 
        
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


    # Seed the database
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
        leads = Db.getLeads(None)
        if not leads:
            data_path = os.path.join("static", "data", "MOCK_DATA.json")
            with open(data_path, "r") as f:
                leads = json.load(f)
                for lead in leads:
                    Db.createLead(lead['first_name'], lead['last_name'], lead['email'], lead['mobile'] ,'Unknown','Unknown')

    @staticmethod
    def SeedProducts():  
        products = Db.getProducts()
        if not products:  
            data_path = os.path.join("static", "data", "MOCK_PRODS.json")
            with open(data_path, "r") as f:
                products = json.load(f)
                for prod in products:
                    Db.createProduct(prod['name'],prod['description'], prod['price'],prod['sku'],prod['category'],True)

    #Dashboard Data
    @staticmethod
    def getCustomerDashboardData():
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('''
            SELECT 
                COUNT(DISTINCT c.id) AS totalCustomers,
                COUNT(DISTINCT l.id) AS totalLeads,
                COUNT(DISTINCT o.id) AS totalOrders,
                SUM(o.total) AS totalSales
            FROM customers c
            LEFT JOIN leads l ON c.id = l.id
            LEFT JOIN orders o ON c.id = o.customerId
        ''')
        return cursor.fetchone()
    
    @staticmethod
    def getSalesDashboardData():
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('''
            SELECT 
                COUNT(DISTINCT o.id) AS totalOrders,
                SUM(o.total) AS totalSales,
                COUNT(DISTINCT c.id) AS totalCustomers,
                COUNT(DISTINCT l.id) AS totalLeads
            FROM orders o
            LEFT JOIN customers c ON o.customerId = c.id
            LEFT JOIN leads l ON c.id = l.id
        ''')
        return cursor.fetchone()
    
    @staticmethod
    def getOpportunitiesDashboardData():
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('''
            SELECT 
                COUNT(DISTINCT o.id) AS totalOpportunities,
                SUM(o.expected_value) AS totalExpectedValue,
                COUNT(DISTINCT l.id) AS totalLeads
            FROM opportunities o
            LEFT JOIN leads l ON o.lead_id = l.id
        ''')
        return cursor.fetchone()

    @staticmethod
    def getProductsDashboardData():
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('''
            SELECT 
                COUNT(DISTINCT p.id) AS totalProducts,
                SUM(p.price) AS totalProductValue,
                COUNT(DISTINCT i.product_id) AS totalInterestedProducts
            FROM products p
            LEFT JOIN lead_prods_Interested i ON p.id = i.product_id
        ''')
        return cursor.fetchone()   


    #ORDERS    
    @staticmethod
    def createOrder(order, orderItems):
        db = Db.get_db()
        cursor = db.cursor()
        try:
            # Start the transaction
            cursor.execute("BEGIN")
            cursor.execute(''' INSERT INTO orders (id,invoiceNO,customerId,amount, tax, total,status,shippingAddress,billingAddress)
                            VALUES (?,?,?,?,?,?,?,?,?)
                    ''',order)
            
            # Insert each order item (assuming each item is a tuple: (order_id, product_name, quantity, price))
            cursor.executemany('''
                        INSERT INTO order_items (id,orderId,productId,quantity,unitPrice)
                        VALUES (?,?,?,?,?)
                        ''', orderItems)
            
            cursor.execute('DELETE FROM lead_prods_Interested WHERE lead_id = ?',(order[2],)) # Assuming order[2] is customerId
            db.commit()
        
        except Exception as e:
            db.rollback()
            print("Transaction failed:", e)

        finally:
            return order[0]

    @staticmethod
    def updateOrder(order, orderItems):
        db = Db.get_db()
        cursor = db.cursor()
        try:
            # Start the transaction
            cursor.execute("BEGIN")
            cursor.execute(''' UPDATE orders SET amount = ?, 
                                    tax = ?, 
                                    total = ?,
                                    status = ?,
                                    shippingAddress = ?,
                                    billingAddress = ?
                                WHERE id = ? and customerId = ?
                             ''',order)
            
            # Insert each order item (assuming each item is a tuple: (order_id, product_name, quantity, price))
            cursor.executemany('''UPDATE order_items SET quantity = ?,
                                    unitPrice = ?
                                WHERE orderId = ? and productId = ?
                                 ''', orderItems)

            db.commit()
        
        except Exception as e:
            db.rollback()
            print("Transaction failed:", e)

        finally:
            return order[6]

    @staticmethod
    def updateOrderStatus(orderId, status):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute(''' UPDATE orders SET status = ? WHERE id = ? ''', (status, orderId,))
        db.commit()
        return orderId
    
    @staticmethod 
    def getCustomerInvoiceDetail(custId):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('''
            SELECT 
                o.orderDate,
                COALESCE(o.id,'') as orderId,   
                COALESCE(o.invoiceNO,'') as invNumber,         
                COALESCE(o.status,'Pending') as status,     
                COALESCE(o.total,0.00) as total
            FROM  orders o    
            LEFT JOIN customers c on c.id = o.customerId          
            WHERE c.id = ?                  
            ''', (custId,))
        return cursor.fetchall()

    @staticmethod
    def getCustomerOrder(id,orderId):
        db = Db.get_db()
        cursor = db.cursor() 
        cursor.execute(f'''
            SELECT c.id as customerId,
                c.firstName || ' ' || c.lastName as client,
                COALESCE(o.orderDate,'') as orderDate,
                COALESCE(o.id,'') as orderId,   
                COALESCE(o.invoiceNO,'') as invNumber,  
                COALESCE(o.id,'') as orderId,         
                COALESCE(o.billingAddress,a.addressLine1 || ', ' ||  a.addressLine2 || ', '|| a.state || ', ' ||  a.postalCode || ' '||  a.country) as billingAddress,
                COALESCE(o.shippingAddress,a.addressLine1 || ', ' ||  a.addressLine2 || ', '|| a.state || ', ' ||  a.postalCode || ' '||  a.country) as shippingAddress,  
                COALESCE(o.status,'Pending') as status,     
                COALESCE(o.amount,0.00) as amount,
                COALESCE(o.tax,0.00) as tax,
                COALESCE(o.total,0.00) as total, 
                a.addressLine1,
                a.addressLine2,
                a.city,
                a.state,
                a.postalCode,
                a.country,
                a.addressType,                
                a.isPrimary
            FROM  customers c 
            LEFT JOIN orders o on c.id = o.customerId 
            LEFT JOIN addresses a on c.id = a.customerId and a.isPrimary = 1          
            WHERE c.id = ? AND (? IS NULL OR o.id = ?)
            ''',(id,orderId,orderId,))
        return cursor.fetchall()

    @staticmethod
    def getCustomerInvoiceLeftInProdInterested(custId):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('''
            SELECT 
                c.id as customerId,
                CASE WHEN COUNT(i.product_id) > 0 THEN 1 ELSE 0 END as orderLeft  
            FROM  lead_prods_Interested i
            LEFT JOIN customers c on c.id = o.customerId and c.id =i.lead_id    
            LEFT JOIN orders o on c.id = o.customerId  OR o.customerId =i.lead_id AND o.id IS NULL   
            WHERE (c.id = ?)                 
            ''', (custId,))
        return cursor.fetchall()


    #LEAD PRODUCTS INTERESTED
    @staticmethod
    def getleadProdsInterested(id):
        db = Db.get_db()
        cursor = db.cursor()

        cursor.execute(''' 
                    SELECT p.id, p.name, p.price, p.description,
                        CASE WHEN i.product_id IS NOT NULL THEN 1 ELSE 0 END AS interested  
                    FROM products p  
                    LEFT JOIN lead_prods_Interested i ON i.product_id = p.id and (i.lead_id = ? OR ? is NULL)
                    LEFT JOIN customers c ON c.id = i.lead_id OR (c.id = ? OR ? IS NULL) 
        ''', (id,id,id,id,))

        return cursor.fetchall()   

    @staticmethod
    def getCustProdsOrders(id,orderId):
        db = Db.get_db()
        cursor = db.cursor()
        # Always use the same query, but adjust the JOINs and WHERE clause to cover both cases
        cursor.execute('''
            SELECT
            oi.orderId,
            c.id as customerId,
            p.id AS productId,
            p.name AS productName,
            p.description,
            COALESCE(oi.quantity, 1.0) AS quantity,
            p.price AS unitPrice
            FROM products p
            LEFT JOIN lead_prods_Interested i ON i.product_id = p.id
            LEFT JOIN order_items oi ON oi.productId = p.id OR oi.productId = i.product_id
            LEFT JOIN orders o ON o.id = oi.orderId
            LEFT JOIN customers c ON c.id = o.customerId OR c.id = i.lead_id
            WHERE (c.id = ? OR ? IS NULL) AND (oi.orderId = ? OR ? IS NULL)
        ''', (id, id, orderId, orderId,))
                
        return cursor.fetchall()

    @staticmethod
    def createLeadProdsInterested(leadId,productId):
        id = str(uuid.uuid4())
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute(''' 
                        INSERT INTO lead_prods_Interested(id,lead_id,product_id) VALUES (?,?,?) 
                       ''', (id,leadId,productId,))
        db.commit()
        return leadId

    @staticmethod
    def deleteLeadProdsInterested(leadId,productId):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('DELETE FROM lead_prods_Interested WHERE lead_id = ? AND product_id = ?',(leadId,productId,))

        db.commit()
        return leadId 


    #PRODUCTS
    @staticmethod
    def getProducts():
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute(''' SELECT id,
                                name,
                                description,
                                price,
                                sku,
                                category,
                                isActive
                           FROM products
                ''')    
        return cursor.fetchall()

    @staticmethod
    def getProduct(id):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute(''' SELECT id,
                                name,
                                description,
                                price,
                                sku,
                                category,
                                isActive
                           FROM products
                           WHERE id = ?
                ''',(id,))    
        return cursor.fetchone()
    
    @staticmethod
    def getProductBy(sku):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute(''' SELECT id,
                                name,
                                description,
                                price,
                                sku,
                                category,
                                isActive
                           FROM products
                           WHERE sku = ?
                ''',(sku,))    
        return cursor.fetchone()
    
    @staticmethod
    def createProduct(name, description, price,sku,category,isActive):
        id = str(uuid.uuid4())
        isActive = 1 if isActive == 'Yes' else 0

        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute(''' INSERT INTO products (id,name, description, price,sku,category,isActive)
                           VALUES (?,?,?,?,?,?,?)
                ''',(id,name, description, price,sku,category,isActive,))
        db.commit()
        return id

    @staticmethod
    def updateProduct(id ,name, description, price,sku,category,isActive):     
        isActive = 1 if isActive == 'Yes' else 0

        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute(''' UPDATE products SET 
                            name = ?, 
                            description = ?, 
                            price = ?,
                            sku = ?,
                            category = ?,
                            isActive =?
                         WHERE id = ?   
                       ''',(name, description, price,sku,category,isActive,id,))
        db.commit()
        return id



    #CUSTOMER ADDRESS
    @staticmethod
    def getCustomerPrimaryAddress(id):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('''SELECT id, 
                                customerId,
                                addressLine1,
                                addressLine2,
                                city,
                                state,
                                postalCode,
                                country,
                                addressType,
                                isPrimary
                            FROM addresses
                            WHERE customerId = ? and isPrimary = 1
                       ''',(id,)
                       )
        return cursor.fetchall()
    
    @staticmethod
    def getCustomerAddress(id):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('''
                            SELECT id,
                                customerId,
                                addressLine1,
                                addressLine2,
                                city,
                                state,
                                postalCode,
                                country,
                                addressType,
                                isPrimary
                            FROM addresses
                            WHERE customerId = ?
                            ''',(id,))
        return cursor.fetchall()

    @staticmethod
    def getCustomerAddressBy(id):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('''
                            SELECT id,
                                customerId,
                                addressLine1,addressLine2,
                                city,state,postalCode,
                                country,addressType,
                                isPrimary
                            FROM addresses
                            WHERE id = ?
                            ''',(id,))
        return cursor.fetchone()
    
    @staticmethod
    def createCustomerAddress(customerId, addressLine1,addressLine2,
                                city,state,postalCode,country,addressType,
                                isPrimary):    
        id = str(uuid.uuid4())
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute(''' INSERT INTO addresses (id ,customerId, addressLine1,addressLine2,
                                                    city,state,postalCode,country,addressType,
                                                    isPrimary)
                                                VALUES (?,?,?,?,?,?,?,?,?,?)
                        ''', (id,customerId, addressLine1,addressLine2,city,state,postalCode,country,addressType,
                                isPrimary,))
        db.commit()
        return id
    
    @staticmethod
    def updateustomerAddress(id,customerId, addressLine1,addressLine2,
                                city,state,postalCode,country,addressType,
                                isPrimary):    
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute(''' 
                            UPDATE addresses SET customerId = ?,
                                                    addressLine1 = ?,
                                                    addressLine2 = ?,
                                                    city = ?,
                                                    state = ?,
                                                    postalCode = ?,
                                                    country = ?,
                                                    addressType = ?,
                                                    isPrimary =?
                                WHERE id = ?
                    ''', (customerId, addressLine1,addressLine2,city,state,postalCode,country,addressType,
                                isPrimary,id,))
        db.commit()
        return id
    
    @staticmethod
    def deleteCustomerAddress(id, custId):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute(''' DELETE FROM addresses WHERE id = ? AND customerId = ?''',(id,custId,))
        db.commit()
    #-------------------------------------------------------------


    #CUSTOMERS
    @staticmethod
    def getCustomers():
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('''
            SELECT c.id, 
                c.firstName,
                c.lastName , 
                c.email, 
                c.mobile,       
                c.created_at, 
                c.updated_at 
            FROM customers c            
            LEFT JOIN addresses a ON a.customerId = c.id AND a.isPrimary = 1  
            ''')
         
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

        cursor.execute('DELETE FROM leads WHERE id = ?',(id,))
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
    
   #-------------------------------------------------------------


    #OPPORTUNITIES
    @staticmethod
    def getOpportunities(leadId):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('''
            SELECT 
                o.id,
                l.id as lead_id,           
                o.current_stage,
                o.expected_value,
                o.closure_date,
                CASE WHEN c.id IS NULL THEN 0 ELSE 1 END as  converted,   
                o.created_at,
                o.updated_at               
            FROM opportunities o
            JOIN leads l ON o.lead_id = l.id AND l.id = ?
            LEFT JOIN customers c ON c.id = l.id            
        ''', (leadId,))
        return cursor.fetchall() 
    
    @staticmethod
    def getOpportunity(id,leadId):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('''
        SELECT 
                o.id,
                l.id as lead_id,           
                o.current_stage,
                o.expected_value,
                o.closure_date,
                CASE WHEN c.id IS NULL THEN 0 ELSE 1 END as  converted,   
                o.created_at,
                o.updated_at               
            FROM opportunities o
            JOIN leads l ON o.lead_id = l.id AND l.id = ? AND o.id = ?
            LEFT JOIN customers c ON c.id = l.id         
        ''', (leadId,id,))
        return cursor.fetchone() 
    
    @staticmethod
    def createOpportunities(lead_id,current_stage,expected_value,closure_date):
        id = str(uuid.uuid4())
        db = Db.get_db()
        cursor = db.cursor() 
        cursor.execute('''
                        INSERT INTO opportunities(id,lead_id,current_stage,expected_value,closure_date) 
                        VALUES (?,?,?,?,?) ''', (id,lead_id,current_stage,expected_value,closure_date,))
        db.commit()
        return id

    @staticmethod
    def updateOpportunities(id,lead_id,current_stage,expected_value,closure_date):
        db = Db.get_db()
        cursor = db.cursor()

        cursor.execute('''UPDATE opportunities SET 
                            lead_id = ?,
                            current_stage = ?,
                            expected_value = ?,
                            closure_date = ?
                       WHERE id = ?
                       ''', (lead_id,current_stage,expected_value,closure_date,id,))
        
        db.commit()
        return id



    #LEADS
    @staticmethod
    def getLeads(id):
        db = Db.get_db()
        cursor = db.cursor()
        cursor.execute('''        
        SELECT id,
                firstName,
                lastName, 
                email, 
                mobile,
                source,      
                status,          
                created_at,
                updated_at
            FROM         
                (SELECT 
                    id,
                    firstName,
                    lastName,
                    email,
                    mobile,
                    '' as source,
                    'Converted' as status,
                    created_at,
                    updated_at
                    FROM customers 
                UNION
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
                    FROM leads) t  
        WHERE t.id = ? OR ? IS NULL
        ''', (id,id,))
               
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
            WHERE id = ?           
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



    #USERS
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



    #USER ROLES
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