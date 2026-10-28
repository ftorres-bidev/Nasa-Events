/*******************************************************************************
  Create_silver_events.sql
  Purpose : Creates the silver EONET events table (one row per observation).
  Source  : Loaded from dbo.bronze_events by silver_events.sql.
  Run     : Once, AFTER Create_silver_places.sql (foreign key dependency).

  NOTE: EONET events can have several observations (points on a track), so
        EventID is not unique in the source; the natural key is
        (EventID, EventDate). The UNIQUE constraint on EventID below is kept
        as originally written, but it will reject events with more than one
        observation. See the note at the constraint.
*******************************************************************************/

USE [NasaEvents];
GO

SET ANSI_NULLS ON;
GO

SET QUOTED_IDENTIFIER ON;
GO

CREATE TABLE [dbo].[silver_events]
(
    -- Keys
    [ObservationGuid] UNIQUEIDENTIFIER NOT NULL,   -- deterministic hash of EventID + EventDate
    [EventID]         NVARCHAR(50)     NOT NULL,   -- EONET event id

    -- Descriptive columns
    [Title]           NVARCHAR(500)    NULL,
    [EventDate]       DATETIME2(7)     NOT NULL,   -- UTC, timezone removed
    [MagnitudeValue]  FLOAT            NULL,
    [MagnitudeUnit]   NVARCHAR(50)     NULL,
    [GeometryType]    NVARCHAR(50)     NULL,
    [categoryId]      NVARCHAR(50)     NULL,

    -- Location
    [Lon]             FLOAT            NULL,
    [Lat]             FLOAT            NULL,
    [PlaceID]         INT              NULL,

    -- Primary key is nonclustered so the clustered index can sit on EventID.
    CONSTRAINT [PK_silver_events]
        PRIMARY KEY NONCLUSTERED ([ObservationGuid]),

    -- TODO: this prevents multiple observations per event. Consider replacing
    --       it with a clustered UNIQUE (EventID, EventDate).
    CONSTRAINT [UQ_silver_events_EventID]
        UNIQUE CLUSTERED ([EventID]),

    CONSTRAINT [FK_silver_events_places]
        FOREIGN KEY ([PlaceID]) REFERENCES [dbo].[silver_places] ([PlaceID])
);
GO
