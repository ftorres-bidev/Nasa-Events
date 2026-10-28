/*******************************************************************************
  Create_silver_categories.sql
  Purpose : Creates the silver lookup table of EONET event categories.
  Source  : Loaded from dbo.bronze_categories by silver_categories.sql.
  Run     : Once, before silver_categories.sql.
*******************************************************************************/

USE [NasaEvents];
GO

SET ANSI_NULLS ON;
GO

SET QUOTED_IDENTIFIER ON;
GO

CREATE TABLE [dbo].[silver_categories]
(
    [CategoryID] VARCHAR(50) NOT NULL,   -- EONET category id, e.g. 'wildfires'
    [Title]      VARCHAR(50) NULL,       -- display name, e.g. 'Wildfires'

    CONSTRAINT [PK_silver_categories] PRIMARY KEY ([CategoryID])
);
GO
