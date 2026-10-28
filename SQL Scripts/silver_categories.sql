USE NasaEvents

INSERT INTO silver_categories (CategoryID, Title)

SELECT [CategoryID]
      ,[Title]
  FROM [NasaEvents].[dbo].[bronze_categories]
