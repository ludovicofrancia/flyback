from utils import api_yes_no, disable_ssl_verification, display_menu, handle_basic_search, handle_weekdays_search

def main():
  print("\n--- --- Welcome to Flyback! --- --- \n")
  disable_ssl_verification()

  # Main program loop
  while True:
      choice= display_menu()
      if choice == "1":
          amadeus_client= api_yes_no()
          handle_basic_search(amadeus_client)
      elif choice == "2":
          amadeus_client= api_yes_no()
          handle_weekdays_search(amadeus_client)
      elif choice == "3":
          print("\n Thank you for using FlyBack! \n")
          break
      
if __name__ == "__main__":
    main()