/*******************************************************************************
  Gold_fact_natural_event.sql
  Purpose : Gold-layer fact view counting EONET observations per
            category, country, year and month.
  Grain   : One row per (CategoryID, Country, Year, Month).
  Sources : dbo.silver_events (facts), dbo.silver_places (country lookup).
  Notes   : - [Total Events] counts observations (rows in silver_events),
              not distinct events, so an event tracked over several days is
              counted once per observation.
            - INNER JOIN: observations with no PlaceID are excluded.
*******************************************************************************/

USE [NasaEvents];
GO

SET ANSI_NULLS ON;
GO

SET QUOTED_IDENTIFIER ON;
GO

CREATE VIEW [dbo].[Gold_fact_natural_event]
AS
SELECT
    e.[categoryId]            AS [CategoryID],     -- joins to Gold_dim_categories
    p.[Country]               AS [Country],
    YEAR(e.[EventDate])       AS [Year],
    MONTH(e.[EventDate])      AS [Month],
    COUNT(e.[ObservationGuid]) AS [Total Events]   -- measure
FROM [dbo].[silver_events] AS e
INNER JOIN [dbo].[silver_places] AS p
    ON p.[PlaceID] = e.[PlaceID]
GROUP BY
    e.[categoryId],
    p.[Country],
    YEAR(e.[EventDate]),
    MONTH(e.[EventDate]);
GO
