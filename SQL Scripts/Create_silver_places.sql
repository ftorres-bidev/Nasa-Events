USE [NasaEvents]
GO

/****** Object:  Table [dbo].[[silver_places]]    Script Date: 16/10/2026 15:44:28 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[silver_places](
	[PlaceID] [int] NOT NULL,
	[PlaceName] [nvarchar](200) NOT NULL,
	[State] [nvarchar](100) NOT NULL,
	[CountryCode] [nchar](2) NOT NULL,
	[Country] [nvarchar](100) NULL,
	[Lat] [float] NULL,
	[Lon] [float] NULL,
	PRIMARY KEY ([PlaceID]))
	GO