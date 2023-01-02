from Household import *
from Person import *
from Vaccine import *
from random import *
from Test import *
from Location import *
from randomuser import RandomUser
import time as time
import datetime as datetime
import os


def str_time_prop(start, end, time_format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formatted in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start. Returns the random date as a timestamp.
    """

    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))

    ptime = stime + prop * (etime - stime)

    return time.mktime(time.localtime(ptime))


def random_date(start, end, prop):
    """
    :param start: start date of the interval
    :param end: end date of the interval
    :param prop: random int used to generate random date
    :return: a random date between start and stop as a timestamp
    """
    return str_time_prop(start, end, '%Y-%m-%d', prop)


def random_date_hour(start, end, prop):
    """
    :param start: start date of the interval
    :param end: end date of the interval
    :param prop: random int used to generate random date
    :return: a random date, with hours and minutes, between start and stop as a timestamp
    """
    return str_time_prop(start, end, '%Y-%m-%d %H:%M', prop)


households = []
people = []
tests = [Test("Serological"), Test("Molecular"), Test("Rapid")]
vaccines = [Vaccine("PfizerBioNTech", 35, 2), Vaccine("Moderna", 35, 2), Vaccine("AstraZeneca", 84, 2),
            Vaccine("JohnsonAndJohnson", 35, 1)]
locations = [Location("Cinema1", 2), Location("Cinema2", 2), Location("Cinema3", 2), Location("Restaurant1", 1.5),
             Location("Restaurant2", 1.5), Location("Restaurant3", 1.5), Location("Restaurant4", 1.5),
             Location("Restaurant5", 1.5), Location("Pub1", 1), Location("Pub2", 1), Location("Pub3", 1),
             Location("Pub4", 1), Location("Pub5", 1), Location("Hairdresser1", 0.5), Location("Hairdresser2", 0.5)]

positive_not_vaccinated_percentage = 0.6
positive_vaccinated_percentage = 0.2
second_dose_probability = 0.5
vaccinated_percentage = 0.6
household_number = 50
daily_test_num = 50
visits_num = 300
days = 31

complete_query = ""

# Generates nodes for the vaccines
print("Generating nodes for vaccines...")
for vaccine in vaccines:
    complete_query = complete_query + 'CREATE(' + str(
        vaccine.name) + ': Vaccine{name:"' + vaccine.name + '", coverage:' + str(
        vaccine.coverage) + ', min_doses:' + str(vaccine.minDoses) + '})\n'

# Generates nodes for tests
print("Generating nodes for test types...")
for test in tests:
    complete_query = complete_query + 'CREATE(' + test.type + ': Test{type:"' + test.type + '"})\n'

# Generates nodes for locations
print("Generating nodes for locations...")
i = 0
for location in locations:
    complete_query = complete_query + 'CREATE(' + location.name + ': Location{id:' + str(
        i) + ', name:"' + location.name + '", avg_stay_time:' + str(location.averageStay) + '})\n'
    i += 1
# Generates 30 households nodes with associated the number of members
print("Generating nodes for households...")
for house_id in range(household_number):
    members = randint(1, 7)
    address = RandomUser().get_street()
    household = Household(house_id, members, address)
    households.append(household)
    complete_query = complete_query + 'CREATE(h' + str(house_id) + ': Household {id: ' + str(
        house_id) + ', address:"' + household.address + '"})\n'

# Generates people for each household with random data taken from randomuser library
print("Generating nodes for people...")
i = 0
for house in households:
    user_list = RandomUser.generate_users(house.members, {'nat': 'it'})
    for user in user_list:
        people.append(
            Person(i, house.id, user.get_first_name(), user.get_last_name(), user.get_gender(), user.get_cell(),
                   user.get_city(), user.get_email(), user.get_dob(), False))
        # Creates the query to generate the Person node
        complete_query = complete_query + 'CREATE(p' + str(
            i) + ': Person {id: ' + str(
            i) + ', firstName: "' + user.get_first_name() + '", lastName: "' + user.get_last_name() + '", gender: "' + user.get_gender() + '", cell: "' + user.get_cell() + '", city: "' + user.get_city() + '", email: "' + user.get_email() + '", date_of_birth: "' + user.get_dob() + '"})\n'
        # Creates the query to generate the relation between the Person and its household
        complete_query = complete_query + 'CREATE (p' + str(i) + ')-[:PART_OF]->(h' + str(house.id) + ')\n'
        i += 1

# Takes 70% of the people in the db and assigns a vaccine to them
print("Associating people with vaccines...")
people_copy = people.copy()
vaccinatedNum = int(len(people) * vaccinated_percentage)

for i in range(vaccinatedNum):
    vaccinated = people_copy.pop(randint(0, len(people_copy) - 1))
    # vaccine_type = randint(0, len(vaccines))
    vaccine = choice(vaccines)
    date = datetime.date.fromtimestamp(random_date("2021-1-1", "2021-11-14", random()))
    
    # People that took a vaccine with a possible 2nd dose, have 50% to have already done it
    if vaccine.minDoses > 1 and random() > 0.5:
        complete_query = complete_query + 'CREATE (p' + str(
            vaccinated.id) + ')-[:GETS{dose:2, datetime:datetime("' + str(datetime.date.fromtimestamp(random_date(str(date), "2021-11-14",
                                                                         random()))) + '")}]->(' + vaccine.name + ')\n'
    else:
        complete_query = complete_query + 'CREATE (p' + str(
            vaccinated.id) + ')-[:GETS{dose:1, datetime:datetime("' + str(date) + '")}]->(' + vaccine.name + ')\n'

    index = people.index(vaccinated)
    people[index].vaccinated = True

# Generates contacts between random people
print("Generating contacts between people...")
contactNum = len(people)
for i in range(contactNum):
    p1 = choice(people)
    p2 = choice(people)

    if p1 != p2:
        date = datetime.datetime.fromtimestamp(random_date_hour("2021-10-14 00:00", "2021-11-14 23:59", random()))
        complete_query = complete_query + 'CREATE (p' + str(p1.id) + ')-[:CONTACT{datetime:datetime("' + str(
            date.date()) + 'T' + str(date.time()) + '")}]->(p' + str(
            p2.id) + ')\n'

# Generates one test per day form 2021-10-14 to 2021-11-14
print("Generating 50 tests a day from 2021-10-14 to 2021-11-14...")
test_date = datetime.date(2021, 10, 14)
for day in range(days):
    for dailyTest in range(daily_test_num):
        tested_person = choice(people)
        test_type = choice(tests)
        if tested_person.vaccinated:
            test_result = "Negative" if random() > positive_vaccinated_percentage else "Positive"
        else:
            test_result = "Negative" if random() > positive_not_vaccinated_percentage else "Positive"
        complete_query = complete_query + 'CREATE(p' + str(
            tested_person.id) + ')-[:TAKES{datetime:datetime("' + str(
            test_date) + '") , result:"' + test_result + '"}]->(' + test_type.type + ')\n'
    test_date += datetime.timedelta(days=1)

# Associates locations with people
print("Associating people with locations...")
for i in range(visits_num):
    location = choice(locations)
    person = choice(people)
    location_date = datetime.date.fromtimestamp(random_date("2021-10-14", "2021-11-14", random()))

    complete_query = complete_query + 'CREATE(p' + str(person.id) + ')-[:VISITS{datetime:datetime("' + str(
        location_date) + '")}]->(' + location.name + ')\n'

print(complete_query)

here = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(here, 'Query.txt')

f = open(filename, "w", encoding="utf-8")
f.write(complete_query)
f.close()
