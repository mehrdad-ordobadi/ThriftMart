import requests
from screen import Screen
from menu import Menu
import time
from requests.exceptions import ConnectionError as RequestsConnectionError


class Program:
    """Super class for containing and running different options in the interface.
    it start ups a menu object and a screen object upon creation
    """
    def __init__(self):
        self.menu = Menu()
        self.screen = Screen()
        self.prompt = ''

    def quit(self):
        self.screen.clear_screen()
        self.screen.print_message('Have a good day!')
        time.sleep(2)
        exit()

    def start(self):
        """Method that display the menu for the program, then takes user's choice and runs the option
        corresponding to the choice
        """
        try:
            response = requests.head('http://localhost:5001/')
        except RequestsConnectionError:
            self.screen.print_error('Flask app is not running, please run the app first!')
            exit()
        self.screen.clear_screen()
        while True:
            self.screen.print_message(self.prompt)
            self.screen.print_menu(self.menu)
            if not self.menu.run(self.screen.get_input()):
                break

    def check_id(self, id):
        """Method that checks whether order id is a non-negative int number 
        and returns false if its not

        Args:
            id (str): user entered price

        Returns:
            boolean: True if valid quantity otherwise false
        """
        try:
            id = int(id)
        except ValueError:
            self.screen.print_error('Id has to be a non-negative, int number!')
            return False
        if id < 0:
            self.screen.print_error('Id has to be a non-negative, int number!')
            return False
        return True
    
    def check_price(self, price):
        """Method that checks whether price is a non-negative float number and returns false if its not

        Args:
            price (str): user entered price

        Returns:
            boolean: True if valid price otherwise false
        """
        try:
            price = float(price)
        except ValueError:
            self.screen.print_error('Price has to be a non-negative, float number!')
            return False
        if price < 0:
            self.screen.print_error('Price has to be a non-negative, float number!')
            return False
        return True
    
    def check_quantity(self, quantity):
        """Method that checks whether quantity is a non-negative int number 
        and returns false if its not

        Args:
            quantity (str): user entered price

        Returns:
            boolean: True if valid quantity otherwise false
        """
        try:
            quantity = int(quantity)
        except ValueError:
            self.screen.print_error('Quantity has to be a non-negative, int number!')
            return False
        if quantity < 0:
            self.screen.print_error('Quantity has to be a non-negative, int number!')
            return False
        return True
    

class MainProgram(Program):
    """A class that handles main page of the interface, it inherits from Program class.
    """
    def __init__(self):
        """Constructor for the MainProgram, in addition to inheritence, it also adds the options
        for the main page. And stores the main page prompt
        """
        super().__init__()
        self.menu.add_options('1', 'Manage products', self.manage_products)
        self.menu.add_options('2', 'Manage orders', self.manage_orders)
        self.menu.add_options('3', 'Quit', self.quit)
        self.prompt = 'Welcome to Thrift Mart!\nPlease choose from the following options by entering the key number, followed by Return key: \n'

    def manage_products(self):
        """Option 1 which creates a ManageProductsProgram and starts it.
        """
        self.screen.clear_screen()
        manage_products = ManageProductsProgram()
        manage_products.start()
        
    def manage_orders(self):
        """Option 1 which creates a ManageProductsOrder and starts it.
        """
        self.screen.clear_screen()
        manage_orders = ManageOrdersProgram()
        manage_orders.start()


class ManageProductsProgram(Program):
    """A class that let's user manage the products in the store
    """
    def __init__(self):
        """Constructor which adds the options for the class and stores its 
        prompt message
        """
        super().__init__()
        self.menu.add_options('1', 'View all products', self.view_all_products)
        self.menu.add_options('2', 'View out-of-stock products', self.view_out_of_stock)
        self.menu.add_options('3', 'Update a product', self.update_product)
        self.menu.add_options('4', 'Add a product', self.add_product)
        self.menu.add_options('5', 'Delete a product', self.delete_product)
        self.menu.add_options('6', 'Return to Main Menu', None)
        self.menu.add_options('7', 'Quit', self.quit)
        self.prompt = 'Please choose from the following options to manage the products:'

    def view_all_products(self):
        """Method that lets user view all the products in the store
        """
        self.screen.clear_screen()
        q = False
        while not q:
            self.screen.print_message('Products carried in store are:\n')
            response = requests.get('http://localhost:5001/view-all-products')
            if response.status_code == 200:
                self.screen.print_message('Products in store are: ')
                self.screen.print_products(response.json())
            elif response.status_code == 404:
                self.screen.print_message('We dont carry anything yet!')
            self.screen.print_message('Enter [y/Y] to return to Products\'s menu:')
            q = (self.screen.get_input().lower() == 'y')

    def view_out_of_stock(self):
        """Method that lets the user view all the products that are out of stock in the store
        """
        self.screen.clear_screen()
        q = False
        while not q:
            response = requests.get('http://localhost:5001/api/product/not-in-stock')
            if response.status_code == 200:
                self.screen.print_message('Out of stocks products in store are:')
                self.screen.print_products(response.json(), quant=False)
            elif response.status_code == 404:
                self.screen.print_message('All products are in stock now!')
            self.screen.print_message('Enter [y/Y] to return to Products\'s menu:')
            q = (self.screen.get_input().lower() == 'y')

    def update_product(self):
        """Method that lets the user update existing product's price or quantity
        """
        self.screen.clear_screen()
        q = False
        while not q:
            name = self.screen.get_input('Please enter the name of product you would like to update:')
            price = self.screen.get_input('Enter the new price (enter the cents as well).\nPress \'Return\' without any values if you wish to keep the current price:')
            if price == '':
                price = None
            elif not self.check_price(price):
                continue
            else:
                price = float(price)
            quantity = self.screen.get_input('Enter the new quantity.\nPress \'Return\' without any values if you wish to keep the current quantity:')
            if quantity == '':
                quantity = None
            elif not self.check_quantity(quantity):
                continue
            else:
                quantity = int(quantity)
            response = requests.put(f'http://localhost:5001/api/product/{name}', json={'price': price, 'quantity': quantity})
            if response.status_code == 200:
                success_msg = f'Product: {name} was updated:'
                if price:
                    success_msg += f'new price: {price}.'
                if quantity:
                    success_msg += f'new quantity {quantity}.'
                self.screen.print_success(success_msg)
            elif response.status_code == 404:
                self.screen.print_error(f'Product: {name} was not found!')
            self.screen.print_message('Would you like to update another product?\nEnter [y/Y] if yes, otherwise enter any keys:')
            q = not (self.screen.get_input().lower() == 'y')
            
    def add_product(self):
        """Method that lets the user create new products with by providing name, price and quantity
        """
        self.screen.clear_screen()
        q = False
        while not q:
            name = self.screen.get_input('Please enter the name of product you would like to add:')
            price = self.screen.get_input('Enter the price (enter the cents as well):')
            if not self.check_price(price):
                continue    # check if price not valid ask for new product
            else:
                price = float(price)
            quantity = self.screen.get_input('Enter the quantity:')
            if not self.check_quantity(quantity):
                continue    # check if quantity not valid ask for new product
            else:
                quantity = int(quantity)
            response = requests.post('http://localhost:5001/api/product', json={'name': name, 'price': price, 'quantity': quantity})
            if response.status_code == 200:
                self.screen.print_success(f'Product: {name} with price: {price} and quantity: {quantity} was added!')
            else:
                self.screen.print_error(f'{response.content}, {response.status_code}')
            self.screen.print_message('Would you like to add another product?\nEnter [y/Y] if yes, otherwise enter any keys:')
            q = not (self.screen.get_input().lower() == 'y')

    def delete_product(self):
        """Method that allows user delete a product from the database using product name
        """
        self.screen.clear_screen()
        q = False
        while not q:
            name = self.screen.get_input('Please enter the name of product you would like to delete:')
            confirm = self.screen.get_input(f'Are you sure you would like delete product: {name}?\nEnter [y/Y] to confirm, else enter any value:')
            if confirm.lower() == 'y':
                response = requests.delete(f'http://localhost:5001/api/product/{name}')
                if response.status_code == 200:
                    self.screen.print_success(f'Product: {name} was successfully deleted!')
                elif response.status_code == 404:
                    self.screen.print_error(f'Product: {name} does not exist in the database!')
                elif response.status_code == 400:
                    self.screen.print_error(f'Cannot delete {name}, since it has been ordered by customers!')
            self.screen.print_message('Would you like to delete another product?\nEnter [y/Y] if yes, otherwise enter any keys:')
            q = not (self.screen.get_input().lower() == 'y')

    def start(self):
        """Method that starts the ManageProduct object by printing it's menu 
        asking for a choice, and then running the choice
        """
        while True:
            self.screen.clear_screen()
            self.screen.print_message(self.prompt)
            self.screen.print_menu(self.menu)
            choice = input()
            if not self.menu.run(choice) or choice == '6':
                self.screen.clear_screen()
                break


class ManageOrdersProgram(Program):
    """A class that allows user manage orders in the store, inherits from Program class.
    """
    def __init__(self):
        """Constructor for ManageOrderProgram class, adds its option and 
        stores its prompt message.
        """
        super().__init__()
        self.menu.add_options('1', 'View an order', self.view_order)
        self.menu.add_options('2', 'Search for a customer\'s order', self.view_customer_order)
        self.menu.add_options('3', 'View all pending orders', self.view_pending_orders)
        self.menu.add_options('4', 'View all processesd orders', self.view_processed_orders)
        self.menu.add_options('5', 'Delete an order', self.delete_order)
        self.menu.add_options('6', 'Process an order', self.process_order)
        self.menu.add_options('7', 'Create an order', self.create_order)
        self.menu.add_options('8', 'Update an order', self.update_order)
        self.menu.add_options('9', 'Return to Main Menu', None)
        self.menu.add_options('10', 'Quit', self.quit)
        self.prompt = 'Please choose from the following options to manage the orders'

    def view_order(self):
        """Method that allows user to view an order by providing the order id
        """
        self.screen.clear_screen()
        q = False
        while not q:
            id = self.screen.get_input('Please enter the order id of the order you would like to see:')
            if not self.check_id(id):
                continue
            id = int(id)
            response = requests.get(f'http://localhost:5001/api/order/{id}')
            if response.status_code == 200:
                self.screen.print_message(f'Order with id: {id}:')
                self.screen.print_order([response.json()])
            elif response.status_code == 404:
                self.screen.print_error(f'Order with id: {id} does not exist!')
            self.screen.print_message('Would you life to view another order?\nEnter [y/Y] if yes, otherwise enter any other keys:')
            q = not (self.screen.get_input().lower() == 'y')

    def view_customer_order(self):
        """Method that allows user view orders belonging to a customer by 
        customer name by doing partial name search
        """
        self.screen.clear_screen()
        q = False
        while not q:
            partial_name = self.screen.get_input('Please enter name or partial name of the customer you would like to see orders of:')
            response = requests.get(f'http://localhost:5001/api/order/user/{partial_name}')
            if response.status_code == 200:
                self.screen.print_message(f'Orders that partial match customer anme with {partial_name} are:')
                self.screen.print_order(response.json())
            if response.status_code == 404:
                self.screen.print_error(f'No order was matched with partial name: {partial_name}')
            self.screen.print_message('Would you like to view another customer\'s order?\nEnter [y/Y] if yes, otherwise enter any keys:')
            q = not (self.screen.get_input().lower() == 'y')
    
    def view_pending_orders(self):
        """Method that allows user view all the pending (no completed) orders in 
        the database.
        """
        self.screen.clear_screen()
        q = False
        while not q:
            response = requests.get('http://localhost:5001/api/order/pending')
            if response.status_code == 200:
                self.screen.print_message('Pending orders in store are:')
                self.screen.print_order(response.json())
            elif response.status_code == 404:
                self.screen.print_error('There are no pending orders in the store!')
            self.screen.print_message('Enter [y/Y] once you are done with reviewing pending orders:')
            q = (self.screen.get_input().lower() == 'y')

    def view_processed_orders(self):
        """Method that allows user to view processed orders in the database
        """
        self.screen.clear_screen()
        q = False
        while not q:
            response = requests.get('http://localhost:5001/api/order/processed')
            if response.status_code == 200:
                self.screen.print_message('Processed orders in the store are: ')
                self.screen.print_order(response.json())
            elif response.status_code == 404:
                self.screen.print_error('There are no processed orders in the store!')
            self.screen.print_message('Enter [y/Y] once you are done with reviewing processed orders:')
            q = (self.screen.get_input().lower() == 'y')

    def delete_order(self):
        """Method that allows user to remove an order from teh database by 
        providing its order id
        """
        self.screen.clear_screen()
        q = False
        while not q:
            id = self.screen.get_input('Please enter the order id of the order you would like to remove: ')
            if not self.check_id(id):
                continue
            id = int(id)
            self.screen.print_message(f'Please confirm that you would like to delete order with id: {id}\nEnter [y/Y] to confirm, otherwise enter any other key:')
            if self.screen.get_input().lower() != 'y':
                self.screen.print_message('Would you like to delete another order?\nIf yes enter [y/Y], otherwise enter any key:')
                q = not (self.screen.get_input().lower() == 'y')
                continue    # if not confirmed ask for another id else got back to order menu
            response = requests.delete(f'http://localhost:5001/api/order/delete/{id}')
            if response.status_code == 200:
                self.screen.print_success(f'Order with id: {id} was removed!')
            elif response.status_code == 404:
                self.screen.print_error(f'Order with id: {id} was not found!')
            else:
                self.screen.print_error(f'{response.text}, {response.status_code}')
            self.screen.print_message('Would you like to delete another order?\nIf yes enter [y/Y], otherwise enter any key:')
            q = not (input().lower() == 'y')

    def process_order(self):
        """Method that allows the user to process and order by providing its id
        """
        self.screen.clear_screen()
        q = False
        while not q:
            id = self.screen.get_input('Please enter the order_id for the order you would like process:')
            if not self.check_id(id):
                continue
            id = int(id)
            process = {'process': True}
            response = requests.put(f'http://localhost:5001/api/order/process/{id}', json=process)
            if response.status_code == 200:
                self.screen.print_success(f'Order with id: {id} was processed successfully!')
            elif response.status_code == 404:
                self.screen.print_error(f'Order with id: {id} does not exist!')
            self.screen.print_message('Would you like to process another order?\nEnter [y\Y] if yes, otherwise enter any key:')
            q = not (self.screen.get_input().lower() == 'y')
            
    def create_order(self):
        """Method that allows that user to create a new order by providing 
        customer name, customer address and products and their quantities
        """
        self.screen.clear_screen()
        q = False
        while not q:
            customer_name = self.screen.get_input('Please enter the customer\'s name:')
            customer_address = self.screen.get_input('Please enter the customer\'s adrress:')
            done = False
            prod_list = []
            while not done:     # get the products
                prod_name = self.screen.get_input('Please enter the name of the product:')
                prod_quant = self.screen.get_input(f'Please enter the quantity of {prod_name}:')
                if not self.check_quantity(prod_quant):
                    continue
                conf = self.screen.get_input(f'Is product: {prod_name}, qunatity: {prod_quant} correct\nEnter [y/Y] to confirm, and other key to redo:')
                if conf.lower() == 'y':
                    prod_list.append(dict(name=prod_name, quantity=int(prod_quant)))
                else:
                    continue
                self.screen.print_message('Would you like to add another product to this order?\nEnter [y/Y] to add more products, otherwise enter any key:')
                done = not (self.screen.get_input().lower() == 'y')
            self.screen.print_message('You have entered the following order:')
            self.screen.print_order([dict(customer_name=customer_name, customer_address=customer_address, products=prod_list)], display=False)
            self.screen.print_message('Would you like to submit this order?\nEnter [y/Y] to submit, any other keys to discard:')
            if not (self.screen.get_input().lower() == 'y'):
                self.screen.print_message('Would you like to make another order?, if yes enter [y/Y], else enter any other value: ')
                if self.screen.get_input().lower() != 'y':
                    break
            response = requests.post('http://localhost:5001/api/order', json={'customer_name': customer_name, 'customer_address': customer_address, 'products': prod_list})
            if response.status_code == 200:
                id = response.json()['order_id']
                self.screen.print_success(f'Your order with id: {id} was successfully submitted!')
            elif response.status_code == 404:
                self.screen.print_error(response.content.decode())
            elif response.status_code == 400:  # User can not order quantities larger than in-stock quantities
                self.screen.print_error(response.content.decode())
            self.screen.print_message('Would you like to create another order?\nEnter [y/Y] if yes, otherwise enter any key;')
            q = not (self.screen.get_input().lower() == 'y')
    
    def update_order(self):
        """Method that allows user to update the products in an order by 
        providing its id. User can add products, update quantity of products, 
        or remove products from the order (by setting its quantity to 0).
        """
        self.screen.clear_screen()
        q = False
        while not q:
            ord_id = self.screen.get_input('Please enter the id of the order you would like to update:')
            if not self.check_id(ord_id):
                continue
            ord_id = int(ord_id)
            response = requests.get(f'http://localhost:5001/api/order/{ord_id}')
            if response.status_code == 200:
                self.screen.print_message(f'Order with id {ord_id} is:')
                self.screen.print_order([response.json()], display=False)   # display order to user
            if response.status_code == 404:
                self.screen.print_error(f'Order with id {ord_id} does not exists!')
                # self.screen.print_message('Would you like to update another order?\nEnter [y/Y] if yes, otherwise enter any other keys:')
                confirm = self.screen.get_input('Would you like to update another order?\nEnter [y/Y] if yes, otherwise enter any other keys:')
                if confirm.lower() == 'y':
                    continue
                else:
                    break
            done = False
            prod_list = []
            while not done:     # get the list of products to update
                self.screen.print_message('You can update a product, add a product, or remove a product from the order by entering 0 for quantity!')
                prod_name = self.screen.get_input('Please enter the name of product you would like to update/add/delete:')
                prod_quant = self.screen.get_input(f'Please enter the new quantity for {prod_name}:')
                if not self.check_quantity(prod_quant):
                    continue
                prod_quant = int(prod_quant)
                confirm = self.screen.get_input(f'Is {prod_name} with quantity {prod_quant} correct?\nEnter [y/Y] if yes, otherwise enter any key:')
                if confirm.lower() == 'y':
                    prod_list.append(dict(name=prod_name, quantity=prod_quant))
                    self.screen.print_message('Would you like to update another product?\nEnter [y/Y] if yes, other enter any key')
                    done = not (self.screen.get_input().lower() == 'y')
                else:
                    continue
            response = requests.put(f'http://localhost:5001/api/order/{ord_id}', json={'products': prod_list})
            if response.status_code == 200:
                self.screen.print_success(f'Order with id: {ord_id} was successfully updated')
            elif response.status_code == 404:   # product(s) not in the database
                self.screen.print_error(response.content.decode())
            elif response.status_code == 400:   # User can not order quantities larger than in-stock quantities
                self.screen.print_error(response.content.decode())
            self.screen.print_message('Would you like to update another order?\nEnter [y/Y], else enter any other value: ')
            q = not (self.screen.get_input().lower() == 'y')      
    
    def start(self):
        """Method that starts the ManageOrderProgram object by printing its 
        menu asking for a choice, and then running the choice
        """
        while True:
            self.screen.clear_screen()
            self.screen.print_message(self.prompt)
            self.screen.print_menu(self.menu)
            choice = self.screen.get_input()
            if not self.menu.run(choice) or choice == '9':
                self.screen.clear_screen()
                break
        

if __name__ == "__main__":
    main_program = MainProgram()
    main_program.start()    # start the program with the main menu here