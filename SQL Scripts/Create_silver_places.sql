/*******************************************************************************
  Create_silver_places.sql
  Purpose : Creates the silver places table shared by earthquakes and events.
  Source  : Loaded from dbo.bronze_places by silver_places.sql.
  Run     : Once, BEFORE Create_silver_events.sql (which references it).
*******************************************************************************/

USE [NasaEvents];
GO

SET ANSI_NULLS ON;
GO

SET QUOTED_IDENTIFIER ON;
GO

CREATE TABLE [dbo].[silver_places]
(
    -- PlaceID is copied from bronze_places, so it is NOT an IDENTITY here.
    [PlaceID]     INT           NOT NULL,
    [PlaceName]   NVARCHAR(200) NOT NULL,   -- nearest GeoNames city
    [State]       NVARCHAR(100) NOT NULL,   -- admin region, '' when unknown
    [CountryCode] NCHAR(2)      NOT NULL,   -- ISO 3166-1 alpha-2
    [Country]     NVARCHAR(100) NULL,
    [Lat]         FLOAT         NULL,       -- coordinates of the city itself
    [Lon]         FLOAT         NULL,

    CONSTRAINT [PK_silver_places] PRIMARY KEY ([PlaceID])
);
GO
