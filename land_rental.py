import mysql.connector

def connect_db():
    c = mysql.connector.connect(host="localhost", user="root", password="Cbse@2026")
    cr = c.cursor()
    cr.execute("CREATE DATABASE IF NOT EXISTS land_rental_db")
    cr.execute("USE land_rental_db")
    
    cr.execute("""CREATE TABLE IF NOT EXISTS owners(
                owner_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(15) UNIQUE NOT NULL,
                address VARCHAR(200))""")
                
    cr.execute("""CREATE TABLE IF NOT EXISTS lands(
                land_id INT AUTO_INCREMENT PRIMARY KEY,
                owner_id INT,
                location VARCHAR(100),
                total_area FLOAT,
                min_area FLOAT,
                max_area FLOAT,
                rent_amount FLOAT,
                status VARCHAR(20) DEFAULT 'Available',
                FOREIGN KEY (owner_id) REFERENCES owners(owner_id) ON DELETE CASCADE)""")
                
    cr.execute("""CREATE TABLE IF NOT EXISTS tenants(
                tenant_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                phone VARCHAR(15) UNIQUE,
                land_id INT,
                rented_area FLOAT,
                monthly_rent FLOAT,
                monthly_interest FLOAT,
                FOREIGN KEY (land_id) REFERENCES lands(land_id) ON DELETE SET NULL)""")
    c.commit()
    return c

def add_owner(c):
    cr = c.cursor()
    nm = input("Enter Owner Name: ")
    if nm.strip() == "":
        print("Error: Name empty.")
        return
        
    ph = input("Enter Phone (10 digits): ")
    if not ph.isdigit() or len(ph) != 10:
        print("Error: Invalid phone.")
        return
        
    cr.execute("SELECT owner_id FROM owners WHERE phone=%s", (ph,))
    if cr.fetchone():
        print("Error: Phone exists.")
        return
        
    ad = input("Enter Address: ")
    cr.execute("INSERT INTO owners (name, phone, address) VALUES(%s, %s, %s)", (nm, ph, ad))
    c.commit()
    print("Owner added successfully!")

def view_owners(c):
    cr = c.cursor()
    cr.execute("SELECT * FROM owners")
    res = cr.fetchall()
    if not res:
        print("No owners.")
    else:
        print(f"\n{'-'*65}\n{'ID':<5} {'Name':<20} {'Phone':<15} {'Address'}\n{'-'*65}")
        for r in res: print(f"{r[0]:<5} {r[1]:<20} {r[2]:<15} {r[3]}")
        print("-" * 65)

def add_land(c):
    cr = c.cursor()
    o_id = input("Enter Owner ID: ")
    if not o_id.isdigit():
        print("Error: Invalid ID.")
        return
        
    cr.execute("SELECT owner_id FROM owners WHERE owner_id=%s", (o_id,))
    if not cr.fetchone():
        print("Error: Owner not found.")
        return
        
    loc = input("Enter Location: ")
    try:
        t_area = float(input("Total Area: "))
        min_a = float(input("Min Area: "))
        max_a = float(input("Max Area: "))
        r_amt = float(input("Rent Amount (50000-1000000): "))
        
        if min_a > max_a or max_a > t_area:
            print("Error: Area constraints failed.")
            return
            
        if r_amt < 50000 or r_amt > 1000000:
            print("Error: Rent out of range.")
            return
            
        sql = "INSERT INTO lands (owner_id, location, total_area, min_area, max_area, rent_amount) VALUES(%s, %s, %s, %s, %s, %s)"
        cr.execute(sql, (o_id, loc, t_area, min_a, max_a, r_amt))
        c.commit()
        print("Land added successfully!")
    except ValueError:
        print("Error: Enter valid numbers.")

def view_lands(c):
    cr = c.cursor()
    cr.execute("""SELECT l.land_id, o.name, l.location, l.total_area, l.rent_amount, l.status 
                  FROM lands l LEFT JOIN owners o ON l.owner_id = o.owner_id""")
    res = cr.fetchall()
    if len(res) == 0: 
        print("No lands.")
    else:
        print(f"\n{'-'*75}\n{'ID':<5} {'Owner':<15} {'Location':<15} {'Area':<10} {'Rent':<10} {'Status'}\n{'-'*75}")
        for r in res:
            own = r[1]
            if own == None:
                own = "None"
            print(f"{r[0]:<5} {own:<15} {r[2]:<15} {r[3]:<10.1f} {r[4]:<10.1f} {r[5]}")
        print("-" * 75)

def reg_tenant(c):
    cr = c.cursor()
    nm = input("Enter Tenant Name: ")
    if nm.strip() == "":
        print("Error: Name empty.")
        return
        
    ph = input("Enter Phone (10 digits): ")
    if not ph.isdigit() or len(ph) != 10:
        print("Error: Invalid phone.")
        return
        
    cr.execute("SELECT tenant_id FROM tenants WHERE phone=%s", (ph,))
    if cr.fetchone():
        print("Error: Phone exists.")
        return
        
    cr.execute("INSERT INTO tenants (name, phone) VALUES(%s, %s)", (nm, ph))
    c.commit()
    print("Tenant registered successfully!")

def rent_land(c):
    cr = c.cursor()
    t_id = input("Enter Tenant ID: ")
    if not t_id.isdigit():
        print("Error: Invalid Tenant ID.")
        return
        
    cr.execute("SELECT land_id FROM tenants WHERE tenant_id=%s", (t_id,))
    t_res = cr.fetchone()
    if not t_res:
        print("Error: Tenant not found.")
        return
        
    if t_res[0] is not None:
        print("Error: Tenant already rented a land.")
        return
        
    l_id = input("Enter Land ID: ")
    if not l_id.isdigit():
        print("Error: Invalid Land ID.")
        return
        
    cr.execute("SELECT total_area, min_area, max_area, rent_amount, status FROM lands WHERE land_id=%s", (l_id,))
    l_res = cr.fetchone()
    if not l_res:
        print("Error: Land not found.")
        return
        
    if l_res[4] != 'Available':
        print("Error: Land is already rented.")
        return
        
    try:
        r_area = float(input("Enter Area to Rent: "))
        if r_area <= 0 or r_area < l_res[1] or r_area > l_res[2]:
            print(f"Error: Area must be between {l_res[1]} and {l_res[2]}.")
            return
            
        m_rent = l_res[3] * (r_area / l_res[0])
        m_int = m_rent * 0.075
        
        cr.execute("UPDATE tenants SET land_id=%s, rented_area=%s, monthly_rent=%s, monthly_interest=%s WHERE tenant_id=%s", (l_id, r_area, m_rent, m_int, t_id))
        cr.execute("UPDATE lands SET status='Rented' WHERE land_id=%s", (l_id,))
        c.commit()
        print(f"Land Rented! Monthly Rent: {m_rent:.2f}, Interest: {m_int:.2f}")
    except ValueError:
        print("Error: Enter valid number.")

def view_rentals(c):
    cr = c.cursor()
    cr.execute("""SELECT t.name, l.location, t.rented_area, t.monthly_rent, t.monthly_interest 
                  FROM tenants t JOIN lands l ON t.land_id = l.land_id""")
    res = cr.fetchall()
    if len(res) == 0: 
        print("No rentals.")
    else:
        print(f"\n{'-'*75}\n{'Tenant':<15} {'Location':<15} {'Area':<10} {'Rent':<10} {'Interest'}\n{'-'*75}")
        for r in res: 
            print(f"{r[0]:<15} {r[1]:<15} {r[2]:<10.1f} {r[3]:<10.1f} {r[4]:<10.1f}")
        print("-" * 75)

def reports(c):
    cr = c.cursor()
    print("\n--- Rental Reports ---")
    
    cr.execute("SELECT COUNT(*) FROM lands WHERE status='Available'")
    av_lands = cr.fetchone()[0]
    
    cr.execute("SELECT COUNT(*) FROM lands WHERE status='Rented'")
    rt_lands = cr.fetchone()[0]
    
    cr.execute("SELECT SUM(monthly_interest) FROM tenants")
    tot_int = cr.fetchone()[0]
    if tot_int is None:
        tot_int = 0.0
        
    print("Total Available Lands:", av_lands)
    print("Total Rented Lands:", rt_lands)
    print("Total Monthly Interest: Rs", round(tot_int, 2))

def main():
    c = None
    try:
        c = connect_db()
        while True:
            print("\nLAND RENTAL SYSTEM")
            print("1. Add Owner")
            print("2. View Owners")
            print("3. Add Land")
            print("4. View Lands")
            print("5. Register Tenant")
            print("6. Rent Land")
            print("7. View Rentals")
            print("8. Reports")
            print("9. Exit")
            ch = input("Enter choice: ")

            if ch == '1':
                add_owner(c)
            elif ch == '2':
                view_owners(c)
            elif ch == '3':
                add_land(c)
            elif ch == '4':
                view_lands(c)
            elif ch == '5':
                reg_tenant(c)
            elif ch == '6':
                rent_land(c)
            elif ch == '7':
                view_rentals(c)
            elif ch == '8':
                reports(c)
            elif ch == '9':
                print("Goodbye!")
                break
            else:
                print("Invalid choice.")
    except mysql.connector.Error as err:
        print("MySQL Error:", err)
    finally:
        if c and c.is_connected():
            c.close()

if __name__ == "__main__":
    main()
