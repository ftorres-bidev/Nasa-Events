/*******************************************************************************
  silver_categories.sql
  Purpose : Copies the category lookup from bronze to silver.
  Note    : Plain INSERT, so run it against an empty silver_categories table
            (re-running would fail on the primary key).
*******************************************************************************/

USE [NasaEvents];
GO

INSERT INTO [dbo].[silver_categories] ([CategoryID], [Title])
SELECT
    [CategoryID],
    [Title]
FROM [dbo].[bronze_categories];
GO
