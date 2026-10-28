/*******************************************************************************
  Gold_fact_topHighest_earthquakes.sql
  Purpose : Top 10 countries per year ranked by their strongest earthquake.
  Grain   : One row per (Year, Country) with a rank of 10 or better.
  Sources : dbo.Gold_fact_earthquakes (facts), dbo.Gold_dim_places (country).
  Notes   : - DENSE_RANK gives tied magnitudes the same rank and leaves no
              gaps, so a year can return more than 10 rows when countries tie.
            - INNER JOIN: earthquakes with no PlaceID are excluded.
            - The column [County] is spelled as in the original view
              (probably meant "Country"); renaming it would break anything
              already reading the view.
*******************************************************************************/

USE [NasaEvents];
GO

SET ANSI_NULLS ON;
GO

SET QUOTED_IDENTIFIER ON;
GO

CREATE VIEW [dbo].[Gold_fact_topHighest_earthquakes]
AS
SELECT
    [Country],
    [Year],
    [Magnitude],
    [Rank]
FROM
(
    -- Strongest earthquake per country and year, ranked within each year.
    SELECT
        b.[Country]                 AS [Country],
        YEAR(a.[EventTimeUtc])      AS [Year],
        MAX(a.[Magnitude])          AS [Magnitude],
        DENSE_RANK() OVER (
            PARTITION BY YEAR(a.[EventTimeUtc])
            ORDER BY MAX(a.[Magnitude]) DESC
        )                           AS [Rank]
    FROM [dbo].[Gold_fact_earthquakes] AS a
    INNER JOIN [dbo].[Gold_dim_places] AS b
        ON b.[PlaceID] = a.[PlaceID]
    GROUP BY
        b.[Country],
        YEAR(a.[EventTimeUtc])
) AS TopEarth
WHERE [Rank] <= 10;    -- keep only the top 10 ranks per year
GO
