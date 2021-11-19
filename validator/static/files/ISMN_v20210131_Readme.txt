Variables stored in separate files (CEOP formatted)

Filename
	
	Data_separate_files_startdate(YYYYMMDD)_enddate(YYYYMMDD).zip

	e.g., Data_separate_files_20050316_20050601.zip

	
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

	CHINA
		Abstract: Soil moisture datasets for 40 stations were collected from the Institute of Geographical Sciences and Natural Resources Research at the Chinese Academy of Sciences. The soil moisture observations were taken using the gravimetric technique and were converted to total soil moisture [cm]. After downloading the measurements from Alan Robock"s "Global Soil Moisture Database" the data was converted into volumetric soil moisture [m^3/m^3]. The dataset provides observations three times a month from 1981 to 1991 in 11 different layers.
		Continent: Asia
		Country: China
		Stations: 40
		Status: inactive
		Data Range: from 1981-01-08 to 1999-12-28
		Type: project
		Url: 
		Reference: Liu S., Mo X, Li H., Peng G., Robock A. 2001  The spatial variation of soil moisture in China:Geostatistical Characteristics. Journal of the Meteorological Society of Japan , 79 (2B) 555-574; Robock, Alan, Konstantin Y. Vinnikov, Govindarajalu Srinivasan, Jared K. Entin, Steven E. Hollinger, Nina A. Speranskaya, Suxia Liu, and A. Namkhai, 2000: The Global Soil Moisture Data Bank. Bull. Amer. Meteorol. Soc., 81, 1281-1299
		Variables: soil moisture, 
		Soil Moisture Depths: 0.00 - 0.05 m , 0.05 - 0.10 m , 0.10 - 0.20 m , 0.20 - 0.30 m , 0.30 - 0.40 m , 0.40 - 0.50 m , 0.50 - 0.60 m , 0.60 - 0.70 m , 0.70 - 0.80 m , 0.80 - 0.90 m , 0.90 - 1.00 m , 
		Soil Moisture Sensors: Coring device-auger, 

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
		Variables: soil temperature, soil moisture, 
		Soil Moisture Depths: 0.00 - 0.05 m , 0.10 - 0.10 m , 0.20 - 0.20 m , 0.40 - 0.40 m , 
		Soil Moisture Sensors: EC-TM, 5TM, 

	HiWATER_EHWSN
		Abstract: The HiWATER EHWSN network is located at farmland in the middle stream of the Heihe River Basin, China. It consists of stations 174.  The datasets are  available from April 2012 till  September 2012 and are collected by the Cold and Arid Regions Environmental and Engineering Research Institute (CAREERI), Chineses Academy of Science (CAS).
		Continent: Asia
		Country: China
		Stations: 174
		Status: inactive
		Data Range: from 2012-05-12 to 2012-09-20
		Type: campaign
		Url: http://www.westgis.ac.cn/
		Reference: 1. Jian Kang, Xin Li, Rui Jin, Yong Ge, Jinfeng Wang and Jianghao Wang. Hybrid optimal design of the eco-hydrological wireless sensor network in the middle reach of the Heihe River Basin, China, Sensors, 2014, 14(10): 19095~19114 ;    ,  2. Rui Jin, Xin Li, Baoping Yan, Xiuhong Li, Wanmin Luo, Mingguo Ma, Jianwen Guo, Jian Kang, Zhongli Zhu and Shaojie Zhao. A nested ecohydrological wireless sensor network for capturing the surface heterogeneity in the midstream areas of the Heihe River Basin, China，IEEE Geoscience and Remote Sensing Letters, 2014, 11(11): 2015~2019
		Variables: soil temperature, soil moisture, 
		Soil Moisture Depths: 0.04 - 0.04 m , 0.10 - 0.10 m , 0.20 - 0.20 m , 0.40 - 0.40 m , 
		Soil Moisture Sensors: FM100, Hydraprobe II, SPADE Time Domain Transmissivity, 

	HSC_SEOLMACHEON
		Abstract: 
		Continent: Asia
		Country: Korea
		Stations: 1
		Status: running
		Data Range: from 2008-01-01
		Type: project
		Url: http://www.hsc.re.kr
		Reference: Yeon gil Lee / Minha Choi
		Variables: soil moisture, 
		Soil Moisture Depths: 0.00 - 0.10 m , 
		Soil Moisture Sensors: Hydraprobe Analog (CR800), 

	IIT_KANPUR
		Abstract: The station called AIRSTRIP and located in thenord-center of India provide Soil Moisture datasets at 4 depths. This station is operated by the Indian Institute of Technology Kanpur.
		Continent: Asia
		Country: India
		Stations: 1
		Status: running
		Data Range: from 2011-06-16
		Type: project
		Url: http://www.iitk.ac.in/
		Reference: Tripathi, Shivam 
		Variables: soil moisture, 
		Soil Moisture Depths: 0.10 - 0.10 m , 0.25 - 0.25 m , 0.50 - 0.50 m , 0.80 - 0.80 m , 
		Soil Moisture Sensors: WaterScout SM100, 

	KHOREZM
		Abstract: 
		Continent: Asia
		Country: Uzbekistan
		Stations: 7
		Status: inactive
		Data Range: from 2010-01-01 to 2011-12-31
		Type: project
		Url: 
		Reference: 
		Variables: air temperature, soil moisture, soil temperature, surface temperature, 
		Soil Moisture Depths: 0.00 - 0.05 m , 
		Soil Moisture Sensors: ThetaProbe ML2X, 

	KIHS_CMC
		Abstract: 
		Continent: Asia
		Country: Korea
		Stations: 18
		Status: running
		Data Range: from 2019-03-20
		Type: project
		Url: http://kihs.re.kr
		Reference: 
		Variables: soil moisture, 
		Soil Moisture Depths: 0.10 - 0.10 m , 0.30 - 0.30 m , 0.40 - 0.40 m , 0.50 - 0.50 m , 0.60 - 0.60 m , 0.90 - 0.90 m , 
		Soil Moisture Sensors: Buriable Waveguide, 

	KIHS_SMC
		Abstract: 
		Continent: Asia
		Country: Korea
		Stations: 19
		Status: running
		Data Range: from 2019-03-21
		Type: campaign
		Url: http://kihs.re.kr
		Reference: 
		Variables: soil moisture, 
		Soil Moisture Depths: 0.10 - 0.10 m , 0.20 - 0.20 m , 0.30 - 0.30 m , 0.40 - 0.40 m , 0.50 - 0.50 m , 0.60 - 0.60 m , 
		Soil Moisture Sensors: Buriable Waveguide, 

	MAQU
		Abstract: The MAQU network consist of 20 stations located at the eastern edge of the Tibetan Plateau in Central China at an altitude of more than 3000 m .a.s.l. The stations are operated by University of Twente, Faculty of Geo-Information Science and  Earth Observation (ITC), and the Chinese Academy of Science - Cold and Arid Regions Environmental and Engineering Research Institute (CAS-CAREERI). The soil moisture datasets were kindly provided by Laura Dente and Bob Su from the ITC and J. Wen of the CAS.
		Continent: Asia
		Country: China
		Stations: 20
		Status: running
		Data Range: from 2008-07-01
		Type: project
		Url: 
		Reference: Su, Z., Wen, J., Dente, L., van der Velde, R., Wang, L., Ma, Y., Yang, K., and Hu, Z. 2011, The Tibetan Plateau observatory of plateau scale soil moisture and soil temperature (Tibet-Obs) for quantifying uncertainties in coarse resolution satellite and model products, Hydrol. Earth Syst. Sci., 15, 2303–2316, 2011
		Variables: soil moisture, soil temperature, 
		Soil Moisture Depths: 0.05 - 0.05 m , 
		Soil Moisture Sensors: ECH20 EC-TM, 

	MONGOLIA
		Abstract: Soil moisture datasets for 44 stations were collected by the National Agency of Meterology, Hydrology and Environment Monitoring in Ulaanbaatar. All observations were taken using the gravimetric technique and initially provided as volumetric plant-available water [%]. Volumetric soil moisture [m^3/m^3] was calculated by first extracting texture properties of all sites from the Harmonized World Soil Database and subsequently calculating the wilting levels for all stations using the equations of Saxton and Rawls (2006). 
Soil moisture measurements are provided three times a month from 1964 to 2002 during the warm period of the year, which runs from April until the end of October.
		Continent: Asia
		Country: Mongolia
		Stations: 44
		Status: inactive
		Data Range: from 1964-04-08 to 2002-10-28
		Type: project
		Url: 
		Reference: Robock, Alan, Konstantin Y. Vinnikov, Govindarajalu Srinivasan, Jared K. Entin, Steven E. Hollinger, Nina A. Speranskaya, Suxia Liu, and A. Namkhai, 2000: The Global Soil Moisture Data Bank. Bull. Amer. Meteorol. Soc., 81, 1281-1299

		Variables: soil moisture, 
		Soil Moisture Depths: 0.00 - 0.10 m , 0.10 - 0.20 m , 0.20 - 0.30 m , 0.30 - 0.40 m , 0.40 - 0.50 m , 0.50 - 0.60 m , 0.60 - 0.70 m , 0.70 - 0.80 m , 0.80 - 0.90 m , 0.90 - 1.00 m , 
		Soil Moisture Sensors: Coring device-auger, 

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

	RUSWET-AGRO
		Abstract: Soil moisture datasets for 78 districts have been prepared by Vladimir Zabelin from the Russian Hydrometeorological Center, Moscow, Russia. The soil moisture observations were taken using the gravimetric technique and were provided as volumetric plant-available water [%] for the upper 20 cm and 1 m soil layers at agricultural fields. Thus volumetric soil moisture [m^3/m^3] was calculated by first extracting texture properties of all sites from the Harmonized World Soil Database and subsequently calculating the wilting levels for all stations using the equations of Saxton and Rawls (2006).
As this dataset was designed for monitoring of soil moisture at agricultural fields datasets were seperately available for spring cereal crops and winter cereal crops for all locations. In the ISMN stations with the suffix "a" represent spring cereal crops while stations with "b" illustrate winter cereal crops. Measurements are available during the growing period from 1987 to 1988, three times a month.
		Continent: Asia
		Country: Former Soviet Union
		Stations: 212
		Status: inactive
		Data Range: from 1986-12-28 to 1988-12-28
		Type: project
		Url: 
		Reference: Robock, Alan, Konstantin Y. Vinnikov, Govindarajalu Srinivasan, Jared K. Entin, Steven E. Hollinger, Nina A. Speranskaya, Suxia Liu, and A. Namkhai, 2000: The Global Soil Moisture Data Bank. Bull. Amer. Meteorol. Soc., 81, 1281-1299

		Variables: soil moisture, 
		Soil Moisture Depths: 0.00 - 0.20 m , 0.00 - 1.00 m , 
		Soil Moisture Sensors: n.s., 

	RUSWET-GRASS
		Abstract: This network combines the two datasets RUSWET-GRASS-50STA and RUSWET-GRASS-130STA of the Global Soil Moisture Data Bank by Alan Robock and Konstantin Vinnikov. Soil moisture information at 122 meterological stations of the Former Soviet Union were collected. The results of soil moisture gravimetric measurements, which were taken at plots with natural grass type vegetation, were initially provided as volumetric plant-available water [%]. Volumetric soil moisture [m^3/m^3] was calculated by first extracting texture properties of all sites from the Harmonized World Soil Database and subsequently calculating the wilting levels for all stations using the equations of Saxton and Rawls (2006).
For the period 1952 to 1985 soil moisture measurements for the layer 0-100 cm are provided for some stations. Measurements of the upper 10 cm soil layer are available for the period 1977 to 1985.
		Continent: Asia
		Country: Former Soviet Union
		Stations: 122
		Status: inactive
		Data Range: from 1972-01-08 to 1985-12-28
		Type: project
		Url: 
		Reference: Robock, Alan, Konstantin Y. Vinnikov, Govindarajalu Srinivasan, Jared K. Entin, Steven E. Hollinger, Nina A. Speranskaya, Suxia Liu, and A. Namkhai, 2000: The Global Soil Moisture Data Bank. Bull. Amer. Meteorol. Soc., 81, 1281-1299

		Variables: soil moisture, 
		Soil Moisture Depths: 0.00 - 0.10 m , 0.00 - 1.00 m , 
		Soil Moisture Sensors: n.s., 

	RUSWET-VALDAI
		Abstract: Soil moisture datasets for 3 catchments located at the Valdai basin were collected by the State Hydrological Institute in St. Petersburg from 1960 to 1990. The catchments differ in their vegetation, Usadievskiy has mostly grassland vegetation, Tayozhniy a mature forest and Sinaya Gnilka was articifally forested in 1961. 
The soil moisture was computed by using data from 9-11 observational points distributed over the basin area. The resulting files contain monthly means of soil moisture for the layers of 0-20, 0-50 and 0-100 cm. These files were downloaded from the "Global Soil Moisture Database" and transformed into volumetric soil moisture [m^3/m^3]. Thus soil moisture values are available as monthly means, precipitation as monthly totals [mm] and temperature [°C] as daily values. Other variables measured but not included into the ISMN are runoff, averaged water table depth, averaged water equivalent snow depth and averaged evaporation.
		Continent: Asia
		Country: Former Soviet Union
		Stations: 3
		Status: inactive
		Data Range: from 1960-01-15 to 1990-12-15
		Type: project
		Url: 
		Reference: Robock, Alan, Konstantin Y. Vinnikov, Govindarajalu Srinivasan, Jared K. Entin, Steven E. Hollinger, Nina A. Speranskaya, Suxia Liu, and A. Namkhai, 2000: The Global Soil Moisture Data Bank. Bull. Amer. Meteorol. Soc., 81, 1281-1299

		Variables: air temperature, precipitation, soil moisture, soil temperature, 
		Soil Moisture Depths: 0.00 - 0.20 m , 0.00 - 0.50 m , 0.00 - 1.00 m , 
		Soil Moisture Sensors: n.s., 

	SKKU
		Abstract: 
		Continent: Asia
		Country: Korea
		Stations: 5
		Status: running
		Data Range: from 
		Type: project
		Url: 
		Reference: 
		Variables: soil moisture, 
		Soil Moisture Depths: 0.05 - 0.05 m , 0.10 - 0.10 m , 0.20 - 0.20 m , 0.40 - 0.40 m , 
		Soil Moisture Sensors: 5TM, 

	SW-WHU
		Abstract: Based on sensor web principle, this network provides continuous and high density monitoring data for soil moisture, soil temperature and meteorological conditions.
		Continent: Asia
		Country: China
		Stations: 7
		Status: running
		Data Range: from 2014-01-11
		Type: project
		Url: http://202.114.118.60:9002/SensorWebPro/index.html
		Reference: Chen, N.; Zhang,X., Wang, C.,2015. Integrated Open Geospatial Web Service enabled Cyber-physical Information Infrastructure for Precision Agriculture Monitoring. Computers and Electronics in Agriculture.111,78–91. doi:10.1016/j.compag.2014.12.009; Chen, N., Xiao, C., Pu, F., Wang, Z., Wang, C., Gong, J. 2015. Cyber-Physical Geographical Information Service-Enabled Control of Diverse In-situ Sensors. Sensors. 15(2), 2565-2592. doi: 10.3390/s150202565
		Variables: air temperature, precipitation, soil moisture, soil temperature, 
		Soil Moisture Depths: 0.10 - 0.10 m , 
		Soil Moisture Sensors: FY-H2, LVDSC12, SoilMoisture-AverageSensor, 

	VDS
		Abstract: These networks have been installed to validate satellite soil moisture products over complex tropical regions.
		Continent: Asia
		Country: Myanmar
		Stations: 4
		Status: running
		Data Range: from 2017-06-01
		Type: project
		Url: https://www.vandersat.com/
		Reference: 
		Variables: soil moisture, soil temperature, 
		Soil Moisture Depths: 0.01 - 0.10 m , 0.10 - 0.10 m , 0.20 - 0.20 m , 
		Soil Moisture Sensors: GS1 Port 1, GS1 Port 2, GS1 Port 3, GS1 Port 4, GS1 Port 5, TEROS12_SM P1, TEROS12_SM P2, TEROS12_SM P3, TEROS12_SM P4, TEROS12_SM P5, TEROS12_SM P6, 

