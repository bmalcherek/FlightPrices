import database_interaction

conn = database_interaction.create_connection('db\FlightPrices.sqlite')
# print(database_interaction.get_flights_by_origin(conn, 'SXF'))
kwargs = {
    'origin': 'SXF',
    'dep_date': '2019-09-11'
}
print(database_interaction.get_flights(conn, **kwargs))

origin = 'SXF'
visits = ['MAD', 'BCN']
