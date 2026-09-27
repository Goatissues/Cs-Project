import mysql.connector

def connect_to_database():
    db_link = mysql.connector.connect(host="localhost", user="root", password="Ayushman@001")
    db_cursor = db_link.cursor()
    db_cursor.execute("CREATE DATABASE IF NOT EXISTS car_rental_db")
    db_cursor.execute("USE car_rental_db")
    
    db_cursor.execute("""CREATE TABLE IF NOT EXISTS customers(
                customer_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(15) UNIQUE NOT NULL,
                license_no VARCHAR(50) UNIQUE NOT NULL)""")
                
    db_cursor.execute("""CREATE TABLE IF NOT EXISTS cars(
                car_id INT AUTO_INCREMENT PRIMARY KEY,
                brand VARCHAR(50) NOT NULL,
                model VARCHAR(50) NOT NULL,
                car_number VARCHAR(20) UNIQUE NOT NULL,
                rent_per_day FLOAT NOT NULL,
                status VARCHAR(20) DEFAULT 'Available')""")
                
    db_cursor.execute("""CREATE TABLE IF NOT EXISTS rentals(
                rental_id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT,
                car_id INT,
                days INT,
                total_amount FLOAT,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
                FOREIGN KEY (car_id) REFERENCES cars(car_id) ON DELETE CASCADE)""")
    db_link.commit()
    return db_link

def register_customer(db_link):
    db_cursor = db_link.cursor()
    cust_name = input("Enter Customer Name: ")
    cust_phone = input("Enter Phone (10 digits): ")
    if cust_name == "":
        print("Name cannot be empty.")
        return
    if cust_phone.isdigit() == False or len(cust_phone) != 10:
        print("Invalid phone number. Must be 10 digits.")
        return
    db_cursor.execute("SELECT customer_id FROM customers WHERE phone=%s", (cust_phone,))
    if db_cursor.fetchone() != None:
        print("This phone number is already registered.")
        return
    license_num = input("Enter License Number: ")
    if license_num == "":
        print("License cannot be empty.")
        return
    db_cursor.execute("SELECT customer_id FROM customers WHERE license_no=%s", (license_num,))
    if db_cursor.fetchone() != None:
        print("This license number is already registered.")
        return
    db_cursor.execute("INSERT INTO customers (name, phone, license_no) VALUES(%s, %s, %s)", (cust_name, cust_phone, license_num))
    db_link.commit()
    print("Customer added successfully!")

def show_customers(db_link):
    db_cursor = db_link.cursor()
    db_cursor.execute("SELECT * FROM customers")
    table_data = db_cursor.fetchall()
    if len(table_data) == 0: 
        print("No customers found in database.")
    else:
        print("\n---------------------------------------------------------")
        print("ID \t Name \t\t Phone \t\t License")
        print("---------------------------------------------------------")
        for record in table_data:
            print(record[0], "\t", record[1], "\t\t", record[2], "\t", record[3])
        print("---------------------------------------------------------")

def insert_car(db_link):
    db_cursor = db_link.cursor()
    car_brand = input("Enter Brand: ")
    car_model = input("Enter Model: ")
    car_plate = input("Enter Car Number: ")
    db_cursor.execute("SELECT car_id FROM cars WHERE car_number=%s", (car_plate,))
    if db_cursor.fetchone() != None:
        print("Car number already exists in database.")
        return
    try:
        daily_rent = float(input("Enter Rent Per Day: "))
        if daily_rent <= 0:
            print("Rent must be greater than zero.")
            return
        db_cursor.execute("INSERT INTO cars (brand, model, car_number, rent_per_day) VALUES(%s, %s, %s, %s)", (car_brand, car_model, car_plate, daily_rent))
        db_link.commit()
        print("Car added successfully!")
    except ValueError:
        print("Please enter a valid number for rent.")

def show_cars(db_link):
    db_cursor = db_link.cursor()
    db_cursor.execute("SELECT * FROM cars")
    table_data = db_cursor.fetchall()
    if len(table_data) == 0: 
        print("No cars found in database.")
    else:
        print("\n-------------------------------------------------------------------------")
        print("ID \t Brand \t\t Model \t\t Car No. \t Rent/Day \t Status")
        print("-------------------------------------------------------------------------")
        for record in table_data:
            print(record[0], "\t", record[1], "\t", record[2], "\t", record[3], "\t", record[4], "\t\t", record[5])
        print("-------------------------------------------------------------------------")

def book_car(db_link):
    db_cursor = db_link.cursor()
    cust_id = input("Enter Customer ID: ")
    if cust_id.isdigit() == False: 
        print("Invalid Customer ID.")
        return
        
    db_cursor.execute("SELECT customer_id FROM customers WHERE customer_id=%s", (cust_id,))
    if db_cursor.fetchone() == None: 
        print("Customer not found.")
        return
    
    car_id = input("Enter Car ID: ")
    if car_id.isdigit() == False: 
        print("Invalid Car ID.")
        return
        
    db_cursor.execute("SELECT rent_per_day, status FROM cars WHERE car_id=%s", (car_id,))
    car_data = db_cursor.fetchone()
    if car_data == None: 
        print("Car not found.")
        return
        
    if car_data[1] != 'Available': 
        print("Car is currently rented.")
        return
    
    try:
        total_days = int(input("Enter Number of Days: "))
        if total_days <= 0: 
            print("Days must be greater than zero.")
            return
            
        final_amount = car_data[0] * total_days
        db_cursor.execute("INSERT INTO rentals (customer_id, car_id, days, total_amount) VALUES(%s, %s, %s, %s)", (cust_id, car_id, total_days, final_amount))
        db_cursor.execute("UPDATE cars SET status='Rented' WHERE car_id=%s", (car_id,))
        db_link.commit()
        print("Car booked successfully! Total Amount to pay: Rs", final_amount)
    except ValueError:
        print("Please enter a valid number of days.")

def show_rentals(db_link):
    db_cursor = db_link.cursor()
    db_cursor.execute("""SELECT r.rental_id, cu.name, ca.brand, ca.model, r.days, r.total_amount 
                         FROM rentals r JOIN customers cu ON r.customer_id = cu.customer_id 
                         JOIN cars ca ON r.car_id = ca.car_id""")
    table_data = db_cursor.fetchall()
    if len(table_data) == 0: 
        print("No rentals found.")
    else:
        print("\n-----------------------------------------------------------------------")
        print("ID \t Customer \t Car Details \t\t Days \t Total Amount")
        print("-----------------------------------------------------------------------")
        for record in table_data:
            car_info = str(record[2]) + " " + str(record[3])
            print(record[0], "\t", record[1], "\t", car_info, "\t", record[4], "\t Rs", record[5])
        print("-----------------------------------------------------------------------")

def take_back_car(db_link):
    db_cursor = db_link.cursor()
    rent_id = input("Enter Rental ID to return car: ")
    if rent_id.isdigit() == False: 
        print("Invalid Rental ID.")
        return
        
    db_cursor.execute("SELECT car_id FROM rentals WHERE rental_id=%s", (rent_id,))
    rent_data = db_cursor.fetchone()
    if rent_data == None: 
        print("Rental record not found.")
        return
    
    db_cursor.execute("UPDATE cars SET status='Available' WHERE car_id=%s", (rent_data[0],))
    db_cursor.execute("DELETE FROM rentals WHERE rental_id=%s", (rent_id,))
    db_link.commit()
    print("Car returned successfully! Rental record closed.")

def view_reports(db_link):
    db_cursor = db_link.cursor()
    print("\n--- Rental Reports ---")
    db_cursor.execute("SELECT COUNT(*) FROM cars WHERE status='Available'")
    avail_count = db_cursor.fetchone()[0]
    db_cursor.execute("SELECT COUNT(*) FROM cars WHERE status='Rented'")
    rented_count = db_cursor.fetchone()[0]
    db_cursor.execute("SELECT SUM(total_amount) FROM rentals")
    total_money = db_cursor.fetchone()[0]
    if total_money == None: total_money = 0.0
    
    print("Total Available Cars:", avail_count)
    print("Total Rented Cars:", rented_count)
    print("Total Rental Revenue: Rs", round(total_money, 2))

def main():
    db_link = None
    try:
        db_link = connect_to_database()
        while True:
            print("\nCAR RENTAL SYSTEM")
            print("1. Add Customer")
            print("2. View Customers")
            print("3. Add Car")
            print("4. View Cars")
            print("5. Rent Car")
            print("6. View Rentals")
            print("7. Return Car")
            print("8. Reports")
            print("9. Exit")
            user_input = input("Enter choice: ")

            if user_input == '1':
                register_customer(db_link)
            elif user_input == '2':
                show_customers(db_link)
            elif user_input == '3':
                insert_car(db_link)
            elif user_input == '4':
                show_cars(db_link)
            elif user_input == '5':
                book_car(db_link)
            elif user_input == '6':
                show_rentals(db_link)
            elif user_input == '7':
                take_back_car(db_link)
            elif user_input == '8':
                view_reports(db_link)
            elif user_input == '9':
                print("Exiting system. Goodbye!")
                break
            else:
                print("Invalid choice. Try again.")
    except mysql.connector.Error as db_err:
        print("Database Error:", db_err)
    finally:
        if db_link != None and db_link.is_connected() == True:
            db_link.close()

if __name__ == "__main__":
    main()
