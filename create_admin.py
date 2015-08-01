from stock_loan import User, db


def create_admin(username, password, email, receive_email):
    """Function to create an admin user"""
    try:
        admin = User(username, password, email, bool(receive_email), True)
        db.session.add(admin)
        db.session.commit()
        print('Admin with username {} successfully created.'.format(username))
        return None
    except:
         print("Something went wrong. No username created.")
         return None


username = input("Admin username: ")
password = input("Admin password: ")
email = input("Admin email: ")
receive_email = input("Receive Email? True/False: ")

create_admin(username, password, email, receive_email)