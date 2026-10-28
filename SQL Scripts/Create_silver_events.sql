USE [NasaEvents]
GO

/****** Object:  Table [dbo].[silver_events]    Script Date: 16/10/2026 19:40:58 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[silver_events](
	[ObservationGuid] UNIQUEIDENTIFIER NOT NULL primary key nonclustered,
	[EventID] [nvarchar](50) NOT NULL unique clustered,
	[Title] [nvarchar](500) NULL,
	[EventDate] [datetime2](7) NOT NULL,
	[MagnitudeValue] [float] NULL,
	[MagnitudeUnit] [nvarchar](50) NULL,
	[GeometryType] [nvarchar](50) NULL,
	[categoryId] [nvarchar](50) NULL,
	[Lon] [float] NULL,
	[Lat] [float] NULL,
	[PlaceID] [int] NULL FOREIGN KEY REFERENCES silver_places(PlaceID),
	
)


