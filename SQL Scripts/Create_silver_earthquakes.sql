/*******************************************************************************
  Create_silver_earthquakes.sql
  Purpose : Creates the silver earthquake table (one row per USGS event).
  Source  : Loaded from dbo.bronze_earthquakes by silver_earthquakes.sql.
  Run     : Once, before silver_earthquakes.sql.
*******************************************************************************/

USE [NasaEvents];
GO

SET ANSI_NULLS ON;
GO

SET QUOTED_IDENTIFIER ON;
GO

CREATE TABLE [dbo].[silver_earthquakes]
(
    -- Identity
    [ID]                    VARCHAR(250) NOT NULL,   -- USGS event id (upper-cased)

    -- Magnitude
    [Magnitude]             FLOAT        NULL,
    [Magnitude_Type]        VARCHAR(MAX) NULL,       -- raw code, e.g. 'ml', 'mww'
    [Magnitude_Description] VARCHAR(MAX) NULL,       -- readable name of the code

    -- Description and timing (UTC)
    [Place]                 VARCHAR(MAX) NULL,       -- e.g. '10 km SW of Ridgecrest, CA'
    [EventTimeUtc]          DATETIME     NULL,
    [UpdateTimeUtc]         DATETIME     NULL,

    -- Impact and quality measures
    [Felt]                  FLOAT        NULL,       -- number of "felt" reports
    [Cdi]                   FLOAT        NULL,       -- community-reported intensity
    [Mmi]                   FLOAT        NULL,       -- instrumental intensity
    [Alert]                 VARCHAR(MAX) NULL,       -- PAGER level, 'n/a' when missing
    [Tsunami]               BIGINT       NULL,       -- 1 = tsunami flag set
    [Sig]                   BIGINT       NULL,       -- significance score
    [Nst]                   FLOAT        NULL,       -- stations used
    [Dmin]                  FLOAT        NULL,
    [Rms]                   FLOAT        NULL,
    [Gap]                   FLOAT        NULL,
    [Type]                  VARCHAR(MAX) NULL,       -- e.g. 'Earthquake'

    -- Location
    [Lon]                   FLOAT        NULL,
    [Lat]                   FLOAT        NULL,
    [DepthKm]               FLOAT        NULL,
    [PlaceID]               INT          NULL,       -- nearest place (see silver_places)

    CONSTRAINT [PK_silver_earthquakes] PRIMARY KEY ([ID])
);
GO
