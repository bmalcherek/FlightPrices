import scraper
import database_interaction


df = scraper.scrape('BER', 'MAD', '2019-09-02')

results = list()
for index, row in df.iterrows():
    flight = list()
    for column in df.columns:
        flight.append(row[column])
    results.append(flight)

conn = database_interaction.create_connection('db\FlightPrices.sqlite')
print(database_interaction.insert_flight(conn, results[0]))

print(df)
