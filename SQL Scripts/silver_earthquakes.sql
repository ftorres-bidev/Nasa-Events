/*******************************************************************************
  silver_earthquakes.sql
  Purpose : Transforms bronze_earthquakes into silver_earthquakes.
  Changes : - ID upper-cased for consistent joins
            - Magnitude rounded to 2 decimals
            - Epoch milliseconds converted to UTC datetimes
            - Missing Alert replaced with 'n/a'
            - Magnitude type code expanded to a readable description
            - Type capitalised ('earthquake' -> 'Earthquake')
  Note    : Plain INSERT, so run it against an empty silver_earthquakes table
            (re-running would fail on the primary key).
*******************************************************************************/

USE [NasaEvents];
GO

INSERT INTO [dbo].[silver_earthquakes]
(
    [ID],
    [Magnitude],
    [Place],
    [EventTimeUtc],
    [UpdateTimeUtc],
    [Felt],
    [Cdi],
    [Mmi],
    [Alert],
    [Tsunami],
    [Sig],
    [Nst],
    [Dmin],
    [Rms],
    [Gap],
    [Magnitude_Type],
    [Magnitude_Description],
    [Type],
    [Lon],
    [Lat],
    [DepthKm],
    [PlaceID]
)
SELECT
    UPPER([ID])                                   AS [ID],
    ROUND([Magnitude], 2)                         AS [Magnitude],
    [Place],

    -- Epoch milliseconds -> datetime: add whole seconds, then the leftover ms.
    DATEADD(MILLISECOND, [EventTime] % 1000,
        DATEADD(SECOND, [EventTime] / 1000,
            CAST('1970-01-01' AS DATETIME2(3))))  AS [EventTimeUtc],
    DATEADD(MILLISECOND, [UpdateTime] % 1000,
        DATEADD(SECOND, [UpdateTime] / 1000,
            CAST('1970-01-01' AS DATETIME2(3))))  AS [UpdateTimeUtc],

    [Felt],
    [Cdi],
    [Mmi],

    -- USGS only sets Alert for significant events; make the gap explicit.
    CASE
        WHEN [Alert] IS NULL THEN 'n/a'
        ELSE [Alert]
    END                                           AS [Alert],

    [Tsunami],
    [Sig],
    [Nst],
    [Dmin],
    [Rms],
    [Gap],

    [MagType]                                     AS [Magnitude_Type],

    -- Readable name for each USGS magnitude type; unknown codes pass through.
    CASE LOWER([MagType])
        WHEN 'ml'    THEN 'Local (Richter) magnitude'
        WHEN 'md'    THEN 'Duration magnitude'
        WHEN 'mb'    THEN 'Body-wave magnitude'
        WHEN 'mb_lg' THEN 'Body-wave (Lg) magnitude'
        WHEN 'ms'    THEN 'Surface-wave magnitude'
        WHEN 'ms_20' THEN 'Surface-wave magnitude (20-second waves)'
        WHEN 'mw'    THEN 'Moment magnitude'
        WHEN 'mww'   THEN 'Moment magnitude (W-phase)'
        WHEN 'mwc'   THEN 'Moment magnitude (centroid)'
        WHEN 'mwb'   THEN 'Moment magnitude (body wave)'
        WHEN 'mwr'   THEN 'Moment magnitude (regional)'
        WHEN 'mwp'   THEN 'Moment magnitude (P-wave)'
        WHEN 'mi'    THEN 'Moment magnitude (P-wave, quick estimate)'
        WHEN 'mh'    THEN 'Non-standard or temporary magnitude'
        WHEN 'mun'   THEN 'Unknown magnitude type'
        WHEN 'ms_vx' THEN 'Surface-wave magnitude (variant)'
        ELSE [MagType]
    END                                           AS [Magnitude_Description],

    -- Capitalise the first letter only.
    CONCAT(UPPER(LEFT([Type], 1)),
           RIGHT([Type], LEN([Type]) - 1))        AS [Type],

    [Lon],
    [Lat],
    [DepthKm],
    [PlaceID]
FROM [dbo].[bronze_earthquakes];
GO
