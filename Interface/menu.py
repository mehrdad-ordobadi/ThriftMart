class Menu:
    """Class to handle menus for programs in the interface
    """
    def __init__(self):
        self.options = {}
    
    def add_options(self, key, description, funct):
        """Simple method to obtain and store options for the menu

        Args:
            key (str): option key, used to call the option in the menu
            description (str): description of the menu
            funct (function): the function that is called when option is chosen
        """
        self.options[key] = [description, funct]

    def run(self, choice):
        """Method that runs the option corresponding to the choice made by user

        Args:
            choice (str): key in menu options passed by user

        Raises:
            KeyError: raised when user enters invalid choice
        """
        if choice not in self.options.keys():
            raise KeyError('Invalid choice!')
        if self.options[choice][1] is not None:
            self.options[choice][1]()
        else:
            return False
        return True