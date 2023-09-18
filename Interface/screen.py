import os
from colorama import Fore, Style, init
from tabulate import tabulate


class Screen:
    """A class that allows user to handle screen messages.
    """
    def __init__(self):
        init()

    def clear_screen(self):
        """Method that clears the screen
        """
        if os.name == 'nt':  # check os here
            os.system('cls')
        else:
            os.system('clear')

    def print_line(self):
        """Method that prints a line |====| with length as wide as the 
        terminal size
        """
        terminal_size = os.get_terminal_size().columns
        line = '|' + (terminal_size - 2) * '=' + '|'
        print(line)
        print()

    def get_input(self, msg=''):
        print(Fore.CYAN + Style.BRIGHT + msg + Style.RESET_ALL + '\n')
        arg = input()
        print()
        return arg

    def print_message(self, message):
        """Method that receives a message in string format and prints it in 
        blue on the screen

        Args:
            message (str): message
        """
        print(Fore.BLUE + Style.BRIGHT + message + Style.RESET_ALL + '\n')
        print()

    def print_error(self, error):
        """Method that receives an error message in string format and prints 
        it in red on the screen

        Args:
            error (str): error message
        """
        print(Fore.RED + Style.BRIGHT + error + Style.RESET_ALL + '\n')
        print()

    def print_menu(self, menu):
        """Method that prints a menu to the screen in yellow

        Args:
            menu (Menu): A Menu object
        """
        options = menu.options
        for key, opt in options.items():
            print(Fore.YELLOW + Style.BRIGHT + str(key) + '. ' + opt[0] + Style.RESET_ALL + '\n')
            # print(key, opt[0])
            print()

    def print_success(self, message):
        """Method that prints a success message to the screen in green

        Args:
            message (str): A success message
        """
        print(Fore.GREEN + Style.BRIGHT + message + Style.RESET_ALL + '\n')
        # print(message)
        print()
    
    def print_products(self, products_list, quant=True):
        """Method that receives a list of products dictionaries and prints 
        them into the screen, includes the quantities if quant value is True

        Args:
            products_list (list): list of product dictionaries
            quant (bool, optional): if true method prints the quantities as well
        """
        if not quant:
            for prod in products_list:
                prod.pop('quantity')
        print(tabulate(products_list, headers='keys'))
        print()

    def print_order(self, order_list, display=True):
        """Method that receives an order dictionary, rearranges the items in it
        then prints it into the screen, if display is true, prints more 
        information about the order, including, order_id, completed, order_date
        process_date and price

        Args:
            order_list (dict): an order
            display (bool, optional): if True method prints more information
        """
        for order in order_list:
            self.print_line()
            order_rearranged = {}
            if display:
                order_rearranged['order_id'] = order['order_id']
            order_rearranged['customer_name'] = order['customer_name']
            order_rearranged['customer_address'] = order['customer_address']
            if display:
                order_rearranged['completed'] = order['completed']
                order_rearranged['order_date'] = order['order_date']
                if order['process_date']:
                    order_rearranged['process_date'] = order['process_date']
            if display:
                order_rearranged['price'] = order['price']
            print(tabulate(order_rearranged.items(), headers=[]))
            print()
            print('Products:')
            print()
            print(tabulate(order['products'], headers='keys'))
        print()
        self.print_line()  
