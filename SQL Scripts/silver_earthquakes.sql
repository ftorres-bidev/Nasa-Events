USE NasaEvents
GO

INSERT INTO silver_earthquakes  
(ID,
Magnitude, 
Place, 
EventTimeUtc, 
UpdateTimeUtc, 
Felt, 
Cdi, 
Mmi, 
Alert, 
Tsunami, 
Sig, 
Nst, 
Dmin, 
Rms, 
Gap, 
Magnitude_Type, 
Magnitude_Description,
Type, 
Lon, 
Lat, 
DepthKm, 
PlaceID)

SELECT 

UPPER(ID) as ID,
ROUND(Magnitude,2) as Magnitude,
Place,
DATEADD(MILLISECOND, EventTime % 1000,
        DATEADD(SECOND, EventTime / 1000, CAST('1970-01-01' AS DATETIME2(3)))) AS EventTimeUtc,
DATEADD(MILLISECOND, UpdateTime % 1000,
        DATEADD(SECOND, UpdateTime / 1000, CAST('1970-01-01' AS DATETIME2(3)))) AS UpdateTimeUtc,
Felt,
Cdi,
Mmi,
CASE
    WHEN Alert is null THEN 'n/a'
    ELSE Alert END AS Alert,
Tsunami,
Sig,
Nst,
Dmin,
Rms,
Gap,
MagType as Magnitute_Type,
CASE LOWER(MagType)
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
    ELSE MagType END as Magnitude_Description,
CONCAT(Upper(LEFT(Type,1)),RIGHT(Type,LEN(Type)-1)) as Type,
Lon,
Lat,
DepthKm,
PlaceID

 FROM bronze_earthquakes 
