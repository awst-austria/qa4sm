Variables stored in separate files (CEOP formatted)

Filename
	
	Data_seperate_files_startdate(YYYYMMDD)_enddate(YYYYMMDD).zip

	e.g., Data_seperate_files_20050316_20050601.zip

	
Folder structure

	Networkname
		Stationname

		
Dataset Filename

	CSE_Network_Station_Variablename_depthfrom_depthto_startdate_enddate.ext

	CSE	- Continental Scale Experiment (CSE) acronym, if not applicable use Networkname
	Network	- Network abbreviation (e.g., OZNET)
	Station	- Station name (e.g., Widgiewa)
	Variablename - Name of the variable in the file (e.g., Soil-Moisture)
	depthfrom - Depth in the ground in which the variable was observed (upper boundary)
	depthto	- Depth in the ground in which the variable was observed (lower boundary)
	startdate -	Date of the first dataset in the file (format YYYYMMDD)
	enddate	- Date of the last dataset in the file (format YYYYMMDD)
	ext	- Extension .stm (Soil Temperature and Soil Moisture Data Set see CEOP standard)

	e.g., OZNET_OZNET_Widgiewa_Soil-Temperature_0.150000_0.150000_20010103_20090812.stm

	
File Content Sample

	2003/12/11 00:30 2003/12/11 00:40 OZNET      OZNET           Widgiewa         -35.09000   146.30600  121.00    0.15    0.15    28.30  U M

	UTC nominal date/time - yyyy/mm/dd HH:MM, where MM is 00 or 30, only
	UTC actual date/time - yyyy/mm/dd HH:MM
	CSE Identifier - Continental Scale Experiment (CSE) acronym, if not applicable use Networkname
	Network	- Network abbreviation (e.g., OZNET)
	Station	- Station name (e.g., Widgiewa)
	Latitude - Decimal degrees. South is negative. 
	Longitude -	Decimal degrees. West is negative.
	Elevation -	Meters above sea level
	Depth from - Depth in the ground in which the variable was observed (upper boundary)
	Depth to - Depth in the ground in which the variable was observed (lower boundary)
	Variable value
	ISMN Quality Flag
	Data Provider Quality Flag, if existing
	

For Definition of the CEOP Data Format see http://www.eol.ucar.edu/projects/ceop/dm/documents/refdata_report/ceop_soils_format.html


Network Information

	AMMA-CATCH
		Abstract: This network consists of three supersites in Benin, Niger and Mali. Mali works operational since 2005, Niger and Benin since 2006. Several measurements in Mali and Niger are taken at the same station with the same sensor type in the same depth. They are located at the bottom (sensor CS616_1), middle (CS616_2) or top (CS616_3) of dune slopes (Mali) or from a plateau to the valley bottom (Niger).
		Continent: Africa
		Country: Benin, Niger, Mali
		Stations: 7
		Status: running
		Data Range: from 2005-01-01
		Type: project
		Url: http://www.amma-catch.org
		Reference: Pellarin T., J.P. Laurent, B. Cappelaere, B. Decharme, L. Descroix, D. Ramier, 2009 : Hydrological modelling and associated microwave emission of a semi-arid region in South-western Niger, /Journal of Hydrology/, vol. 375, 1-2, 262-272, 2009; , 
Mougin, E., Hiernaux, P., Kergoat, L., Grippa, M., de Rosnay, P., Timouk, F., Le Dantec, V., Demarez, V., Lavenu, F., Arjounin, M., Lebel, T. et al., 2009. The AMMA-CATCH Gourma observatory site in Mali: Relating climatic variations to changes in vegetation, surface in press, hydrology, fluxes and natural resources. Journal of Hydrology, 375(1-2): 14-33; , 
Cappelaere, C., Descroix, L., Lebel, T., Boulain, N., Ramier, D., Laurent, J.-P., Le Breton, E., Boubkraoui, S., Bouzou Moussa, I. et al., 2009. The AMMA Catch observing system in the cultivated Sahel of South West Niger- Strategy, Implementation and Site conditions, 2009. Journal of Hydrology, 375(1-2): 34-51; , 
de Rosnay, P., Gruhier, C., Timouk, F., Baup, F., Mougin, E., Hiernaux, P., Kergoat, L., and LeDantec, V.: Multi-scale soil moisture measurements at the Gourma meso-scale site in Mali, Journal of Hydrology, 375, 241-252, 2009;,  Lebel, Thierry, Cappelaere, Bernard, Galle, Sylvie, Hanan, Niall, Kergoat, Laurent, Levis, Samuel, Vieux, Baxter, Descroix, Luc, Gosset, Marielle, Mougin, Eric, Peugeot, Christophe and Seguis, Luc, 2009: AMMA-CATCH studies in the Sahelian region of West-Africa: An overview. JOURNAL OF HYDROLOGY, 375, 3-13.
		Variables: soil moisture, 
		Soil Moisture Depths: 0.05 - 0.05 m , 0.10 - 0.10 m , 0.10 - 0.40 m , 0.20 - 0.20 m , 0.40 - 0.40 m , 0.40 - 0.70 m , 0.60 - 0.60 m , 0.70 - 1.00 m , 1.00 - 1.00 m , 1.00 - 1.30 m , 1.05 - 1.35 m , 1.20 - 1.20 m , 
		Soil Moisture Sensors: CS616, 

	BIEBRZA_S-1
		Abstract: Preparation of the method for determining biomass and soil moisture changes on the basis of data delivered by recent satellite missions
		Continent: Europe
		Country: Poland
		Stations: 30
		Status: running
		Data Range: from 2015-09-15
		Type: project
		Url: http://www.igik.edu.pl/en
		Reference: 
		Variables: soil moisture, soil temperature, precipitation, air temperature, 
		Soil Moisture Depths: 0.05 - 0.05 m , 0.10 - 0.10 m , 0.20 - 0.20 m , 0.50 - 0.50 m , 
		Soil Moisture Sensors: GS-3, 

	BNZ-LTER
		Abstract: The Bonanza Creek (BNZ) LTER project was initiated in 1987 and since then has provided experimental and observational research designed to understand the dynamics, resilience, and vulnerability of Alaska's boreal forest ecosystems. The project has illuminated the responses of boreal forest organisms and ecosystems to climate and various atmospheric inputs, focusing on forest and landscape dynamics and biogeochemistry. This project will continue that long-term line of research, expanding it to broaden the landscape under study, broaden the predictive realm of the resulting information, and to directly address the resilience of socio-economic systems. The project hypothesizes that the past observed high resilience of boreal ecosystems to interannual and decadal changes in environmental conditions is approaching a critical tipping point., 
This project contributes to understanding of the structure, function, and dynamics of boreal forest ecosystems and the broader boreal landscape, including the human communities. It assembles and integrates valuable long-term data sets on climate, hydrology, biology, ecology, and biogeochemical and geomorphic processes, as incorporates emerging data types, including molecular and social science data and digital images. The project has broad societal value through its contributions to knowledge that can inform management of boreal forest ecosystems and sustainability of subsistence communities. Its broader values also include extensive research-based training and educational program development. Its strong public outreach program includes collaborations between artists and scientists and strong linkages with Native organizations.
		Continent: North_America
		Country: Alaska
		Stations: 12
		Status: running
		Data Range: from 1989-05-01 to 2012-12-31
		Type: project
		Url: http://www.lter.uaf.edu/
		Reference: Van Cleve, Keith; Chapin, F.S. Stuart; Ruess, Roger W. 2015. Bonanza Creek Long Term Ecological Research Project Climate Database - University of Alaska Fairbanks.; ,  Bonanza Creek Long Term Ecological Research Project Climate Database. 2015. University of Alaska Fairbanks.
		Variables: snow water equivalent, soil moisture, soil temperature, precipitation, air temperature, snow depth, surface temperature, 
		Soil Moisture Depths: 0.05 - 0.05 m , 0.10 - 0.10 m , 0.20 - 0.20 m , 0.50 - 0.50 m , 
		Soil Moisture Sensors: CS615, 

	CARBOAFRICA
		Abstract: Meteorological data and soil data have been collected at a site in the central Sudan from 2002 to 2012. The site is a sparse savanna in the semiarid region of Sudan. In addition to basic meteorological variables, soil properties (temperature, water content, and heat flux) and radiation (global radiation, net radiation, and photosynthetic active radiation) were measured. The dataset has a temporal resolution of 30 minutes and provides general data for calibration and validation of ecosystem models and remote-sensing-based assessments, and it is relevant for studies of ecosystem properties and processes.
		Continent: Africa
		Country: Sudan
		Stations: 1
		Status: running
		Data Range: from 2002-02-08
		Type: project
		Url: http://dx.doi.org/10.7167/2013/297973
		Reference: Jonas Ardö, A 10-Year Dataset of Basic Meteorology and Soil Properties in Central Sudan, Dataset Papers in Geosciences, vol. 2013, Article ID 297973, 6 pages, 2013
		Variables: soil moisture, soil temperature, precipitation, air temperature, 
		Soil Moisture Depths: 0.05 - 0.05 m , 0.15 - 0.15 m , 0.30 - 0.30 m , 0.60 - 0.60 m , 1.00 - 1.00 m , 1.50 - 1.50 m , 2.00 - 2.00 m , 
		Soil Moisture Sensors: CS616, CS615, 

	COSMOS
		Abstract: A new project to measure soil moisture using a cosmic-ray technique. Currently, there are 67 stations deployed in 7 countries, which 59 are in USA, 1 in Germany, 1 in Switzerland, 1 in France, 1 in Brasil, 2 in Kenya, 1 in United Kingdom and 1 in Mexico.
		Continent: North_America
		Country: USA
		Stations: 109
		Status: running
		Data Range: from 2008-04-28
		Type: project
		Url: http://cosmos.hwr.arizona.edu/
		Reference: Zreda M., Desilets D., Ferré Ty P.A., Scott R.L., “Measuring soil moisture content non-invasively at intermediate spatial scale using cosmic-ray neutrons”, Geophysical Research Letters 35(21), 2008. ,   Zreda, M., W.J. Shuttleworth, X. Zeng, C. Zweck, D. Desilets, T. Franz, and R. Rosolem, 2012. COSMOS: the COsmic-ray Soil Moisture Observing System. Hydrology and Earth System Sciences 16, 4079-4099, doi: 10.5194/hess-16-4079-2012. 
		Variables: soil moisture, 
		Soil Moisture Depths: 0.00 - 0.04 m , 0.00 - 0.05 m , 0.00 - 0.06 m , 0.00 - 0.07 m , 0.00 - 0.08 m , 0.00 - 0.09 m , 0.00 - 0.10 m , 0.00 - 0.11 m , 0.00 - 0.12 m , 0.00 - 0.13 m , 0.00 - 0.14 m , 0.00 - 0.15 m , 0.00 - 0.16 m , 0.00 - 0.17 m , 0.00 - 0.18 m , 0.00 - 0.19 m , 0.00 - 0.20 m , 0.00 - 0.21 m , 0.00 - 0.22 m , 0.00 - 0.23 m , 0.00 - 0.24 m , 0.00 - 0.25 m , 0.00 - 0.26 m , 0.00 - 0.27 m , 0.00 - 0.28 m , 0.00 - 0.29 m , 0.00 - 0.30 m , 0.00 - 0.31 m , 0.00 - 0.32 m , 0.00 - 0.33 m , 0.00 - 0.34 m , 0.00 - 0.36 m , 0.00 - 0.37 m , 0.00 - 0.38 m , 0.00 - 0.39 m , 0.00 - 0.40 m , 0.00 - 0.41 m , 0.00 - 0.44 m , 0.00 - 0.55 m , 0.00 - 0.69 m , 0.00 - 0.90 m , 
		Soil Moisture Sensors: Cosmic-ray Probe, 

	CTP_SMTMN
		Abstract: A dense monitoring network that consists of 56 stations is established on the central Tibetan Plateau to measure two state variables (soil moisture and temperature) at three spatial scales (1.0, 0.3, 0.1 degree) and four soil depths (0~5, 10, 20, and 40 cm). Elevations of these stations vary over 4470~4950 m. The experimental area is characterized by low biomass, high soil moisture dynamic range, and typical freeze-thaw cycle. As auxiliary parameters of this network, soil texture and soil organic carbon content are measured at each station to support further studies. All the sensors have been calibrated by taking account of the impact of soil texture and soil organic carbon content on the measurements. 
As the highest soil moisture network above sea level in the world, this network meets the requirement for evaluating a variety of soil moisture products and for soil moisture scaling analyses. 
Note that, 
a)	some of the stations are shared by two or three sub-scale networks (indicated by the station names) and thus the number of station names is up to 69 in total; 
b)	in order to ensure the continuous measurements of the near surface (0~5 cm) SM/TM, the original surface layer sensor (when get damaged) is usually replaced with another sensor at deeper depth during field maintenance. Therefore there may be offset in a time series before and after the replacing time point (shown in Table 1). 
Table 1. Sensor replacing/exchanging time points at specific stations. 
Station_Name	0-0.05 m	0.40 m
M19	        10/13/2012	
L01	          6/14/2012	  6/14/2012
L07_M13	  6/15/2012	  6/15/2012
L35	        10/15/2012	10/15/2012
M03	        10/13/2012	10/13/2012
M07_S01	10/13/2012	10/13/2012

		Continent: Asia
		Country: China
		Stations: 57
		Status: running
		Data Range: from 2007-07-01
		Type: project
		Url: http://dam.itpcas.ac.cn/rs/?q=data#CTP-SMTMN
		Reference: Yang, K., J. Qin, L. Zhao, Y. Y. Chen, W. J. Tang, M. L. Han, Lazhu, Z. Q. Chen, N. Lv, B. H. Ding, H. Wu, C. G. Lin, 2013. A Multi-Scale Soil Moisture and Freeze-Thaw Monitoring Network on the Third Pole, Bulletin of the American Meteorological Society, doi: 10.1175/BAMS-D-12-00203.1
		Variables: soil moisture, soil temperature, 
		Soil Moisture Depths: 0.00 - 0.05 m , 0.10 - 0.10 m , 0.20 - 0.20 m , 0.40 - 0.40 m , 
		Soil Moisture Sensors: 5TM, EC-TM, 

	DAHRA
		Abstract: Earth Observation of long term changes in land surface moisture conditions
		Continent: Africa
		Country: Senegal
		Stations: 1
		Status: running
		Data Range: from 2002-07-04
		Type: project
		Url: http://ign.ku.dk/earthobservation/research/document4/CaLM/
		Reference: Tagesson T, Fensholt R, Guiro I et al. (2014) Ecosystem properties of semi-arid savanna grassland in West Africa and its relationship to environmental variability. Global Change Biology, (accepted).
		Variables: soil moisture, soil temperature, precipitation, air temperature, 
		Soil Moisture Depths: 0.05 - 0.05 m , 0.10 - 0.10 m , 0.30 - 0.30 m , 0.50 - 0.50 m , 1.00 - 1.00 m , 
		Soil Moisture Sensors: ThetaProbe ML2X, 

	FLUXNET-AMERIFLUX
		Abstract: Datasets of 2 stations near the city of Sacramento are provided. They are managed by Dennis D. Baldocchi, University of California, Berkeley. 
		Continent: North_America
		Country: USA
		Stations: 2
		Status: running
		Data Range: from 2000-10-22
		Type: project
		Url: http://ameriflux.lbl.gov/
		Reference: 
		Variables: soil moisture, soil temperature, precipitation, air temperature, 
		Soil Moisture Depths: 0.00 - 0.00 m , 0.00 - 0.15 m , 0.10 - 0.10 m , 0.15 - 0.30 m , 0.20 - 0.20 m , 0.30 - 0.45 m , 0.45 - 0.60 m , 0.50 - 0.50 m , 
		Soil Moisture Sensors: Moisture Point PRB-K, ThetaProbe ML2X, 

	FMI
		Abstract: The finnish network "FMI" includes one station that contains multiple soil moisture measurements in 2cm and 10cm depth, taken only a few meters next to each other. Additionaly air temperature is measured in 2m height and soil temperature in 2cm depth. The datasets start at 2007-01-25 and are updated once a day. The FMI is the first network that has been implemented with data updates in Near Real Time.
		Continent: Europe
		Country: Finland
		Stations: 27
		Status: running
		Data Range: from 2007-01-25
		Type: project
		Url: http://fmiarc.fmi.fi/
		Reference: 
		Variables: soil moisture, soil temperature, air temperature, 
		Soil Moisture Depths: 0.02 - 0.02 m , 0.05 - 0.05 m , 0.10 - 0.10 m , 0.20 - 0.20 m , 0.40 - 0.40 m , 0.60 - 0.60 m , 0.80 - 0.80 m , 
		Soil Moisture Sensors: 5TE, ThetaProbe ML2X, CS655, 

	FR_Aqui
		Abstract: The Fr_Aqui network is located in France and hosted by the Institue of Agricultural Research (INRA); it consists of 5 stations with soil moisture and soil temperature measurements in 6 different  depths.
		Continent: Europe
		Country: France
		Stations: 5
		Status: running
		Data Range: from 2010-01-01
		Type: meteo
		Url: 
		Reference: 
		Variables: soil moisture, soil temperature, 
		Soil Moisture Depths: 0.01 - 0.01 m , 0.03 - 0.03 m , 0.05 - 0.05 m , 0.10 - 0.10 m , 0.15 - 0.15 m , 0.20 - 0.20 m , 0.21 - 0.21 m , 0.30 - 0.30 m , 0.34 - 0.34 m , 0.45 - 0.45 m , 0.50 - 0.50 m , 0.55 - 0.55 m , 0.56 - 0.56 m , 0.70 - 0.70 m , 0.80 - 0.80 m , 0.90 - 0.90 m , 
		Soil Moisture Sensors: ThetaProbe ML2X, 

	HOBE
		Abstract: Soil moisture and soil temperature network with 30 stations within the area of major signal contribution of one selected SMOS grid node in the Skjern River Catchment
		Continent: Europe
		Country: Denmark
		Stations: 32
		Status: running
		Data Range: from 2009-09-08
		Type: project
		Url: http://www.hobe.dk/
		Reference: Bircher, S., Skou, N., Jensen, K.H., Walker, J.P., and Rasmussen, L. (2011): A soil moisture and temperature network for SMOS validation in Western Denmark. Hydrology and Earth System Sciences Discussions, 8, 9961-10006, doi:10.5194/hessd-8-9961
		Variables: soil moisture, soil temperature, 
		Soil Moisture Depths: 0.00 - 0.05 m , 0.20 - 0.25 m , 0.50 - 0.55 m , 
		Soil Moisture Sensors: Decagon 5TE, 

	iRON
		Abstract: 
		Continent: North_America
		Country: USA
		Stations: 9
		Status: running
		Data Range: from 2012-06-07
		Type: meteo
		Url: https://agci.org/iron
		Reference: 
		Variables: soil moisture, soil temperature, precipitation, air temperature, 
		Soil Moisture Depths: 0.05 - 0.05 m , 0.20 - 0.20 m , 0.51 - 0.51 m , 1.00 - 1.00 m , 
		Soil Moisture Sensors: 10HS, EC5 II, EC5 I, EC5, 

	LAB-net
		Abstract: In Chile, remote sensing applications related to soil moisture and evapotranspiration estimates have increased during the last decades because of the drought and the water use conflicts which generate a strong interest on water demand. To address these problems on water balance in large scales by using remote sensing imagery, LAB-net was created as the first soil moisture network located in Chile over four different land cover types. These land cover types are vineyard and olive orchards located in a semi-arid region of Copiapó Valley, a well irrigated raspberry crop located in the central zone of of Tinguiririca Valley and a green grass rangeland located Austral zone of Chile. Over each site, a well implemented meteorological station is continuously measuring a 5 minute intervals above the following parameters: soil moisture and temperature at two ground levels (5 and 20 cm), air temperature and relative humidity, net radiation, global radiation, brightness surface temperature (8 – 14 µm), rainfall and ground fluxes. This is the first approach of an integrated soil moisture network in Chile. The data generated by this network is freely available for any research or scientific purpose related to current and future soil moisture satellite missions.    

		Continent: South_America
		Country: Chile
		Stations: 3
		Status: running
		Data Range: from 2014-07-18
		Type: meteo
		Url: http://www.biosfera.uchile.cl/LAB-net.html

		Reference: Mattar, C., Santamaría-Artigas, A., Durán-Alarcón, C., Olivera-Guerra, L and Fuster, R. 2014. LAB-net the First Chilean soil moisture network for Remote Sensing Applications. Procd. IV Recent Advances in Quantitative Remote Sensing Symposium (RAQRS). 22 - 25 September, Valencia, Spain.

		Variables: soil moisture, soil temperature, precipitation, air temperature, 
		Soil Moisture Depths: 0.07 - 0.07 m , 0.10 - 0.10 m , 0.20 - 0.20 m , 
		Soil Moisture Sensors: CS616, CS650, 

	MySMNet
		Abstract: 
		Continent: Asia
		Country: Malaysia
		Stations: 7
		Status: running
		Data Range: from 2014-06-01
		Type: project
		Url: 
		Reference: 
		Variables: soil moisture, soil temperature, 
		Soil Moisture Depths: 0.00 - 0.05 m , 0.45 - 0.50 m , 0.95 - 1.00 m , 
		Soil Moisture Sensors: WaterScout SM100, 

	OZNET
		Abstract: 
		Continent: Australia
		Country: Australia
		Stations: 38
		Status: running
		Data Range: from 2001-01-01
		Type: project
		Url: http://www.oznet.org.au/
		Reference: Smith, A. B., J. P.Walker, A. W.Western, R. I.Young, K. M.Ellett, R. C.Pipunic, R. B.Grayson, L.Siriwardena, F. H. S.Chiew, and H.Richter (2012), The Murrumbidgee soil moisture monitoring network data set, Water Resour. Res., 48, W07701, doi:10.1029/2012WR011976.  , Young, R., Walker, J., Yeoh, N., Smith, A., Ellett, K., Merlin, O. and Western, A., 2008. Soil moisture and meteorological observations from the murrumbidgee catchment. Department of Civil and Environmental Engineering, The University of Melbourne.
		Variables: soil moisture, soil suction, soil temperature, precipitation, 
		Soil Moisture Depths: 0.00 - 0.05 m , 0.00 - 0.08 m , 0.00 - 0.30 m , 0.15 - 0.25 m , 0.30 - 0.60 m , 0.57 - 0.87 m , 0.60 - 0.90 m , 
		Soil Moisture Sensors: EnviroSCAN, CS616, Stevens Hydra Probe, CS615, 

	PBO_H2O
		Abstract: The soil moisture data is measured using GPS reflections.
		Continent: North_America
		Country: USA
		Stations: 159
		Status: running
		Data Range: from 2007-01-01
		Type: project
		Url: http://xenon.colorado.edu/portal/index.php?product=soil_moisture
		Reference: Kristine M. Larson, Eric E. Small, Ethan D. Gutmann, Andria L. Bilich, John J. Braun, Valery U. Zavorotny: Use of GPS receivers as a soil moisture network for water cycle studies. GEOPHYSICAL RESEARCH LETTERS, VOL. 35, L24405, doi:10.1029/2008GL036013, 2008.
		Variables: soil moisture, precipitation, air temperature, snow depth, 
		Soil Moisture Depths: 0.00 - 0.05 m , 
		Soil Moisture Sensors: GPS, 

	REMEDHUS
		Abstract: 
		Continent: Europe
		Country: Spain
		Stations: 24
		Status: running
		Data Range: from 2005-01-01
		Type: project
		Url: http://campus.usal.es/~hidrus/
		Reference: 
		Variables: soil moisture, soil temperature, 
		Soil Moisture Depths: 0.00 - 0.05 m , 
		Soil Moisture Sensors: Stevens Hydra Probe, 

	RISMA
		Abstract: In 2010 and 2011, Agriculture and Agri-Food Canada (AAFC), with the collaboration of Environment Canada, established three in situ monitoring networks near Kenaston (Saskatchewan), Carman (Manitoba) and Casselman (Ontario) as part of the Sustainable Agriculture Environmental Systems (SAGES) project titled Earth Observation Information on Crops and Soils for Agri-Environmental Monitoring in Canada.
		Continent: North_America
		Country: Canada
		Stations: 23
		Status: running
		Data Range: from 2013-06-15
		Type: project
		Url: http://aafc.fieldvision.ca/
		Reference: Ojo, E. R., Bullock, P. R., L’Heureux, J., Powers, J., McNairn, H., & Pacheco, A. (2015). Calibration and evaluation of a frequency domain reflectometry sensor for real-time soil moisture monitoring. Vadose Zone Journal, 14(3). doi: 10.2136/vzj2014.08.0114 , 
L’Heureux, J. (2011). 2011 Installation Report for AAFC‐  SAGES Soil Moisture Stations in Kenaston,   SK. Agriculture , 
Canisius, F. (2011). Calibration of Casselman, Ontario Soil Moisture Monitoring Network, Agriculture and Agri‐Food Canada, Ottawa, ON, 37pp
		Variables: soil moisture, soil temperature, precipitation, air temperature, 
		Soil Moisture Depths: 0.00 - 0.05 m , 0.05 - 0.05 m , 0.20 - 0.20 m , 0.50 - 0.50 m , 1.00 - 1.00 m , 1.50 - 1.50 m , 
		Soil Moisture Sensors: Hydraprobe II Sdi-12, 

	RSMN
		Abstract: The project proposal aims at paving the way for the utilisation of satellite derived soil moisture products in Romania, creating the framework for the validation and evaluation of actual & future satellite microwave soil moisture derived products, demonstrating its value, and by developing the necessary expertise for successfuly approaching implementations in the Societal Benefit Areas (as they were defined in GEOSS)

		Continent: Europe
		Country: Romania
		Stations: 20
		Status: running
		Data Range: from 2014-04-09
		Type: meteo
		Url: http://assimo.meteoromania.ro
		Reference: 
		Variables: soil moisture, soil temperature, precipitation, air temperature, 
		Soil Moisture Depths: 0.00 - 0.05 m , 
		Soil Moisture Sensors: 5TM, 

	SCAN
		Abstract: Soil Climate Analysis Network contains 187 stations all over the USA including stations in Alaska, Hawaii, Puerto Rico or even one in Antarctica. Apart from soil moisture and soil temperature, also precipitation and air temperature are measured. Some stations have also additional measurements of snow depth and snow water equivalent. Almost 150 stations are updated on daily basis. The network is operated by the USDA NRCS National Water and Climate Center with assistance from the USDA NRCS National Soil Survey Center.
		Continent: North_America
		Country: USA
		Stations: 232
		Status: running
		Data Range: from 
		Type: project
		Url: http://www.wcc.nrcs.usda.gov/
		Reference: 
		Variables: snow water equivalent, soil moisture, soil temperature, precipitation, air temperature, snow depth, 
		Soil Moisture Depths: 0.02 - 0.02 m , 0.05 - 0.05 m , 0.10 - 0.10 m , 0.15 - 0.15 m , 0.20 - 0.20 m , 0.25 - 0.25 m , 0.27 - 0.27 m , 0.30 - 0.30 m , 0.38 - 0.38 m , 0.40 - 0.40 m , 0.45 - 0.45 m , 0.50 - 0.50 m , 0.60 - 0.60 m , 0.66 - 0.66 m , 0.68 - 0.68 m , 0.76 - 0.76 m , 0.83 - 0.83 m , 0.88 - 0.88 m , 1.01 - 1.01 m , 1.09 - 1.09 m , 1.14 - 1.14 m , 1.29 - 1.29 m , 1.39 - 1.39 m , 1.52 - 1.52 m , 2.03 - 2.03 m , 
		Soil Moisture Sensors: Hydraprobe Analog (5.0 Volt), n.s., Hydraprobe Digital Sdi-12 (2.5 Volt), Hydraprobe Digital Sdi-12 Thermistor (linear), Hydraprobe Analog (2.5 Volt), 

	SMOSMANIA
		Abstract: 
		Continent: Europe
		Country: France
		Stations: 22
		Status: running
		Data Range: from 2003-01-01
		Type: project
		Url: http://www.hymex.org
		Reference: Albergel, C., Rüdiger, C., Pellarin, T., Calvet, J.-C., Fritz, N., Froissard, F., Suquia, D., Petitpa, A., Piguet, B., and Martin, E.: From near-surface to 
root-zone soil moisture using an exponential filter: an assessment of the method based 
on insitu observations and model simulations, Hydrol. Earth Syst. Sci., 12, 1323–1337, 2008.
Calvet, J.-C., Fritz, N., Froissard, F., Suquia, D., Petitpa, A., and Piguet, B.: In situ soil moisture observations for the CAL/VAL of SMOS: the SMOSMANIA network, International Geoscience and Remote Sensing Symposium, IGARSS,

Barcelona, Spain, 23-28 July 2007, 1196-1199,
doi:10.1109/IGARSS.2007.4423019, 2007.
		Variables: soil moisture, soil temperature, 
		Soil Moisture Depths: 0.05 - 0.05 m , 0.10 - 0.10 m , 0.20 - 0.20 m , 0.30 - 0.30 m , 
		Soil Moisture Sensors: ThetaProbe ML2X, ThetaProbe ML3, 

	TERENO
		Abstract: Soil moisture network in Germany, There are 4 observatories: in Northeastern Germany- Lowlan Observatory coordinated by German Research Centre of Geosciences, in Harz/Central Germany-  Lowland Observatory coordinated by Helmholtz Centre for Environmental Research, in Eifel/Lower Rhine Valley- Observatory coordinated by Research Centre Juelich and in Bavarian Alps/pre-Alps- Obervatory coordinated by Karlsruhe Institute of Technology and German Center for Environmental Health
		Continent: Europe
		Country: Germany
		Stations: 5
		Status: running
		Data Range: from 
		Type: meteo
		Url: http://teodoor.icg.kfa-juelich.de/overview-de
		Reference: Zacharias, S., H.R. Bogena, L. Samaniego, M. Mauder, R. Fuß, T. Pütz, M. Frenzel, M. Schwank, C. Baessler, K. Butterbach-Bahl, O. Bens, E. Borg, A. Brauer, P. Dietrich, I. Hajnsek, G. Helle, R. Kiese, H. Kunstmann, S. Klotz, J.C. Munch, H. Papen, E. Priesack, H. P. Schmid, R. Steinbrecher, U. Rosenbaum, G. Teutsch, H. Vereecken. 2011. A Network of Terrestrial Environmental Observatories in Germany. Vadose Zone J. 10. 955–973. doi:10.2136/vzj2010.0139
		Variables: soil moisture, soil temperature, precipitation, air temperature, 
		Soil Moisture Depths: 0.05 - 0.05 m , 0.20 - 0.20 m , 0.50 - 0.50 m , 
		Soil Moisture Sensors: Hydraprobe II Sdi-12, 

	USCRN
		Abstract: Soil moisture NRT network USCRN (Climate Reference Network) in United States;the  datasets of 114 stations were collected and processed by the National Oceanicand Atmospheric Administration's National Climatic Data Center (NOAA's NCDC)
		Continent: North_America
		Country: USA
		Stations: 115
		Status: running
		Data Range: from 2009-06-09
		Type: meteo
		Url: http://www.ncdc.noaa.gov/crn/
		Reference: Bell, J. E., M. A. Palecki, C. B. Baker, W. G. Collins, J. H. Lawrimore, R. D. Leeper, M. E. Hall, J. Kochendorfer, T. P. Meyers, T. Wilson, and H. J. Diamond. 2013: U.S. Climate Reference Network soil moisture and temperature observations. J. Hydrometeorol., 14, 977-988. doi:  10.1175/JHM-D-12-0146.1
		Variables: soil moisture, soil temperature, precipitation, air temperature, surface temperature, 
		Soil Moisture Depths: 0.05 - 0.05 m , 0.10 - 0.10 m , 0.20 - 0.20 m , 0.50 - 0.50 m , 1.00 - 1.00 m , 
		Soil Moisture Sensors: Stevens Hydraprobe II Sdi-12, 

	WEGENERNET
		Abstract: 
		Continent: Europe
		Country: Austria
		Stations: 12
		Status: running
		Data Range: from 2007-01-01
		Type: project
		Url: http://www.wegenernet.org/;http://www.wegcenter.at/wegenernet
		Reference: 
		Variables: soil moisture, soil temperature, precipitation, air temperature, 
		Soil Moisture Depths: 0.20 - 0.20 m , 0.30 - 0.30 m , 
		Soil Moisture Sensors: Hydraprobe II, pF-Meter, 

	WSMN
		Abstract: The WSMN network is located in Wales, Great Britain, and consists of six stations. The datasets are collected by the Aberystwyth University and are available since September 2011.
		Continent: Europe
		Country: UK
		Stations: 8
		Status: running
		Data Range: from 2013-07-11
		Type: project
		Url: http://www.aber.ac.uk/wsmn
		Reference: 
		Variables: soil moisture, soil temperature, 
		Soil Moisture Depths: 0.02 - 0.02 m , 0.05 - 0.05 m , 0.10 - 0.10 m , 
		Soil Moisture Sensors: CS655, CS616, CS615, 

