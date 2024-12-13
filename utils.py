from amadeus import Client
import ssl
import urllib3
import pandas as pd
from datetime import datetime
from flight import BasicSearch, WeekDaysSearch
from config import iata_codes, api_key


# Make the user choose whether or not to use real data
def api_yes_no():
  api= input("--- --- --- \nYou can choose between two options: \n1. Use API to access real data (Note: API calls are limited and can make the program slower.\n2. Use dummy data for faster execution.\n--- --- ---\nEnter your choice: ")

  while api != "1" and api != "2":
      print("--- --- ---")
      api= input("You can choose between two options: \n1. Use API to access real data (Note: API calls are limited and can make the program slower.\n2. Use dummy data for faster execution.\n--- --- ---\nEnter your choice (Type 1 or 2 and press enter): ")

  assert api in ["1", "2"], "api must be '1' or '2'."
  if api == "1":
      try:
          amadeus_client = Client(
              client_id= api_key['client_id'],
              client_secret= api_key['client_secret']
              )
          print("The program will use real data from Amadeus API.")
      except Exception as e:
          print(f'Error initializing Amadeus client: {e}.\nThe program will use dummy data.')
          amadeus_client= None
  elif api == "2":
      print("The program will use dummy data.")
      amadeus_client= None
  return amadeus_client

# Disable SSL verification to avoid problems with insecure certificates (this is safe in test environments)
def disable_ssl_verification():
  ssl._create_default_https_context = ssl._create_unverified_context
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Display a list of cities and their IATA codes in a table with n_col columns
def display_cities_iata_codes(iata_codes= iata_codes, n_col= 5):
    """
    Args:
    - iata_codes (dict): Dictionary with IATA codes as key and city names as value.
    - n_col (int): Number of columns to show in the table.
    """
    assert isinstance(iata_codes, dict), "iata_codes must be a dictionary."
    assert isinstance(n_col, int) and n_col > 0, "n_col must be a positive integer."

    # Sort IATA codes by ordering city names alphabetically
    items= sorted(iata_codes.items(), key= lambda x: x[1])
    # Format each entry as 'city_name iata_code'
    formatted = [f"{x[1]} ({x[0]})   " for x in items]

    # Divide into rows with n_columns
    df = pd.DataFrame([formatted[i:i+n_col] for i in range(0, len(formatted), n_col)])

    print("City Name (IATA Code):")
    print(df.to_string(index=False, header=False))
    return

# Display the main menu for the user
def display_menu():
    print("\n---- ---- ----")
    print("Select an option:")
    print("[1] Basic Search: \ne.g. 'Search for 2-passenger direct flights from CPH airport to BER airport, departing on 2025-01-24 with minimum departure time 11:15 and returning on 2025-01-30 with maximum arrival time 18:00.' \n")
    print("[2] Search by specific days of the week: \ne.g. 'Search for direct flights for the CPH-FCO route during the period 2025-01-01 - 2025-02-28 for 3 passengers departing on a Friday and returning on the following Sunday.' \n")
    print("[3] Exit")
    print("---- ---- ----\n")

    choice= input("Enter your choice: ") # Get the input of the user
    while choice not in ["1", "2", "3"]:
        choice= input("Enter your choice (Input '1', '2' or '3' and then press Enter): ") # Get the input of the user

    return choice

# Asks the user for input, if it is not provided then returns a specified default value
def get_optional_input(prompt, default= None):
    """
    Args:
    - prompt (str): The message to be displayed when requesting input.
    - default : Value to be returned if the user does not provide any input.
    """
    assert isinstance(prompt, str), "prompt must be a string."

    user_input= input(prompt)
    return user_input if user_input != "" else default

# Manage the flow of BasicSearch flight search
def handle_basic_search(amadeus_client):
    """
    Args:
    - iata_codes (dict): Dictionary with IATA codes as key and city names as value.
    """
    print("\n")
    print("-- Basic Search --")
    print("e.g. 'Search for 2-passenger direct flights from CPH airport to BER airport, departing on 2025-01-24 with minimum departure time 11:15 and returning on 2025-01-30 with maximum arrival time 18:00.' \n")
    display_cities_iata_codes(iata_codes= iata_codes)
    print("\n")
    where_from = input("Enter the IATA code of the departure airport: ").upper()
    while not(isinstance(where_from, str) and len(where_from) == 3 and where_from in iata_codes):
        print("\n IATA code of the airport must be three characters long and must be available in the above list  e.g. 'FCO'. \n")
        where_from = input("Enter the IATA code of the departure airport: ").upper()

    where_to = input("Enter the IATA code of the destination airport: ").upper()
    while not(isinstance(where_to, str) and len(where_to) == 3 and where_to in iata_codes):
        print("\n IATA code of the airport must be three characters long and must be available in the above list  e.g. 'FCO'. \n")
        where_to = input("Enter the IATA code of the destination airport: ").upper()

    passengers = input("Enter the number of passengers: ")
    while not(passengers.isdigit() and int(passengers)>0):
        print("\n passengers must be a positive integer. \n")
        passengers = input("Enter the number of passengers: ")
    passengers= int(passengers)

    while True:
        departure_date = input("Enter your departure date (YYYY-MM-DD e.g. 2024-12-23): ")
        try:
            assert datetime.strptime(departure_date, "%Y-%m-%d")
            assert datetime.strptime(departure_date, "%Y-%m-%d")>datetime.now()
            break
        except:
            print("\n departure_date must be in the format 'YYYY-MM-DD' and it must be in the future. \n")

    while True:
        departure_min_departure_time = get_optional_input("Enter DEPARTURE time from (HH:MM e.g. 16:10) [optional]: ", default=None)
        try:
            if departure_min_departure_time == None:
                    break
            assert datetime.strptime(departure_min_departure_time, "%H:%M")
            break
        except:
            print("\n departure_min_departure_time must be in the format 'HH:MM' or equal to None. \n")


    while True:
        return_date = get_optional_input("Enter your return date (YYYY-MM-DD e.g. 2024-12-30) [optional]: ", default=None)
        try:
            if return_date == None:
                break
            assert datetime.strptime(return_date, "%Y-%m-%d")
            assert datetime.strptime(return_date, "%Y-%m-%d")>datetime.strptime(departure_date, "%Y-%m-%d")
            break
        except:
            print("\n return_date must be in the format 'YYYY-MM-DD' and it must be after the departure date. \n")

    while True:
        return_max_arrival_time = get_optional_input("Enter the maximum ARRIVAL time  (HH:MM e.g. 22:00) [optional]: ", default=None)
        try:
            if return_max_arrival_time == None:
                    break
            assert datetime.strptime(return_max_arrival_time, "%H:%M")
            break
        except:
            print("\n return_max_arrival_time must be in the format 'HH:MM' or equal to None. \n")

    # Perform BasicSearch flight search and show results
    search = BasicSearch(where_from, where_to, departure_date, passengers, return_date, departure_min_departure_time, return_max_arrival_time, amadeus_client)
    search.print_results()
    return

# Manage the flow of WeekDaysSearch flight search
def handle_weekdays_search(amadeus_client):
    """
    Args:
    - iata_codes (dict): Dictionary with IATA codes as key and city names as value.
    """
    print("\n")
    print("-- WeekDays Search --")
    print("e.g. 'Search for direct flights for the CPH-FCO route during the period 2025-01-01 - 2025-02-28 for 3 passengers departing on a Friday and returning on the following Sunday.' \n")
    display_cities_iata_codes(iata_codes= iata_codes)
    print("\n")
    where_from = input("Enter the IATA code of the departure airport: ").upper()
    while not(isinstance(where_from, str) and len(where_from) == 3 and where_from in iata_codes):
        print("\n IATA code of the airport must be three characters long and must be available in the above list  e.g. 'FCO'. \n")
        where_from = input("Enter the IATA code of the departure airport: ").upper()

    where_to = input("Enter the IATA code of the destination airport: ").upper()
    while not(isinstance(where_to, str) and len(where_to) == 3 and where_to in iata_codes):
        print("\n IATA code of the airport must be three characters long and must be available in the above list  e.g. 'FCO'. \n")
        where_to = input("Enter the IATA code of the destination airport: ").upper()

    passengers = input("Enter the number of passengers: ")
    while not(passengers.isdigit() and int(passengers)>0):
        print("\n passengers must be a positive integer. \n")
        passengers = input("Enter the number of passengers: ")
    passengers= int(passengers)

    while True:
        departure_weekday = input("Enter your preferred departure day of the week (e.g. Monday): ").upper()
        try:
            assert isinstance(departure_weekday, str)
            assert departure_weekday in ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
            break
        except:
            print("\n It must be a day of the week e.g. 'Monday'. \n")

    while True:
        return_weekday = input("Enter your preferred return day of the week (e.g. Tuesday): ").upper()
        try:
            assert isinstance(return_weekday, str)
            assert return_weekday in ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
            break
        except:
            print("\n It must be a day of the week e.g. 'Monday'. \n")

    while True:
        departure_min_date = input("Enter DEPARTURE date from (YYYY-MM-DD e.g. 2024-12-23): ")
        try:
            assert datetime.strptime(departure_min_date, "%Y-%m-%d")
            assert datetime.strptime(departure_min_date, "%Y-%m-%d")>datetime.now()
            break
        except:
            print("\n Date must be in the format 'YYYY-MM-DD' and it must be in the future. \n")

    while True:
        return_max_date = input("Enter maximum RETURN date on (YYYY-MM-DD e.g. 2024-12-23): ")
        try:
            assert datetime.strptime(return_max_date, "%Y-%m-%d")
            assert datetime.strptime(return_max_date, "%Y-%m-%d")>datetime.strptime(departure_min_date, "%Y-%m-%d")
            break
        except:
            print("\n Date must be in the format 'YYYY-MM-DD' and it must be after the minimum departure date. \n")

    # Perform WeekDaysSearch flight search and show results
    search = WeekDaysSearch(where_from, where_to, passengers, departure_weekday, return_weekday, departure_min_date, return_max_date, amadeus_client)
    search.print_results()
    return