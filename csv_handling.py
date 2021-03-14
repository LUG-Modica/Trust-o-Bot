import csv
from tempfile import NamedTemporaryFile
import shutil

filename='data.csv'

def add_reputation(username,n):
    tempfile = NamedTemporaryFile(mode='w', delete=False)
    fields = ['username','reputation']
    found = False

    with open(filename, 'r') as csvfile, tempfile:
        reader = csv.DictReader(csvfile, fieldnames=fields)
        writer = csv.DictWriter(tempfile, fieldnames=fields)

        for row in reader:
            if row['username'] == str(username):
                found = True
                row['reputation'] = str(int(row['reputation']) + int(n))
            row = {'username': row['username'], 'reputation': row['reputation']}
            writer.writerow(row)
        # if it's the first time we add reputation
        if (found == False):
            row = {'username': username, 'reputation': str(n)}
            writer.writerow(row)

    shutil.move(tempfile.name, filename)

def get_user_reputation(username):
    fields = ['username','reputation']
    return_string = ""

    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=fields)

        for row in reader:
            if (row['username'] == username):
                return_string += row['username'] + " : " + row['reputation'] + "\n"
                return return_string

    return return_string

# returns a string containing the reputation
def get_users_reputation():
    fields = ['username','reputation']
    return_string = ""

    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=fields)

        first = False # in order to skip the first string
        for row in reader:
            if (first == False): # skip the first row 
                first = True
                continue
            return_string += row['username'] + " : " + row['reputation'] + "\n"

    return return_string




