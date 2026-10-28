USE [NasaEvents]
GO

/****** Object:  Table [dbo].[silver_categories]    Script Date: 16/10/2026 15:21:13 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[silver_categories](
	[CategoryID] [varchar](50) NOT NULL,
	[Title] [varchar](50) NULL,
	PRIMARY KEY ([CategoryID])
) 

