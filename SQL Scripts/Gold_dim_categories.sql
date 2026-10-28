/*******************************************************************************
  Gold_dim_categories.sql
  Purpose : Gold-layer category dimension, exposed as a view over silver.
  Note    : CREATE VIEW must be the first statement in its batch, hence the GO
            after USE. Columns are listed explicitly so later changes to
            silver_categories do not silently change the gold contract.
*******************************************************************************/

USE [NasaEvents];
GO

CREATE VIEW [dbo].[Gold_dim_categories]
AS
SELECT
    [CategoryID],
    [Title]
FROM [dbo].[silver_categories];
GO
