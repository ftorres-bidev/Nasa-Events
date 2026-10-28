/*******************************************************************************
  silver_places.sql
  Purpose : Copies the places table from bronze to silver, keeping PlaceID so
            earthquakes and events still link to the same places.
  Note    : Plain INSERT, so run it against an empty silver_places table.
            Run before silver_events.sql (foreign key dependency).
*******************************************************************************/

USE [NasaEvents];
GO

INSERT INTO [dbo].[silver_places]
(
    [PlaceID],
    [PlaceName],
    [State],
    [CountryCode],
    [Country],
    [Lat],
    [Lon]
)
SELECT
    [PlaceID],
    [PlaceName],
    [State],
    [CountryCode],
    [Country],
    [Lat],
    [Lon]
FROM [dbo].[bronze_places];
GO
