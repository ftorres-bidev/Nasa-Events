/*******************************************************************************
  silver_events.sql
  Purpose : Copies bronze_events into silver_events and adds a surrogate key.
  Key     : ObservationGuid is a deterministic GUID built from the first 16
            bytes of SHA-256(EventID | EventDate), so the same observation
            always gets the same GUID on every load.
  Note    : Plain INSERT, so run it against an empty silver_events table.
            Load silver_places first (foreign key on PlaceID).
*******************************************************************************/

USE [NasaEvents];
GO

INSERT INTO [dbo].[silver_events]
(
    [ObservationGuid],
    [EventID],
    [Title],
    [EventDate],
    [MagnitudeValue],
    [MagnitudeUnit],
    [GeometryType],
    [categoryId],
    [Lon],
    [Lat],
    [PlaceID]
)
SELECT
    -- Style 126 = ISO 8601, so the hash input format is stable.
    CAST(SUBSTRING(
            HASHBYTES('SHA2_256',
                [ID] + N'|' + CONVERT(NVARCHAR(30), [EventDate], 126)),
            1, 16)
         AS UNIQUEIDENTIFIER)                     AS [ObservationGuid],
    [ID]                                          AS [EventID],
    [Title],
    [EventDate],
    [MagnitudeValue],
    [MagnitudeUnit],
    [GeometryType],
    [categoryId],
    [Lon],
    [Lat],
    [PlaceID]
FROM [dbo].[bronze_events];
GO
