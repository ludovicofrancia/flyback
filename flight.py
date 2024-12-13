from datetime import datetime, timedelta
import random
from abc import ABC, abstractmethod
from amadeus import Client
from config import airline_codes, iata_codes

# Class to represent basic information associated with a flight
class Flight():
    """
    Attributes:
    - where_from (str): IATA code of the departure airport.
    - where_to (str): IATA code of the arrival airport.
    - departure_time (str): Departure time in the following format: e.g. '2024-12-10T18:00:00'.
    - arrival_time (str): Arrival time in the following format: e.g. '2024-12-10T21:15:00'.
    - airline (str): Name or code of the airline.
    - price (float): Price of the flight.
    - currency (str): Currency of the price (e.g. 'EUR').
    - duration (str): Duration of the flight in the following formati: e.g. 'PT3H30M'.
    """
    def __init__(self, where_from, where_to, departure_time, arrival_time, airline, price, currency, duration):
        #Validate attributes
        assert isinstance(where_from, str) and len(where_from) == 3, "IATA code for departure airport must be three characters long."
        assert isinstance(where_to, str) and len(where_to) == 3, "IATA code for return airport must be three characters long."
        try:
            datetime.fromisoformat(departure_time)
            datetime.fromisoformat(arrival_time)
        except ValueError as e:
            raise ValueError(f"Datetime is not in the format e.g.'2024-12-10T21:15:00': {e}")
        assert isinstance(airline, str), "airline must be a string."
        assert float(price) > 0, "price must be a positive number in string format."
        assert isinstance(currency, str), "currency must be a string."
        assert isinstance(duration, str) and duration[0:2]== "PT", "duration must be in the format e.g. 'PT3H30M'."

        self.where_from= where_from
        self.where_to= where_to
        self.departure_time= departure_time
        self.arrival_time= arrival_time
        self.airline= airline
        self.price= price
        self.currency= currency
        self.duration= duration

# Class that handles flights searches using the Amadeus API or by generating dummy data
class FlightSearch(ABC):
    """
    Attributes:
    - amadeus_client (Client): An instance of the Amadeus client to make API requests (it's equal to None if we use dummy data).
    """
    def __init__(self, amadeus_client= None):
       assert isinstance(amadeus_client, Client) or amadeus_client==None, "amadeus_client must be an instance of Client or equal to None."
       self.amadeus_client= amadeus_client

    @abstractmethod
    def execute_search(self):
        """Perform a specific type of flight search."""
        pass

    @abstractmethod
    def print_results(self):
        """Prints the results of the performed flight search."""
        pass

    def search_flights_api(self, where_from, where_to, date, passengers= 1):
        """
        This method searches for flights using the Amadeus API.

        Args:
        - where_from (str): IATA code of the departure airport.
        - where_to (str): IATA code of the arrival airport.
        - date (str): Departure date in 'YYYY-MM-DD' format: e.g. '2024-12-10'.
        - passengers (int): Number of passengers, default is 1.

        Returns:
        - flights (list[Flight]): List of Flight objects sorted by increasing price.
        """
        assert isinstance(where_from, str) and len(where_from) == 3, "IATA code for departure airport must be three characters long."
        assert isinstance(where_to, str) and len(where_to) == 3, "IATA code for return airport must be three characters long."
        assert isinstance(date, str) and len(date) == 10, "departure date must be in the format 'YYYY-MM-DD'."
        assert isinstance(passengers, int) and passengers >0, "passengers must be a positive integer."

        try:
            # Request to the Amadeus API to obtain flight deals with the required features
            response = self.amadeus_client.shopping.flight_offers_search.get(
                originLocationCode= where_from,
                destinationLocationCode= where_to,
                departureDate= date,
                adults= passengers
            )
            assert isinstance(response.data, list), "Amadeus API response must be a list."


            # Initializing the list of flights
            flights= []

            # Analyze the response obtained from the API and extract data regarding flights
            for offer in response.data:
                try:
                    itineraries = offer.get('itineraries', [])
                except KeyError as e:
                    print(f"'itineraries' is missing in API response: {e}")

                for itinerary in itineraries:
                    segments = itinerary.get('segments', [])
                    if len(segments) == 1 and segments[0].get('numberOfStops') == 0:
                        segment = segments[0]

                        flights.append(Flight(where_from= segment['departure']['iataCode'],
                                               where_to= segment['arrival']['iataCode'],
                                               departure_time= segment['departure']['at'],
                                               arrival_time= segment['arrival']['at'],
                                               airline= airline_codes.get(offer['validatingAirlineCodes'][0], offer['validatingAirlineCodes'][0]),
                                               price= float(offer['price']['total']),
                                               currency= offer['price']['currency'],
                                               duration= itinerary['duration']))

            return self.sort_flights_by_price(flights) # Return of flight deals sorted by increasing price
        except:
            print("Failed to use Amadeus API...Generating random fake data...")
            flights= self.generate_mock_flights(where_from, where_to, date)
            return flights

    def generate_mock_flights(self, where_from, where_to, date):
        """
        This method generates a list of dummy flights data to simulate results.

        Args:
        - where_from (str): IATA code of the departure airport.
        - where_to (str): IATA code of the arrival airport.
        - date (str): Departure date in 'YYYY-MM-DD' format: e.g. '2024-12-10'.

        Returns:
        - flights (list): List of Flight objects (randombly generated) sorted by increasing price.
        """
        assert isinstance(where_from, str) and len(where_from) == 3, "IATA code for departure airport must be three characters long."
        assert isinstance(where_to, str) and len(where_to) == 3, "IATA code for return airport must be three characters long."
        assert isinstance(date, str) and len(date) == 10, "departure date must be in the format 'YYYY-MM-DD'."

        # Initializing the list of flights and generating a random number of flights
        flights= []
        num_flights = random.randint(0, 5)

        #Generation of random data regarding dummy flights
        for i in range(num_flights):
            departure_datetime= datetime.strptime(date, "%Y-%m-%d") + timedelta(minutes= random.randint(0, 1440))
            duration_hours = random.randint(1, 8)
            duration_minutes = random.randint(0, 59)

            flights.append(Flight(where_from= where_from,
                                  where_to= where_to,
                                  departure_time= departure_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
                                  arrival_time= (departure_datetime + timedelta(hours=duration_hours, minutes=duration_minutes)).strftime("%Y-%m-%dT%H:%M:%S"),
                                  airline= random.choice(list(airline_codes.values())),
                                  price= round(random.uniform(100, 600), 2),
                                  currency= 'EUR',
                                  duration= f"PT{duration_hours}H{duration_minutes}M"))
        return self.sort_flights_by_price(flights) # Return of flight deals sorted by increasing price

    def sort_flights_by_price(self, flights):
        """
        This method sorts a list of Flight objects by their price attribute using the insertion sort algorithm.

        Args:
        - flights (list): List of Flight objects.

        Returns:
        - flights (list): List of Flight objects sorted by increasing price.
        """
        assert all(isinstance(flight, Flight) for flight in flights), "All elements of flights must be instances of Flight."

        for i in range(1, len(flights)):
            flight_to_order = flights[i]
            previous_index = i-1
            while previous_index >=0 and flights[previous_index].price > flight_to_order.price:
                flights[previous_index+1] = flights[previous_index]
                previous_index -=1
            flights[previous_index+1] = flight_to_order
        return flights

    def print_flights_info(self, flights, iata_codes):
        """
        This method prints the information about the flights found, which comply with the search filters entered, in a readable format.

        Args:
        - flights (list): List of Flight objects sorted by increasing price.
        - iata_codes (dict): Dictionary with IATA codes and city names.
        """
        assert all(isinstance(flight, Flight) for flight in flights), "All elements of flights must be instances of Flight."

        if len(flights)== 0:
            print("No options matching your filters")
        else:
            n= 1
            for flight in flights:
                print(f"{n}) From: {flight.where_from} ({iata_codes.get(flight.where_from, flight.where_from)}) - "
                    f"To: {flight.where_to} ({iata_codes.get(flight.where_to, flight.where_to)})\n"
                    f"  - Airline: {flight.airline}\n"
                    f"  - Departure Time: {flight.departure_time.split('T')[1]} - {flight.departure_time.split('T')[0]}\n"
                    f"  - Arrival Time: {flight.arrival_time.split('T')[1]} - {flight.arrival_time.split('T')[0]}\n"
                    f"  - Duration: {flight.duration[2:]} \n"
                    f"  - Price: {flight.price} {flight.currency} \n"
                    )
                n +=1
        return

# Class representing a basic flight search with options for round-trip flights and additional filters such as departure and arrival times.
# BasicSearch Class allows us to perform searches that answer questions such as
# 'Search for 2-passenger direct flights from CPH airport to BER airport, departing on 2025-01-24 with minimum departure time 11:15 and returning on 2025-01-30 with maximum arrival time 18:00.'
class BasicSearch(FlightSearch):
    """
    Attributes:
    - where_from (str): IATA code of the departure airport.
    - where_to (str): IATA code of the arrival airport.
    - departure_date (str): Departure date in 'YYYY-MM-DD' format: e.g. '2024-12-10'.
    - passengers (int): Number of passengers.
    - return_date (str, optional): Return date in 'YYYY-MM-DD' format: e.g. '2024-12-25'.
    - departure_min_departure_time (str, optional): Minimum departure time in 'HH:MM' format: e.g. '16:23'.
    - return_max_arrival_time (str, optional): Maximum arrival time in 'HH:MM' format: e.g. '22:15'.
    - amadeus_client (Client, optional): An instance of the Amadeus client to make API requests (it's equal to None if we use dummy data).
    """

    def __init__(self, where_from, where_to, departure_date, passengers, return_date= None, departure_min_departure_time= None, return_max_arrival_time= None, amadeus_client= None):
        assert isinstance(where_from, str) and len(where_from) == 3, "IATA code for departure airport must be three characters long."
        assert isinstance(where_to, str) and len(where_to) == 3, "IATA code for return airport must be three characters long."
        assert isinstance(departure_date, str) and len(departure_date) == 10, "departure date must be in the format 'YYYY-MM-DD'."
        assert isinstance(passengers, int) and passengers >0, "passengers must be a positive integer."
        assert return_date== None or (isinstance(departure_date, str) and len(departure_date) == 10), "departure date must be in the format 'YYYY-MM-DD'."
        assert departure_min_departure_time== None or (isinstance(departure_min_departure_time, str) and len(departure_min_departure_time) == 5), "departure_min_departure_time must be in the format 'HH:MM' or equal to None."
        assert return_max_arrival_time== None or (isinstance(return_max_arrival_time, str) and len(return_max_arrival_time) == 5), "return_max_arrival_time must be in the format 'HH:MM' or equal to None."
        assert isinstance(amadeus_client, Client) or amadeus_client==None, "amadeus_client must be an instance of Client or equal to None."

        super().__init__(amadeus_client)

        self.where_from= where_from
        self.where_to= where_to

        self.departure_date= departure_date
        self.departure_min_departure_time= departure_min_departure_time
        self.return_date= return_date
        self.return_max_arrival_time= return_max_arrival_time

        self.passengers= passengers

        self.results= self.execute_search()

    def execute_search(self):
        """
        This method searches for outbound flights and, if applicable, return flights.
        If specified it also applies filters on departure and arrival times.
        """

        # Search for outbound flights
        departure_time_info= f"(minimum departing time: {self.departure_min_departure_time}) " if self.departure_min_departure_time else ""
        print(f"\n--- ---\nSearching flights from {self.where_from} to {self.where_to} {departure_time_info}on {self.departure_date} for {self.passengers} passenger(s)...")

        departing_flights= []
        returning_flights= []

        try:
            if self.amadeus_client != None:
              departing_flights= super().search_flights_api(self.where_from, self.where_to, self.departure_date, self.passengers)
            else:
              departing_flights= super().generate_mock_flights(self.where_from, self.where_to, self.departure_date)
        except Exception as e:
            print(f"Error searching flights with Amadeus API: {e}")


        # Filter outbound flights by minimum departure time if specified.
        if self.departure_min_departure_time:
            departing_flights = self.sort_flights_by_price([flight for flight in departing_flights
                                    if datetime.fromisoformat(departing_flights[departing_flights.index(flight)].departure_time).time() >= datetime.strptime(self.departure_min_departure_time, "%H:%M").time()])
        print(f"Available departing flights: {len(departing_flights)} \n---")

        # Search for return flights if a return date is specified
        if self.return_date:
            returning_time_info= f"(maximum arrival time: {self.return_max_arrival_time}) " if self.return_max_arrival_time else ""
            print(f"\n---\nSearching return flights from {self.where_to} to {self.where_from} {returning_time_info}on {self.return_date}...")

            try:
                if self.amadeus_client != None:
                  returning_flights= super().search_flights_api(self.where_to, self.where_from, self.return_date, self.passengers)
                else:
                  returning_flights= super().generate_mock_flights(self.where_to, self.where_from, self.return_date)
            except Exception as e:
                print(f"Error searching flights with Amadeus API: {e}")

            # Filter return flights by maximum arrival time if specified.
            if self.return_max_arrival_time:
                returning_flights = self.sort_flights_by_price([flight for flight in returning_flights
                                        if datetime.fromisoformat(returning_flights[returning_flights.index(flight)].arrival_time).time() <= datetime.strptime(self.return_max_arrival_time, "%H:%M").time()])
            print(f"Available returning flights: {len(returning_flights)} \n---\n")

        print("Search completed! \n--- ---")
        return {"departing_flights": departing_flights, "returning_flights": returning_flights}

    def print_results(self):
        """
        This method prints the information about the flights found, which comply with the search filters entered, in a readable format.
        """
        print("\n ----------------------------------------")
        print("Available Departing Flights:")
        super().print_flights_info(self.results["departing_flights"], iata_codes)
        if self.return_date:
            print("Available Returning Flights:")
            super().print_flights_info(self.results["returning_flights"], iata_codes)
        print("---------------------------------------- \n")

# Class representing a flight search by specific days of the week for departures and returns within a user-specified date range.
# WeekDays Class allows us to perform searches that answer questions such as
# 'Search for direct flights for the CPH-FCO route during the period 2025-01-01 - 2025-02-28 for 3 passengers departing on a Friday and returning on the following Sunday.'
class WeekDaysSearch(FlightSearch):
    """
    Attributes:
    - where_from (str): IATA code of the departure airport.
    - where_to (str): IATA code of the arrival airport.
    - passengers (int): Number of passengers.
    - departure_weekday (str): Day of the week for departure: e.g. 'Monday'.
    - return_weekday (str): Day of the week for return: e.g. 'Wednesday'.
    - departure_min_date (str): Minimum departure date in the format “YYYY-MM-DD”: e.g. '2024-12-01'.
    - return_max_date (str): Maximum return date in the format “YYYY-MM-DD”: e.g. '2025-02-01'.
    - amadeus_client (Client, optional): An instance of the Amadeus client to make API requests (it's equal to None if we use dummy data).
    - weekday_pairs (list[tuple]): Pairs (departure_date, return_date) corresponding to the days requested.
    - results (list[dict]): List of the cheapest round-trip flights sorted by increasing price.
    """
    def __init__(self, where_from, where_to, passengers, departure_weekday, return_weekday, departure_min_date, return_max_date, amadeus_client= None):
        assert isinstance(where_from, str) and len(where_from) == 3, "IATA code for departure airport must be three characters long."
        assert isinstance(where_to, str) and len(where_to) == 3, "IATA code for return airport must be three characters long."
        assert isinstance(passengers, int) and passengers >0, "passengers must be a positive integer."
        assert isinstance(departure_weekday, str) and len(departure_weekday) <= 9 , "departure_weekday must be a day of the week e.g. 'Monday'."
        assert isinstance(return_weekday, str) and len(return_weekday) <= 9 , "return_weekday must be a day of the week e.g. 'Monday'."
        assert isinstance(departure_min_date, str) and len(departure_min_date) == 10, "departure_min_date must be in the format 'YYYY-MM-DD'."
        assert isinstance(return_max_date, str) and len(return_max_date) == 10, "return_max_date must be in the format 'YYYY-MM-DD'."
        assert isinstance(amadeus_client, Client) or amadeus_client == None, "amadeus_client must be an instance of Client or equal to None."

        super().__init__(amadeus_client)
        self.where_from= where_from
        self.where_to= where_to
        self.passengers= passengers
        self.departure_weekday= departure_weekday.upper()
        self.return_weekday= return_weekday.upper()
        self.departure_min_date= departure_min_date
        self.return_max_date= return_max_date

        self.weekday_pairs= self.find_weekday_pairs(self.departure_weekday, self.return_weekday, self.departure_min_date, self.return_max_date)
        self.results= self.execute_search(self.weekday_pairs)

    def find_weekday_pairs(self, departure_weekday= "WEDNESDAY", return_weekday= "TUESDAY", departure_min_date= "2024-12-09", return_max_date= "2024-12-24"):
        """
        This method finds date pairs corresponding to the specified days of the week for departure and return.

        Args:
        - departure_weekday (str): Day of the week for departure: e.g. 'MONDAY'.
        - return_weekday (str): Day of the week for return: e.g. 'WEDNESDAY'.
        - departure_min_date (str): Minimum departure date in the format “YYYY-MM-DD”: e.g. '2024-12-01'.
        - return_max_date (str): Maximum return date in the format “YYYY-MM-DD”: e.g. '2025-02-01'.

        Returns:
        - weekday_pairs (list[tuple]): List of of tuples (departure_date, return_date).
        """
        assert isinstance(departure_weekday, str) and len(departure_weekday) <= 9 , "departure_weekday must be a day of the week e.g. 'Monday'."
        assert isinstance(return_weekday, str) and len(return_weekday) <= 9 , "return_weekday must be a day of the week e.g. 'Monday'."
        assert isinstance(departure_min_date, str) and len(departure_min_date) == 10, "departure_min_date must be in the format 'YYYY-MM-DD'."
        assert isinstance(return_max_date, str) and len(return_max_date) == 10, "return_max_date must be in the format 'YYYY-MM-DD'."

        print("Looking for all possible combinations of dates compatible with the filters entered...")
        weekday_pairs= []

        weekdays_mapping= {"MONDAY": 0, "TUESDAY": 1, "WEDNESDAY": 2, "THURSDAY": 3, "FRIDAY": 4, "SATURDAY": 5, "SUNDAY": 6}
        departure_min_date_datetime= datetime.strptime(departure_min_date, "%Y-%m-%d")
        return_max_date_datetime= datetime.strptime(return_max_date, "%Y-%m-%d")

        current_date= departure_min_date_datetime
        while current_date <= return_max_date_datetime:
            if current_date.weekday() == weekdays_mapping[departure_weekday]:
                # calculate the return date based on the difference between days of the week
                days_to_return= (weekdays_mapping[return_weekday]-weekdays_mapping[departure_weekday]) %7
                return_date= current_date + timedelta(days= days_to_return)
                if return_date <= return_max_date_datetime:
                    weekday_pairs.append((current_date.strftime("%Y-%m-%d"), return_date.strftime("%Y-%m-%d")))
            current_date += timedelta(days=1)

        print(f"Combinations of dates that match the filters entered: {len(weekday_pairs)}")
        return weekday_pairs

    def execute_search(self, weekday_pairs):
        """
        This method finds the cheapest round-trip flights for each date pair, if any, sorting them by their total price (outbound price + return price).

        Args:
        - weekday_pairs (list[tuple]): List of of tuples (departure_date, return_date).

        Returns:
        - results (list[dict]): List of the cheapest round-trip flights for each date pair, if any, sorted by increasing total price.
        """
        assert isinstance(weekday_pairs, list), "weekday_pairs must be a list."
        assert all(isinstance(pair, tuple) and len(pair) == 2 for pair in weekday_pairs), "Each element of the list weekday_pairs must be a tuple of two elements (departure_date, return_date)."

        print("Searching for cheap flights for the dates found...")
        results= []

        for departure_date, return_date in weekday_pairs:
            try:
                if self.amadeus_client != None:
                    departure_flights= super().search_flights_api(self.where_from, self.where_to, departure_date, self.passengers)
                    return_flights= super().search_flights_api(self.where_to, self.where_from, return_date, self.passengers)
                else:
                    departure_flights= super().generate_mock_flights(self.where_from, self.where_to, departure_date)
                    return_flights= super().generate_mock_flights(self.where_to, self.where_from, return_date)
            except Exception as e:
                print(f"Error searching flights: {e}")

            if len(departure_flights) != 0 and len(return_flights) != 0:
                # Find the cheapest flights, if they exist, for each date pair
                cheapest_departure_flight= departure_flights[0]
                cheapest_return_flight= return_flights[0]
                total_price= float(cheapest_departure_flight.price) + float(cheapest_return_flight.price)

                results.append({"cheapest_departure_flight": cheapest_departure_flight,
                                "cheapest_return_flight": cheapest_return_flight,
                                "total_price": round(total_price, 2)})

        # Sort the results by increasing total price by using the insertion sort algorithm
        for i in range(1, len(results)):
            weekday_pairs_flights_to_order = results[i]
            previous_index = i-1
            while previous_index >=0 and results[previous_index]["total_price"] > weekday_pairs_flights_to_order["total_price"]:
                results[previous_index+1] = results[previous_index]
                previous_index -=1
            results[previous_index+1] = weekday_pairs_flights_to_order
        return results

    def print_results(self):
        """
        This method prints the information about the flights found, which comply with the search filters entered, in a readable format.
        """
        print("\n ----------------------------------------")
        if len(self.results) == 0:
            print("No options matching your filters")
            return
        else:
            print("You are looking for a round trip with the following characteristics: \n"
                  f"- Range: {self.departure_min_date} - {self.return_max_date} \n"
                  f"- Passenger/s: {self.passengers} \n"
                  f"- Departure day: {self.departure_weekday} \n"
                  f"- Returning day: {self.return_weekday} \n")

            print("Cheapest Option: \n"
                  f"- Departure Flight: {self.departure_weekday} {self.results[0]['cheapest_departure_flight'].departure_time.split('T')[0]} {self.results[0]['cheapest_departure_flight'].departure_time.split('T')[1]} (€{self.results[0]['cheapest_departure_flight'].price}) \n"
                  f"- Return Flight: {self.return_weekday} {self.results[0]['cheapest_return_flight'].arrival_time.split('T')[0]} {self.results[0]['cheapest_return_flight'].arrival_time.split('T')[1]} (€{self.results[0]['cheapest_return_flight'].price}) \n"
                  f"- Total Price: €{self.results[0]['total_price']} \n"
                 )

            if len(self.results) > 1:
                print("Other Options: ")
                for i in range(1, len(self.results)):
                    print(f"{i}) {self.departure_weekday} {self.results[i]['cheapest_departure_flight'].departure_time.split('T')[0]} {self.results[i]['cheapest_departure_flight'].departure_time.split('T')[1]} "+
                          f"- {self.return_weekday} {self.results[i]['cheapest_return_flight'].departure_time.split('T')[0]} {self.results[i]['cheapest_return_flight'].departure_time.split('T')[1]} "+
                          f"(Total Price: €{self.results[i]['total_price']})")
        print("---------------------------------------- \n")
        return
