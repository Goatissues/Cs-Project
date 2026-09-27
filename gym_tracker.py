import mysql.connector

con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Cbse@2026"
)

cur = con.cursor()

cur.execute("CREATE DATABASE IF NOT EXISTS gym_management")
cur.execute("USE gym_management")

cur.execute("""
    CREATE TABLE IF NOT EXISTS trainers (
        trainer_id INT AUTO_INCREMENT PRIMARY KEY,
        trainer_name VARCHAR(50) NOT NULL,
        specialization VARCHAR(50)
    )
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS members (
        member_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        age INT,
        phone VARCHAR(15) UNIQUE,
        trainer_id INT
    )
""")


def read_text(message, maximum):
    while True:
        text = input(message).strip()

        if text != "" and len(text) <= maximum:
            return text

        print("Enter between 1 and", maximum, "characters.")


def read_phone():
    while True:
        phone = input("Enter phone number: ").strip()

        if phone.isdigit() and len(phone) == 10:
            return phone

        print("Phone number must contain exactly 10 digits.")


def add_member():
    name = read_text("Enter name: ", 50)

    age = input("Enter age (10-100): ").strip()

    if not age.isdigit():
        print("Age must be a number.")
        return

    age = int(age)

    if age < 10 or age > 100:
        print("Age must be between 10 and 100.")
        return

    phone = read_phone()

    cur.execute(
        "SELECT member_id FROM members WHERE phone = %s",
        (phone,)
    )

    if cur.fetchone() is not None:
        print("Phone number is already registered.")
        return

    trainer_id = input("Enter trainer ID (optional): ").strip()

    if trainer_id == "":
        trainer_id = None
    else:
        if not trainer_id.isdigit():
            print("Trainer ID must be a number.")
            return

        cur.execute(
            "SELECT trainer_id FROM trainers WHERE trainer_id = %s",
            (trainer_id,)
        )

        if cur.fetchone() is None:
            print("Trainer not found.")
            return

    cur.execute("""
        INSERT INTO members (name, age, phone, trainer_id)
        VALUES (%s, %s, %s, %s)
    """, (name, age, phone, trainer_id))

    con.commit()
    print("Member added! Member ID:", cur.lastrowid)


def display_member(row):
    print("\n--------------------")
    print("Member ID:", row[0])
    print("Name:", row[1])
    print("Age:", row[2])
    print("Phone:", row[3])

    if row[4] is None:
        print("Trainer: Not assigned")
    else:
        print("Trainer ID:", row[4])


def view_members():
    cur.execute("""
        SELECT member_id, name, age, phone, trainer_id
        FROM members
    """)

    rows = cur.fetchall()

    if len(rows) == 0:
        print("No members found.")
    else:
        for row in rows:
            display_member(row)


def search_member():
    member_id = input("Enter member ID: ").strip()

    if not member_id.isdigit():
        print("Enter a numeric ID.")
        return

    cur.execute("""
        SELECT member_id, name, age, phone, trainer_id
        FROM members
        WHERE member_id = %s
    """, (member_id,))

    row = cur.fetchone()

    if row is None:
        print("Member not found.")
    else:
        display_member(row)


def update_member():
    member_id = input("Enter member ID: ").strip()

    if not member_id.isdigit():
        print("Enter a numeric ID.")
        return

    cur.execute(
        "SELECT member_id FROM members WHERE member_id = %s",
        (member_id,)
    )

    if cur.fetchone() is None:
        print("Member not found.")
        return

    phone = read_phone()

    cur.execute("""
        SELECT member_id FROM members
        WHERE phone = %s AND member_id != %s
    """, (phone, member_id))

    if cur.fetchone() is not None:
        print("Another member already uses this phone number.")
        return

    cur.execute(
        "UPDATE members SET phone = %s WHERE member_id = %s",
        (phone, member_id)
    )

    con.commit()
    print("Phone number updated!")


def delete_member():
    member_id = input("Enter member ID: ").strip()

    if not member_id.isdigit():
        print("Enter a numeric ID.")
        return

    confirm = input("Delete this member? (y/n): ").strip().lower()

    if confirm != "y":
        print("Deletion cancelled.")
        return

    cur.execute(
        "DELETE FROM members WHERE member_id = %s",
        (member_id,)
    )

    con.commit()

    if cur.rowcount == 0:
        print("Member not found.")
    else:
        print("Member deleted!")


def add_trainer():
    name = read_text("Enter trainer name: ", 50)
    specialization = read_text("Enter specialization: ", 50)

    cur.execute("""
        INSERT INTO trainers (trainer_name, specialization)
        VALUES (%s, %s)
    """, (name, specialization))

    con.commit()
    print("Trainer added! Trainer ID:", cur.lastrowid)


def view_trainers():
    cur.execute("""
        SELECT trainer_id, trainer_name, specialization
        FROM trainers
    """)

    rows = cur.fetchall()

    if len(rows) == 0:
        print("No trainers found.")
    else:
        for row in rows:
            print("\n--------------------")
            print("Trainer ID:", row[0])
            print("Name:", row[1])
            print("Specialization:", row[2])


def reports():
    cur.execute("SELECT COUNT(*) FROM members")
    print("Total members:", cur.fetchone()[0])

    cur.execute("SELECT COUNT(*) FROM trainers")
    print("Total trainers:", cur.fetchone()[0])

    cur.execute("SELECT AVG(age) FROM members")
    average = cur.fetchone()[0]

    if average is None:
        print("Average age: No age data available")
    else:
        print("Average age:", round(average, 1))


while True:
    print("\n--- Gym Management System ---")
    print("1. Add member")
    print("2. View members")
    print("3. Search member")
    print("4. Update member phone")
    print("5. Delete member")
    print("6. Add trainer")
    print("7. View trainers")
    print("8. Reports")
    print("9. Exit")

    choice = input("Enter your choice: ").strip()

    try:
        if choice == "1":
            add_member()
        elif choice == "2":
            view_members()
        elif choice == "3":
            search_member()
        elif choice == "4":
            update_member()
        elif choice == "5":
            delete_member()
        elif choice == "6":
            add_trainer()
        elif choice == "7":
            view_trainers()
        elif choice == "8":
            reports()
        elif choice == "9":
            break
        else:
            print("Invalid choice.")

    except mysql.connector.Error as error:
        con.rollback()
        print("Database error:", error)

cur.close()
con.close()

print("Goodbye!")