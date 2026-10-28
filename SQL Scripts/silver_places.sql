INSERT INTO silver_places (PlaceID, PlaceName, State, CountryCode, Country, Lat, Lon)

SELECT [PlaceID]
      ,[PlaceName]
      ,[State]
      ,[CountryCode]
      ,[Country]
      ,[Lat]
      ,[Lon]
  FROM [NasaEvents].[dbo].[bronze_places]
