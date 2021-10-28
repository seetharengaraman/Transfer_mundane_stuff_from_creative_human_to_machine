# Import required modules
import requests
from google.cloud import bigquery
from timezonefinder import TimezoneFinder

# Construct a BigQuery client object.
client = bigquery.Client()
#Query for all records that require latitude, longitude and corresponding timezone
query = """
	SELECT SOURCE_CITY,POSTALCODE_CORRECTED SOURCE_POSTALCODE,SOURCE_COUNTRY FROM `gcpproject1.OrderData.TimeZoneFetch`
WHERE SOURCE_LATITUDE IS NULL OR SOURCE_LONGITUDE IS NULL OR TIMEZONE IS NULL;
"""
latitude =''
longitude=''
query_job = client.query(query)  # Make an API request to run the query
print("The query data:")
for row in query_job:
	print("SOURCE_CITY={}, SOURCE_POSTALCODE={}".format(row[0], row["SOURCE_POSTALCODE"]))
	#For each postal code and country fetch latitude and longitude
	try:
		url = "https://nominatim.openstreetmap.org/search/?postalcode={}&country={}&format=json".format(row["SOURCE_POSTALCODE"],row["SOURCE_COUNTRY"])
		response = requests.get(url).json()
		latitude = response[0]["lat"]
		longitude = response[0]["lon"]
	except Exception as e:
	#If unable to fetch latitude and longitude by postal code and country, fetch by city and country
		try:
			url = "https://nominatim.openstreetmap.org/search/?city='{}'&country='{}'&format=json".format(row["SOURCE_CITY"],row["SOURCE_COUNTRY"])
			response = requests.get(url).json()
			latitude = response[0]["lat"]
			longitude = response[0]["lon"]
		except Exception as e:
			print("Unexpected error occurred during lat/long fetch", e )
	if bool(latitude):
		try:
			#Fetch Time zone by latitude and longitude
			tf = TimezoneFinder()
			timezone = tf.timezone_at(lng=float(longitude), lat=float(latitude))
			print(timezone)
			#Update latitude, longitude and timezone 
			query = """
					UPDATE `gcpproject1.OrderData.TimeZoneFetch`
						SET SOURCE_LATITUDE = @latitude, SOURCE_LONGITUDE = @longitude,
						TIMEZONE = @timezone
						WHERE POSTALCODE_CORRECTED = @postalcode
						AND SOURCE_COUNTRY = @country;
					"""
			job_config = bigquery.QueryJobConfig(
			query_parameters=[
			bigquery.ScalarQueryParameter("latitude", "STRING", latitude),
			bigquery.ScalarQueryParameter("longitude", "STRING", longitude),
			bigquery.ScalarQueryParameter("timezone", "STRING", timezone),
			bigquery.ScalarQueryParameter("postalcode", "STRING", row["SOURCE_POSTALCODE"]),
			bigquery.ScalarQueryParameter("country", "STRING", row["SOURCE_COUNTRY"]),
							]
					)
			query_job = client.query(query, job_config=job_config)
			print(f'Result:{query_job.result()}')            
		except Exception as e:
			print("Unexpected error occurred during update", e )

