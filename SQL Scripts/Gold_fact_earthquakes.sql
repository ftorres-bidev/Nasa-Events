/*******************************************************************************
  Gold_fact_earthquakes.sql
  Purpose : Gold-layer earthquake fact view, exposing only the columns needed
            for reporting.
  Grain   : One row per earthquake (USGS event id).
  Source  : dbo.silver_earthquakes.
  Links   : PlaceID joins to Gold_dim_places.
  Note    : Update time, location coordinates, depth and the impact/quality
            measures (Felt, Cdi, Mmi, Sig, ...) are left out on purpose; add
            them here if reports need them.
*******************************************************************************/

USE [NasaEvents];
GO

SET ANSI_NULLS ON;
GO

SET QUOTED_IDENTIFIER ON;
GO

CREATE VIEW [dbo].[Gold_fact_earthquakes]
AS
SELECT
    [ID],
    [Magnitude],                -- measure
    [Place],                    -- original USGS description text
    [EventTimeUtc],
    [Magnitude_Type],           -- raw code, e.g. 'ml', 'mww'
    [Magnitude_Description],    -- readable name of the code
    [Type],
    [PlaceID]                   -- foreign key to Gold_dim_places
FROM [dbo].[silver_earthquakes];
GO
