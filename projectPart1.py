import sys
import cx_Oracle # the package used for accessing Oracle in Python
import getpass # the package for getting password from user without displaying it


def create_available_view(connection):

    #crazy shit creating the available flights view table if it does not exist, if it already exist, drop it then create.
    curs = connection.cursor()
    curs.execute("SELECT view_name from user_views")
    rows = curs.fetchall()
    for row in rows:
        print(row[0])
        if row[0] == "AVAILABLE_FLIGHTS" :
            curs.execute("DROP view available_flights")
    curs.execute("create view available_flights(flightno,dep_date, src,dst,dep_time,arr_time,fare,seats,price) as select f.flightno, sf.dep_date, f.src, f.dst, f.dep_time+(trunc(sf.dep_date)-trunc(f.dep_time)), f.dep_time+(trunc(sf.dep_date)-trunc(f.dep_time))+(f.est_dur/60+a2.tzone-a1.tzone)/24, fa.fare, fa.limit-count(tno), fa.price from flights f, flight_fares fa, sch_flights sf, bookings b, airports a1, airports a2 where f.flightno=sf.flightno and f.flightno=fa.flightno and f.src=a1.acode and f.dst=a2.acode and fa.flightno=b.flightno(+) and fa.fare=b.fare(+) and sf.dep_date=b.dep_date(+) group by f.flightno, sf.dep_date, f.src, f.dst, f.dep_time, f.est_dur,a2.tzone, a1.tzone, fa.fare, fa.limit, fa.price having fa.limit-count(tno) > 0 ")
    curs.close()

def loginMenu():
    #INITIAL SCREEN FOR SCREENING NEW OR OLD USERS.
    loginMenu = True
    oldUser = False
    newUser = False
    loginOptions = {}
    loginOptions['1'] = "Already Registered"
    loginOptions['2'] = "Not Already Registered"
    
    while loginMenu == True:
    
        print("~~~LOGGIN SCREEN:~~~\nAre you registered yet or not?\n")
        for eachOption in loginOptions:
            print (eachOption, loginOptions[eachOption])
    
        loginMenuSelection = input("Choose your path: ")
        
        if loginMenuSelection == '1':
            print("GO TO USERNAME AND PASSWORD PART!")
            oldUser = True
        if loginMenuSelection == '2':
            print("GO TO NEW REGISTRATION PAGE!")
            newUser = True
            
            #THIS IS GOING TO BE THE NEW USER SCREEN!
        if newUser == True:
            print("YOU ARE A PEASANT. REGISTER.")
            newUserName = input("Give me your Email!: ")
            newUserPass = input("Give me your password!: ")
            print("CONGRATS ON JOINING THE FUN!")
            loginMenu = False
            return
        
        if oldUser == True:
            print("Okay we've got you, now give me your username!")
            oldUserName = input("Give me your Email!: ")
            oldUserPass = input("Give me your password!: ")
            print("Welcome back!")
            loginMenu = False     
            return
        
    print("K so we broke out of that shit")

def mainMenu(connection):
    #Now we have that main menu of a trillion various options as requested.
    #Initialize all the things.

    mainMenu = True
    mainMenuOptions = {} #empty dict
    isAirlineAgent = False #THIS CAN BE TRUE OPENING MORE OPTIONS!
    mainMenuOptions['1'] = "Search for flights."
    mainMenuOptions['2'] = "Make a booking."
    mainMenuOptions['3'] = "List exiting bookings."
    mainMenuOptions['4'] = "Cancel a booking."
    mainMenuOptions['5'] = "Logout."
    mainMenuOptions['6'] = "AIRLINE AGENTS ONLY: Record a flight departure."
    mainMenuOptions['7'] = "AIRLINE AGENTS ONLY: Record a flight arrival."
    while mainMenu == True:
        print("\n")
        print("Welcome to the main screen that will decide your fates")
        for eachOption in mainMenuOptions:
            print (eachOption, mainMenuOptions[eachOption])
    
        
        mainMenuSelection = input("Tell me which option you want: ")
        if mainMenuSelection == '1':
            searchForFlights(connection)
    
            
        if mainMenuSelection == '2':
            makeBookingOption(connection)
    
        if mainMenuSelection == '3':
            listExitingBookings()
    
            
        if mainMenuSelection == '4':
            cancelABooking()
    
            
        if mainMenuSelection == '5':
            logoutConfirm = logoutFunction()
            return logoutConfirm
            
        if mainMenuSelection == '6':
            recordFlightDeparture(isAirlineAgent)

        
        if mainMenuSelection == '7':
            recordFlightArrival(isAirlineAgent)
    


#All of the functions called upon by the main menu. (All 7 options!) 
def searchForFlights(connection):
    # prompt user for source, destination and departure date
    curs = connection.cursor()
    print("SEARCH FOR FLIGHTS OPTION BEGIN")
    
    #sql statements for case insensitivity
    curs.execute("alter session set NLS_COMP=LINGUISTIC")
    curs.execute("alter session set NLS_SORT=BINARY_CI")
    #searching for airports if the user didn't give a 3 letter airport code
    input_source = input("Enter source: ")
    if len(input_source) > 3 :
        curs.execute("SELECT * from AIRPORTS where city ="+"'"+input_source+"'" + " or name LIKE '%"+input_source+"%'" )
        # executing a query
        # get all data and print it
        rows = curs.fetchall()
        for row in rows:
            print("|Airport Code:",row[0],"|Airport Name:",row[1],"|City:",row[2],"|Country:",row[3],"|Time Zone:",row[4])
        flight_source = input("\nPlease select and enter the three letter airport code of your source airport: ")
        print("\n")

    else :
        flight_source = input_source

    #searching for destination airports
    input_destination = input("Enter destination: ")
    if len(input_destination) > 3 :
        curs.execute("SELECT * from AIRPORTS where city ="+"'"+input_destination+"'" + " OR name LIKE '%"+input_destination+"%'" )
        # executing a query
        # get all data and print it
        rows = curs.fetchall()
        for row in rows:
            print("|Airport Code:",row[0],"|Airport Name",row[1],"|City:",row[2],"|Country",row[3],"|Time Zone:",row[4])
        flight_destination = input("\nPlease select and enter the three letter airport code of your destination airport: ")
        print("\n")

    else:
        flight_destination = input_destination

    #only taking departure date in this format
    flight_departure = input("Enter departure date in DD-Mon-YY format: ")
    print("\n")

    #direct flight results
    curs.execute("SELECT flightno, src, dst, dep_date, seats, price FROM AVAILABLE_FLIGHTS WHERE src =" + "'" +flight_source+ "'" + " AND dst =" + "'" +flight_destination+ "'" + " and dep_date =" + "'" +flight_departure+ "'" + " and seats > 1 ORDER BY price")
    rows = curs.fetchall()
    for row in rows:
        print("|Flight Number:",row[0],"|Source Airport:",row[1],"|Destination Airport:",row[2],"|Departure Date:",row[3].strftime('%d-%b-%Y'), "|Seats Available:",row[4],"|Seat Price",row[5])

    curs.close()

def listExitingBookings():
    print("LIST EXITING BOOKINGS")  
    
def cancelABooking():
    print("CANCEL A BOOKING") 
    
def makeBookingOption(connection):
    curs = connection.cursor()
    cursInsert = connection.cursor()
    print("MAKE A BOOKING OPTION")
    user_email = input("Please enter your email: ")
    user_email = "'"+user_email+"'"
    curs.execute("SELECT * from passengers where email ="+user_email)
    rows = curs.fetchall()

    if rows:
        pass
    else:
        print("\nThe Email address you've entered was not part of our database")
        print("Please give us your name and your country")
        user_name = input("Please enter your name:")
        user_name = "'"+user_name+"'"
        user_country = input("Please enter your country:")
        user_country = "'"+user_country+"'"

        cursInsert.execute("INSERT INTO PASSENGERS values "+"("+user_email+","+user_name+","+user_country+")");
        connection.commit()
    cursInsert.close()
    print("Please enter the flight number of your booking, fare type, departure date and the seat number")
    user_flightno = input("Enter flight number:")
    user_fare = input("Enter fare type:")
    user_departure = input("Enter departure date:")
    user_seat = input("Enter the seat number:")



    curs.close()

def logoutFunction():
    print("LOG OUT")
    print("Saved time of logoff!")
    return (True)    
    
    
    
def recordFlightArrival(isAirlineAgent):
    #Block non-airline agents from accessing this.
    if isAirlineAgent == False:
        print("You do NOT get to use this option! Sorry, not sorry!") 
        return

    #Now if they are actually a airline agent they proceed....
    print("RECORD FLIGHT ARRIVAL")        
    
def recordFlightDeparture(isAirlineAgent):
    #Block non-airline agents from accessing this.
    if isAirlineAgent == False:
        print("You do NOT get to use this option! Sorry, not sorry!")
        return
    
    #Now if they are actually a airline agent they proceed....
    print("RECORD FLIGHT DEPARTURE")  
        

#Main method is located HERE!
def main():

    exitCommand = False

    #takes and stores sql info from user
    # get username
    user = input("Username [%s]: " % getpass.getuser())
    if not user:
            user=getpass.getuser()
    
    # get password
    pw = getpass.getpass()
    conString=''+user+'/' + pw +'@gwynne.cs.ualberta.ca:1521/CRS'

    try:
        # Establish a connection in Python
        connection = cx_Oracle.connect(conString)

        #creates the view table of available flights upon connection
        create_available_view(connection)
        #user login stuff here
        loginMenu()
        #Allow constant repetition of the main menu for the user.
        while exitCommand != True:
            exitCommand = mainMenu(connection)
        connection.close()

    #if sql id or pw is incorrect it breaks
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        print( sys.stderr, "Oracle code:", error.code)
        print( sys.stderr, "Oracle message:", error.message)



        

if __name__ == "__main__":
    main()