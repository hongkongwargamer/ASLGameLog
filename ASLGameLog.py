import sqlite3
from datetime import datetime, timedelta
from prettytable import prettytable
from prettytable import from_db_cursor
import csv

#Advanced Squad Leader game logging program by HongKongWargamer
#Started 12 August 2021
DATE_FORMAT='%Y-%m-%d'

#Class for each record, for flexibility
class PlayRecord:
    def __init__(self,scen_id,scen_name,opponent_fn,opponent_ln,side_played,attack_defender,start_date,finish_date,result,format):
        self.scen_id=scen_id
        self.scen_name=scen_name
        self.opponent_fn=opponent_fn
        self.opponent_ln=opponent_ln
        self.side_played=side_played
        self.attack_defender=attack_defender
        self.start_date=start_date
        self.finish_date=finish_date
        self.result=result
        self.format=format

#Command Menu
def command_menu():
    #Showing a count of the # of records
    cur.execute("SELECT COUNT(*) FROM gamelog")
    print("\nWe have a grand total of {} records".format(cur.fetchone()))
    #The Menu
    print("\nAdvanced Squad Leader Game Log 1.0")
    print("==================================")
    print("Press 1: Show all records")
    print("Press 2: Input record")
    print("Press 3: Delete record")
    print("Press 4: Query by finish dates")
    print("Press 9: Export to CSV")
    print("Press *: See Credits")
    print("Type \"End\": End this Session")
    command=input("\nInput command: ")
    if command=="1":
        #Show all records
        report_all()
        return True
    elif command=="2":
        #Add record
        record=input_record()
        add_record(record)
        report_all()
        return True
    elif command=="3":
        #Delete record
        record=input_record()
        delete_record(record)
        return True
    elif command=="4":
        #Query by Year
        query_date_range()
        return True
    elif command=="9":
        #Export to CSV
        export_csv()
        return True
    elif command=="*":
        print_credits()
        return True
    elif command.lower()=="end":
        export_csv()
        con.close
        quit()
        return False
    else:
        return True
    return
    



#Create table
def create_table():
    cur.execute("""CREATE TABLE gamelog (
                scen_id text,
                scen_name text,
                opponent_fn text,
                opponent_ln text,
                side_played text,
                attack_defender text,
                start_date text,
                finish_date text,
                result text,
                format text
                )""")

#Input Records
def input_record():

    #Date Validation
    def validate_date(d):
        try:
            datetime.strptime(d, DATE_FORMAT)
            return True
        except ValueError:
            return False

    #Getting scenario ID and name
    print("\n\nEntering Details of the Game .....")
    scen_id=""
    scen_name=""
    while scen_id=="":
        scen_id=input("Enter Scenario ID: ")
        if len(scen_id) > 8:
            print("Your Scenario ID seems to be too long?")
            scen_id=""
        else:
            pass
    while scen_name=="":
        scen_name=input("Enter Scenario Name: ")

    #List existing first names & ask for input
    cur.execute("SELECT DISTINCT opponent_fn FROM gamelog")
    print("Existing opponent first names: {}".format(cur.fetchall()))
    opponent_fn=""
    while opponent_fn=="":
        opponent_fn=input("Enter your Opponent's First Name: ")

    
    #List existing last names & ask for input
    cur.execute("SELECT DISTINCT opponent_ln FROM gamelog")
    print("Existing opponent last names: {}".format(cur.fetchall()))
    opponent_ln=""
    while opponent_ln=="":
        opponent_ln=input("Enter your Opponent's Last Name: ")
        opponent_ln=opponent_ln.capitalize()
    
    #List existing nationalities & ask for input
    cur.execute("SELECT DISTINCT side_played FROM gamelog")
    print("Existing nationalities in database: {}".format(cur.fetchall()))
    side_played=""
    while side_played=="":
        side_played=input("Which nationality did you play? ")

    # this 'input' command works for Python 3
    # if you're using Python 2, use 'raw_input' instead of 'input'
    while True:
        attack_defender = input("Were you the Attacker/ Defender? ")
        if attack_defender.lower() in ["attacker", "defender"]:
            attack_defender=attack_defender.capitalize()
            # we've got valid input! Break out of our 'while True' loop.
            break
        else:
            # invalid input. Loops back and asks again.
            print("Sorry, you must enter either Attacker or Defender.")
            continue

    #Start date?  Date validation
    valid=False
    while valid==False:
        start_date=input("Start date? YYYY-MM-DD ")
        valid=validate_date(start_date)
    start_date=datetime.strptime(start_date,DATE_FORMAT)

    #End date?  Date validation
    finish_date=datetime.strptime("1990-01-01",DATE_FORMAT)
        #Finish date should be after start date
    while finish_date<start_date:
        valid=False
        while valid==False:
            finish_date=input("Finish date? YYYY-MM-DD ")
            valid=validate_date(finish_date)
            if valid:
                finish_date=datetime.strptime(finish_date,DATE_FORMAT)

    #Win/Lost/Draw/Hold/Abandon?  Check input
    while True:
        result=input("Won/Lost/Draw/Hold/Abdn/PT ")
        if result.lower() in ["won","lost","draw","hold","abdn","pt"]:
            result=result.capitalize()
            if result == "Pt":
                result = result.upper()
            else:
                break
            break
        else:
            print("Sorry, results are confined to Won/Lost/Draw/Hold/Abdn/PT.")
            continue

    #Live/VASL/PBeM?  Check input
    while True:
        format=input("FtF/VASL/PBeM ")
        if format.lower() in ["ftf","vasl","pbem"]:
            if format.lower() == "ftf":
                format="FtF"
            elif format.lower() == "vasl":
                format="VASL"
            elif format.lower() == "pbem":
                format="PBeM"
            
            break
        else:
            print("Sorry, formats are confined to FtF, VASL or PBeM.")
            continue

    #Create an instance of PlayRecord
    record = PlayRecord(scen_id,scen_name,opponent_fn,opponent_ln,side_played,attack_defender,start_date,finish_date,result,format)
    return record

#Add Record after seeking user confirmation & looking for duplicates
def add_record(record):
    # Add a record to the table via an instance of PlayRecord
    print("\n\n")
    x=prettytable.PrettyTable()
    x.field_names=column_names.split(",")
    x.add_row([record.scen_id,record.scen_name,record.opponent_fn,record.opponent_ln,record.side_played,record.attack_defender,record.start_date.strftime(DATE_FORMAT),record.finish_date.strftime(DATE_FORMAT),record.result, record.format])
    print(x)

    user_okay=input("Save to Log? (Y/N) ")
    if user_okay.lower()=="y":
            # Check to see if there's a duplicate, if not, commit 
        cur.execute("SELECT * FROM gamelog WHERE scen_id=? AND opponent_ln=? AND attack_defender=? AND finish_date=?", (record.scen_id, record.opponent_ln, record.attack_defender,record.finish_date.date()))
        if len(str(cur.fetchone())) >5:
            print("This play record already exists. Not saving it.")
            return
        else:
            cur.execute("INSERT INTO gamelog VALUES(?,?,?,?,?,?,?,?,?,?)",(record.scen_id,record.scen_name,record.opponent_fn,record.opponent_ln,record.side_played,record.attack_defender,record.start_date.strftime(DATE_FORMAT),record.finish_date.strftime(DATE_FORMAT),record.result,record.format))
            con.commit()
            print("New game record saved\n")
            # con.close
            return
    else:
        print("Okay, not saving this.")
        return
    return

# Delete Record after seeking user confirmation
def delete_record(record):
    print("\n\n")
    search_fields="scen_id=? AND scen_name=? AND opponent_fn=? AND opponent_ln=? AND side_played=? AND attack_defender=? AND result=? AND start_date=? AND finish_date=? AND result=? AND format=?"
    cur.execute("SELECT * FROM gamelog WHERE {}".format(search_fields), (record.scen_id, record.scen_name, record.opponent_fn, record.opponent_ln, record.side_played, record.attack_defender, record.result, record.start_date.date(), record.finish_date.date(), record.result, record.format))
    del_record=cur.fetchall()
    if del_record:
        pretty_table(del_record)
        print("\nFound the above for deletion\n")
    else:
        print("\nThis record doesn't exist\n")
        return

    user_okay=input("Delete this Record? (Y/N) ")
    if user_okay.lower()=='y':
        cur.execute("DELETE FROM gamelog WHERE {}".format(search_fields), (record.scen_id, record.scen_name, record.opponent_fn, record.opponent_ln, record.side_played, record.attack_defender, record.result, record.start_date.date(), record.finish_date.date(), record.result, record.format))
        con.commit()
        report_all()
        print("\nRecord(s) deleted\n")
    else:
        print("\nNothing deleted\n")
        return
    return

# Query Data by Start Date Range
def query_table(Search_Field, Search_String):
    Field=Search_Field
    String=Search_String
    cur.execute("SELECT * FROM gamelog WHERE Field=String")
    print(cur.fetchall())

# Export data to CSV
def export_csv():
    cur.execute("SELECT {} FROM gamelog".format(column_names))
    export_file=cur.fetchall()

    with open("ASLGameLogData.csv","w") as csv_file:
        csv_writer=csv.writer(csv_file, dialect='excel')
        
        for line in export_file:
            csv_writer.writerow(line)
    print("\nGame records exported to CSV\n")

# Query Data by Date Range
def query_date_range():

    #date validation
    def validate_date(d):
        try:
            datetime.strptime(d, DATE_FORMAT)
            return True
        except ValueError:
            return False

    print("\n\nQuery by Dates:")
    #Start date?  Date validation
    valid=False
    while valid==False:
        query_start_date=input("Start date? YYYY-MM-DD ")
        valid=validate_date(query_start_date)
    query_start_date=datetime.strptime(query_start_date,DATE_FORMAT)

    #End date?  Date validation
    query_finish_date=datetime.strptime("1990-01-01",DATE_FORMAT)
        #Finish date should be after start date
    while query_finish_date<query_start_date:
        valid=False
        while valid==False:
            query_finish_date=input("Finish date? YYYY-MM-DD ")
            valid=validate_date(query_finish_date)
            if valid:
                query_finish_date=datetime.strptime(query_finish_date,DATE_FORMAT)
    cur.execute("SELECT {} FROM gamelog WHERE finish_date BETWEEN ? AND ?".format(column_names),(query_start_date,query_finish_date))
    query_results=cur.fetchall()
    pretty_table(query_results)

def pretty_table(show_records):
    x=prettytable.PrettyTable()
    x.field_names=column_names.split(",")
    for show_record in show_records:
        x.add_row(show_record)
    print(x)


# Query Data by End Date Range



# Query Data by Opponent Name
 

# Query Data by Scenario ID


# Query Data by Scenario Name


# Update Play Record


# Commit changes & close





# REPORT ALL DATA
def report_all():
    cur.execute("SELECT {} FROM gamelog".format(column_names))
    mytable = from_db_cursor(cur)
    mytable.align["scen_id"]='l'
    mytable.align["scen_name"]='l'
    mytable.align["opponent_fn"]='l'
    mytable.align["opponent_ln"]='l'
    mytable.align["side_played"]='l'
    print("\n")
    print(mytable.get_string(sortby="finish_date"))
 

# Report Games by Completed Date Range (W/L) (A/D) (Nationality) (Format)


# Report Games that are in Progress


# Report Games that are Playtesting

# Print credits
def print_credits():
    print("\n\nCreated by Jackson CS Kwan, 12 Aug 2021")
    print("Creator provides NO guarantees.  Use at your own risk.")
    print("hongkongwargamer@disroot.org")
    print("hongkongwargamer.com")
    print("@HWargamer\n")


#Main Program =====================================================
#Create Game Log db file if none exists

con=sqlite3.connect('ASLgamelog.db')
cur=con.cursor()
column_names="scen_id, scen_name, opponent_fn, opponent_ln, side_played, attack_defender, start_date, finish_date, result, format"

def main():
    #Create Table if needed 
    #Check if a table exists, if not, creates 'gamelog' Table
    cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='gamelog' ")
    if (cur.fetchone()[0])<1:
        print("\nCreating a gamelog table\n")
        create_table()

    #Calling up the Command Menu
    while command_menu():
        command_menu()

if __name__=="__main__":
    main()