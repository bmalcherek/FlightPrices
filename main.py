import scraper
import database_interaction
import time

conn = database_interaction.create_connection('db\FlightPrices.sqlite')

df = scraper.scrape('BER', 'MAD', '2019-09-02')

results = list()
for index, row in df.iterrows():
    flight = list()
    for column in df.columns:
        flight.append(row[column])
    results.append(flight)

for operator in df['operator']:
    if database_interaction.get_operator_id(conn, operator) == 'no such operator':
        database_interaction.insert_operator(conn, operator)
    print(operator)

# print(database_interaction.insert_flight(conn, results[0]))

print(df)


# origins = ['WAW']
# destinations = ['MAD', 'BCN', 'PAR']
# dates = ['2019-09-01', '2019-09-02']
#
# requests_count = 0
#
# for origin in origins:
#     for destination in destinations:
#         for date in dates:
#             while scraper.get_page(origin, destination, date) != 'success':
#                 time.sleep(3)
#             print(headers)
#             requests_count += 1
#             scrape(origin, destination, date, headers)
#             time.sleep(15)
