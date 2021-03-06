# pylint: disable=invalid-name
# pylint: disable=pointless-string-statement
# pylint: disable=too-few-public-methods

import pickle
from os import rename, remove, listdir


PERSONNEL_INFO_CSV = 'Personnel Info.csv'
PERSONNEL_INFO_TXT = 'Personnel Info.txt'
AdminUsername = 'Admin'
AllPossibleCommands = """
Commands                                  What it does                      Syntax Example

-h        or        --help                Display All Commands              python3 Personnel.py -h
-a        or        --add                 Add new personnel type            python3 Personnel.py -a <new name> <new pin>
-u        or        --update              Update a personnel type's pin     python3 Personnel.py -u <name> <new pin>
-r        or        --remove              Remove a personnel type's pin     python3 Personnel.py -r <name>
-l        or        --list                List all users                    python3 Personnel.py -l
"""


"""
This is the module for the Personnel class, and is designed to
document which personnel in the sandbox are authorizing
disabling of printers at the sandbox
"""


class Personnel(object):
    """
    Class for the personnel at the sandbox, and can be used to
    authorize access to the printer usage
    """
    def __init__(self, name, pin):
        """
        Args:
            name: str
                The name of the Personnel, saved for security reasons

            pin: str
                The password pin of the indiviual. This is hashed using
                a md5 algorithm and it's hash is what is used to check
        """
        self.name = name
        self.pin = Personnel._getHash(pin)
        self._save()

    def __str__(self):
        """
        magic function to convert the Personnel Object to a string
        """
        return '{0}, {1}'.format(self.name, self.pin)

    def __repr__(self):
        """
        magic function to represent the Personnel Object
        """
        return '{0}, {1}'.format(self.name, self.pin)

    def __eq__(self, pin: str):
        """
        Function to check if the pin matches the pin of this object
        """
        if not isinstance(pin, str):
            raise TypeError("Expected str, got", type(pin))

        else:
            return self.pin == self._getHash(pin)

    @staticmethod
    def _getHash(pin):
        import hashlib
        """
        Function used to return hash generated by the pin
        This is a static method as it is is independant of all
        other properties of the class

        Args:
            pin :str
                The pin that the user has given
        """
        pin = pin.encode('utf-8')
        hashVal = hashlib.md5(pin).hexdigest()

        return hashVal

    @staticmethod
    def isPinPresent(pin, personnel_list_file=PERSONNEL_INFO_TXT):
        """
        Function to check if the pin is present in the hash of the pins
        """
        hashed_pin = Personnel._getHash(pin)
        with open(personnel_list_file, 'rb') as file_object:
            return Personnel.__CheckIfPinMatchesInFile(file_object, hashed_pin)

    @staticmethod
    def isUsernameAndPinPresent(username, pin, personnel_list_file=PERSONNEL_INFO_TXT):
        """
        Function to check if the username and password exist in the file
        """
        hashed_pin = Personnel._getHash(pin)
        with open(personnel_list_file, 'rb') as file_object:
            return Personnel.__CheckIfUsernameAndPinMatchesInFile(file_object, username, hashed_pin)

    @staticmethod
    def __CheckIfUsernameAndPinMatchesInFile(file_object, username, hashed_pin):
        """
        Function to verify if username and password are correct
        """
        while True:
            try:
                user_details = pickle.load(file_object)
                if username == user_details.name:
                    if hashed_pin == user_details.pin:
                        return True
            except EOFError:
                return False

    @staticmethod
    def __CheckIfPinMatchesInFile(file_object, hashed_pin):
        """
        Function to iterate over each object in the file to see if its pin matches or not
        """
        while True:
            try:
                user_details = pickle.load(file_object)
                if hashed_pin == user_details.pin:
                    return True
            except EOFError:
                return False

    @staticmethod
    def addNewPersonnel(name, pin, adminPin):
        """
        Function to add a new personnel. It first checks if the personnel had a
        pin occour before, and asks to change it.
        """
        if adminPin == -1:
            Personnel(name, pin)
        elif not Personnel.isAdminPin(adminPin):
            raise ValueError('Admin Pin Incorrect')
        elif Personnel.isUsernameAndPinPresent(name, pin):
            raise IndexError("Pin has been used before, please enter another pin")
        else:
            Personnel(name, pin)

    @staticmethod
    def isAdminPin(adminPin):
        """
        Function to check if the given pin is the admin's pin or not
            is over ridden when adminPin is kept as -1 (signed int)
        returns Boolean
        """
        if adminPin == -1:
            return True
        return Personnel.isUsernameAndPinPresent(AdminUsername, adminPin)

    @staticmethod
    def updatePersonnel(name, new_pin, adminPin):
        """
        Commandline function to update the personnel files
            Checks if admin pin provided is correct or not
                if incorrect, raises value error
            removes personnel from file based on given pin
            adds personnel back with updated pin
        """
        if not Personnel.isAdminPin(adminPin= adminPin):
            raise ValueError('Admin Pin Incorrect')
        else:
            Personnel.removePersonnel(name=name, adminPin=adminPin)
            Personnel(name, new_pin)

    @staticmethod
    def removePersonnel(name, adminPin, personnel_list_file = PERSONNEL_INFO_TXT):
        """
        Commandline function to remove the personnel files
            Checks if admin pin provided is correct or not
                if incorrect, raises value error
            opens personnel files
            iterates over each object and saves it to a list(ListOfUsers)
                when EOFError ocours, it deletes PERSONNEL_INFO_CSV and
                PERSONNEL_INFO_TXT and runs the _save function for each of the Personnel objects
        """
        if not Personnel.isAdminPin(adminPin):
            raise ValueError('Admin Pin Incorrect')

        else:
            file_object = open(personnel_list_file, 'rb')
            ListOfUsers = []
            while True:
                try:
                    user_details = pickle.load(file=file_object)
                    if user_details.name != name:
                        ListOfUsers.append(user_details)
                except EOFError:
                    file_object.close()
                    remove(PERSONNEL_INFO_CSV)
                    remove(PERSONNEL_INFO_TXT)
                    for user in ListOfUsers:
                        user._save()
                    break

    def _save(self):
        """
        Saving the Personnel information for later usage
        """
        with open(PERSONNEL_INFO_CSV, 'a') as file_object:
            file_object.write(str(self) + '\n')

        with open(PERSONNEL_INFO_TXT, 'ab') as file_object:
            pickle.dump(self, file_object)

    @staticmethod
    def resetPersonnelFiles():
        """
        function to erase all personnel information as if it's the first time
        This feature is only for debugging
        """
        try:
            remove(PERSONNEL_INFO_TXT)
            remove(PERSONNEL_INFO_CSV)
        except FileNotFoundError:
            pass

    @staticmethod
    def addAdmin():
        """
        Function to add the Admin the first time the sets up the machine
        """
        # try:
        name = AdminUsername
        pin = input('Enter the new Admin pin: ')
        Personnel.addNewPersonnel(name, pin, -1)
        # except IndexError:
        #     pass

    @staticmethod
    def listAllUsers():
        """
        Commandline function to display all the personnel associated with the account
        Source: PERSONNEL_INFO_CSV file
        """
        with open(PERSONNEL_INFO_CSV) as UserFileObject:
            ListOfUsers = UserFileObject.readlines()
            ListOfUsers = [x.split(',')[0] for x in ListOfUsers]
            for user in ListOfUsers:
                print(user)


if __name__ == '__main__':
    from sys import argv
    if not (PERSONNEL_INFO_CSV in listdir() and PERSONNEL_INFO_TXT in listdir()):
        createNewFileNow = input('File Not Found, would you like to create the file now? (y/n) ')
        if createNewFileNow.lower() == 'y':
            Personnel.addAdmin()
            print('Added; going to quit now')
        else:
            print("Aborting")
            exit()

    elif '-h' in argv or '--help' in argv:
        print('The following commands are possible:')
        print(AllPossibleCommands)

    elif '-a' in argv or '--add' in argv:
        new_user = argv[argv.index('-a' if '-a' in argv else '--add' in argv)+1]
        new_pin = argv[argv.index(new_user)+1]
        print('Please confirm:')
        print('Personnel: {}'.format(new_user))
        print('Pin: {}'.format(new_pin))
        confirm = input("y/N")

        if confirm.lower() == 'y':
            expectedAdminPin = input("Please enter admin pin: ")
            Personnel.addNewPersonnel(name=new_user, pin=new_pin, adminPin=expectedAdminPin)
            print('User Added')
        else:
            #exit program
            print("Aborting")
            exit()

    elif '-u' in argv or '--update' in argv:
        user = argv[argv.index('-u' if '-u' in argv else '--update' in argv)+1]
        new_pin = argv[argv.index(user)+1]
        print('Please confirm:')
        print('Personnel: {}'.format(user))
        print('Pin: {}'.format(new_pin))
        confirm = input("y/N")

        if confirm.lower() == 'y':
            expectedAdminPin = input("Please enter admin pin: ")
            Personnel.updatePersonnel(user, new_pin, expectedAdminPin)
            print('Personnel Updated')
        else:
            print("Aborting")
            exit()

    elif '-r' in argv or '--remove' in argv:
        user = argv[argv.index('-r' if '-r' in argv else '--remove' in argv)+1]
        print('Please confirm:')
        print('Personnel: {}'.format(user))
        confirm = input("y/N")
        if confirm.lower() == 'y':
            expectedAdminPin = input("Please enter admin pin: ")
            Personnel.removePersonnel(name=user, adminPin=expectedAdminPin)
            print('Personnel removed')
        else:
            print("Aborting")
            exit()

    elif '-l' in argv or '--list' in argv:
        Personnel.listAllUsers()

    elif len(argv) != 1:
        print('Command not understood, here is a list of avalible commands')
        print(AllPossibleCommands)
