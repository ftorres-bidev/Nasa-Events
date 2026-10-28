/*******************************************************************************
  Gold_dim_places.sql
  Purpose : Gold-layer place dimension, exposed as a view over silver.
  Grain   : One row per place (PlaceID).
  Source  : dbo.silver_places.
  Used by : Gold_fact_earthquakes (via PlaceID).
  Note    : PlaceName, Lat and Lon are not exposed; add them here if reports
            need them. Columns are listed explicitly so later changes to
            silver_places do not silently change the gold contract.
*******************************************************************************/

USE [NasaEvents];
GO

SET ANSI_NULLS ON;
GO

SET QUOTED_IDENTIFIER ON;
GO

CREATE VIEW [dbo].[Gold_dim_places]
AS
SELECT
    [PlaceID],        -- key
    [State],          -- admin region, '' when unknown
    [CountryCode],    -- ISO 3166-1 alpha-2
    [Country]
FROM [dbo].[silver_places];
GO
