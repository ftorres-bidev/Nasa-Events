USE NasaEvents

INSERT INTO silver_events (ObservationGuid, EventID, Title, EventDate, MagnitudeValue, MagnitudeUnit, GeometryType, categoryId, Lon, Lat, PlaceID)
 
SELECT 
CAST(SUBSTRING(HASHBYTES('SHA2_256',
            ID + N'|' + CONVERT(NVARCHAR(30), EventDate, 126)), 1, 16) AS UNIQUEIDENTIFIER) AS ObservationGuid,
ID, Title, EventDate, MagnitudeValue, MagnitudeUnit, GeometryType, categoryId, Lon, Lat, PlaceID
  FROM [NasaEvents].[dbo].[bronze_events] 

