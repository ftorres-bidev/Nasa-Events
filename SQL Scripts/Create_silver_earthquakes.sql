USE [NasaEvents]
GO

/****** Object:  Table [dbo].[silver_earthquakes]    Script Date: 16/10/2026 15:04:48 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[silver_earthquakes](
	[ID] [varchar](250) NOT NULL,
	[Magnitude] [float] NULL,
	[Place] [varchar](max) NULL,
	[EventTimeUtc] [DateTime] NULL,
	[UpdateTimeUtc] [DateTime] NULL,
	[Felt] [float] NULL,
	[Cdi] [float] NULL,
	[Mmi] [float] NULL,
	[Alert] [varchar](max) NULL,
	[Tsunami] [bigint] NULL,
	[Sig] [bigint] NULL,
	[Nst] [float] NULL,
	[Dmin] [float] NULL,
	[Rms] [float] NULL,
	[Gap] [float] NULL,
	[Magnitude_Type] [varchar](max) NULL,
	[Magnitude_Description] [varchar](max) NULL,
	[Type] [varchar](max) NULL,
	[Lon] [float] NULL,
	[Lat] [float] NULL,
	[DepthKm] [float] NULL,
	[PlaceID] [int] NULL,
	PRIMARY KEY ([ID])
) 
GO



