import datetime


class params:
  def __init__(self, label=None, value=None, source=None, source_year=None, description=None, comment=None, unit=None, type=None):
    self.label = label
    self.value = value
    self.source = source
    self.source_year = source_year
    self.description = description
    self.comment = comment
    self.unit = unit
    self.type = type
  

PARAMS = {}


def add_params(**kwargs):
    """Create a new params instance, and add it to the index."""

    PARAMS[kwargs["label"]] = params(**kwargs)

# HARDCODED
add_params(
    label = "heat_event_count_start_date",
    value = datetime.date(year=2000, month=1, day=1),
    description = "Start date for counting extreme heat events in HH&C to determine liklihood",
    type = "HARDCODED",
)
add_params(
    label = "heat_event_count_end_date",
    value =  datetime.date(year=2019, month=12, day=31),
    description = "End date for counting extreme heat events in HH&C to determine likilhood",
    type = "HARDCODED",
)
add_params(
    label = "list_excluded_tracts",
    value = [5990100, 5008900],
    description = "Tract IDs to be excluded from analysis.",
    comment = "990100 is Hoffman and Swinburne island, which are not inhabited. 8900 is a pier on Staten\
 Island and is no longer a tract in the 2020 census data.",
    type = "HARDCODED",
)
add_params(
    label = "hhc_event_count_start_date",
    value = datetime.date(year=2000, month=1, day=1),
    description = "Start date for  events in HH&C to determine liklihood",
    type = "HARDCODED",
)
add_params(
    label = "hhc_event_count_end_date",
    value = datetime.date(year=2019, month=12, day=31),
    description = "End date for  events in HH&C to determine likilhood",
    type = "HARDCODED",
)

# SETTINGS
add_params(
    label = "epsg",
    value = 2263,
    description = "Default projection for all inputs",
    type = "SETTINGS",
)
add_params(
    label = "target_year",
    value = 2024,
    comment = "All costs will be adjusted to dollars in this year using CPI index",
    type = "SETTINGS",
)
add_params(
    label = "make_plots",
    value = True,
    description = "Flag for making plots in Jupyter Notebooks.",
    comment = "Set to True to make plots, False otherwise.",
    type = "SETTINGS",
)

# PARAMS
add_params(
    label = "average coastal erosion rate_m",
    value = 0.3,
    source = "According to Coastal Erosion (nychazardmitigation.com), the average annual erosion rate\
 (short-term assessment for a 25- to 30-year period accounting for both rapid and gradual erosion) in the\
 New England area is 0.3 meters per year. link: https://nychazardmitigation.com/documentation/hazard-profiles/coastal-erosion/ ",
    source_year = "",
    description = "Average coastal erosion rate in meters.",
    comment = "According to Coastal Erosion (nychazardmitigation.com), the average annual erosion rate\
 (short-term assessment for a 25- to 30-year period accounting for both rapid and gradual erosion) in\
 the New England area is 0.3 meters per year",
     unit = "meter",
    type = "PARAMS",
)

add_params(
    label = "average_duration_CST_displacement_days",
    value = 30,
    description = "Assumed duration of displacement if flood flooded.",
    type = "PARAMS",
)
add_params(
    label = "buffer_period_power_outage_days",
    value = 2,
    description = "Number of days after the end of storm during which power outages are attributed to that storm.",
    type = "PARAMS",
)

add_params(
    label = "buffer_period_tree_servicing_days",
    value = 2,
    source = "",
    source_year = "",
    description = "Number of days after the end of storm during which tree service calls are attributed to that storm.",
    type = "PARAMS",
)

add_params(
    label = "building_floor_height_flood_threshold_ft",
    value = 1,
    description = "Threshold for flooding floor and displacing all residents.",
    type = "PARAMS",
)

add_params(
    label = "building_floor_height_ft",
    value = 10,
    description = "Assumed height of building floor in NYC.",
    comment = "Heights can vary depending on factors such as building codes and building type.",
    type = "PARAMS",
)

add_params(
    label = "cost_nyc_home_meals_per_day",
    value = 9,
    source = "Benefit-Cost Analysis Sustainment and Enhancements: Standard Economic Values Methodology Report\
 (Version 12.0) (fema.gov). Link: https://www.fema.gov/sites/default/files/documents/fema_standard-economic-values-methodology-report_2023.pdf",
    source_year = 2023,
    description = "Cost of home meals for residents in NYC.",
    unit = "USD",
    type = "PARAMS",
)

add_params(
    label = "cost_nyc_night_lodging",
    value = 257,
    source = "FY 2024 Per Diem Rates for New York | GSA. Link: https://www.gsa.gov/travel/plan-book/per-diem-rates/per-diem-rates-results?action=perdiems_report&city=&fiscal_year=2024&state=NY&zip= ",
    source_year = 2024,
    description = "Rate for lodging for displaced residence in NYC (FEMA 2016)",
    unit = "USD",
    type = "PARAMS",
)

add_params(
    label = "cost_nyc_per_diem",
    value = 79,
    source = "FY 2024 Per Diem Rates for New York | GSA. Link: https://www.gsa.gov/travel/plan-book/per-diem-rates/per-diem-rates-results?action=perdiems_report&city=&fiscal_year=2024&state=NY&zip=",
    source_year = 2024,
    description = "Per diem rate for displaced residents in NYC (FEMA 2016)",
    unit = "USD",
    type = "PARAMS",
)

add_params(
    label = "erosion_rate_Annandale_Staten_Island_ft_yr",
    value = 1.5,
    source = "Plan for Hazards - Hazard Mitigation - NYCEM. Link: https://www.nyc.gov/site/em/ready/hazard-mitigation.page",
    source_year = 2019,
    description = "Erosion rates described as 'faster than citywide average' in narrative in NYC HMP 2019.",
    unit = "Feet per year",
    type = "PARAMS",
)

add_params(
    label = "erosion_rate_Coney_Island_ft_yr",
    value = 1.3,
    source = "Plan for Hazards - Hazard Mitigation - NYCEM. Link: https://www.nyc.gov/site/em/ready/hazard-mitigation.page",
    source_year = 2019,
    description = "Erosion rates described as 1.3' per year in narrative in NYC HMP 2019.",
    unit = "Feet per year",
    type = "PARAMS",
)

add_params(
    label = "erosion_rate_Oakwood_Beach_Staten_Island_ft_yr",
    value = 1.5,
    source = "Plan for Hazards - Hazard Mitigation - NYCEM. Link: https://www.nyc.gov/site/em/ready/hazard-mitigation.page",
    source_year = 2019,
    description = "Erosion rates described as 'faster than citywide average' in narrative in NYC HMP 2019.",
    unit = "Feet per year",
    type = "PARAMS",
)

add_params(
    label = "erosion_rate_Rockaway_East_ft_yr",
    value = 0,
    source = "Plan for Hazards - Hazard Mitigation - NYCEM. Link: https://www.nyc.gov/site/em/ready/hazard-mitigation.page",
    source_year = 2019,
    description = "Erosion rates described as stable or gaining in narrative in NYC HMP 2019.",
    unit = "Feet per year",
    type = "PARAMS",
)

add_params(
    label = "erosion_rate_Rockaway_Middle_ft_yr",
    value = 1.7,
    source = "Plan for Hazards - Hazard Mitigation - NYCEM. Link: https://www.nyc.gov/site/em/ready/hazard-mitigation.page",
    source_year = 2019,
    description = "Erosion rates described as up to 5' per year  in narrative in NYC HMP 2019.",
    unit = "Feet per year",
    type = "PARAMS",
)

add_params(
    label = "erosion_rate_Rockaway_West_ft_yr",
    value = 0,
    source = "Plan for Hazards - Hazard Mitigation - NYCEM. Link: https://www.nyc.gov/site/em/ready/hazard-mitigation.page",
    source_year = 2019,
    description = "Erosion rates described as stable or gaining in narrative in NYC HMP 2019.",
    unit = "Feet per year",
    type = "PARAMS",
)

add_params(
    label = "erosion_rate_South_Shore_Staten_Island_ft_yr",
    value = 0,
    source = "Plan for Hazards - Hazard Mitigation - NYCEM. Link: https://www.nyc.gov/site/em/ready/hazard-mitigation.page",
    source_year = 2019,
    description = "Erosion rates described as generally stable  in narrative in NYC HMP 2019.",
    unit = "Feet per year",
    type = "PARAMS",
)

add_params(
    label = "EXH_deaths_per_year",
    value = 115,
    source = "https://www.liebertpub.com/doi/full/10.1089/hs.2015.0059",
    source_year = 2016,
    description = "Average value reported by Matte et al 2016 in  https://www.liebertpub.com/doi/full/10.1089/hs.2015.0059",
    comment = "This paper is published in 2016 and has no changes since then.",
    type = "PARAMS",
)

add_params(
    label = "EXH_outage_person_hrs_per_year",
    value = 32430,
    source = "Based on data from Dominianni 2018.",
    source_year = 2018,
    description = "Number of person hours of power outage due to extreme heat events per year.  Assumes average\
 power outage is 24 hrs long.",
    comment = "This paper is published in 2018 and has no changes since then.",
    unit = "Hours per year",
    type = "PARAMS",
)

add_params(
    label = "loss_day_power",
    value = 174,
    source = "https://www.fema.gov/sites/default/files/2020-08/fema_bca_toolkit_release-notes-july-2020.pdf",
    source_year = 2020,
    description = "Value of electrical service (per person per day) in 2015 USD (FEMA 2016).",
    unit = "USD",
    type = "PARAMS",
)

add_params(
    label = "RI_of_category_1_storm_yr",
    value = 19,
    source = "Plan for Hazards - Hazard Mitigation - NYCEM. Link: https://www.nyc.gov/site/em/ready/hazard-mitigation.page",
    source_year = 2019,
    description = "Return interval of category 1 to category 2 storm in NYC HMP 2019.",
    comment = "NYC HMP 2019 is the most recent HMP. #HMP guidelines says 'According to these NHC probability models,\
 New York City should expect to experience a lower-category hurricane on average once every 19 years and a major\
 hurricane (Category 3 or greater) on average once every 74 years. Assume annual probablitliy of cat 1 is 1/19,\
 and cat 3 is 1/74.  Don't consider 2 or 4'",
    type = "PARAMS",
)

add_params(
    label = "RI_of_category_3_storm_yr",
    value = 74,
    source = "Plan for Hazards - Hazard Mitigation - NYCEM. Link: https://www.nyc.gov/site/em/ready/hazard-mitigation.page",
    source_year = 2019,
    description = "Return interval of category 3 and higher storm in NYC HMP 2019.",
    type = "PARAMS",
)

add_params(
    label = "search_buffer_for_natural_shoreline_ft",
    value = 250,
    description = "Search buffer used to look for  shoreline around each tract.",
    unit = "Feet",
    type = "PARAMS",
)

add_params(
    label = "search_buffer_for_shelter_capacity_ft",
    value = 5280,
    description = "Search buffer used to look for shelter.",
    unit = "Feet",
    type = "PARAMS",
)

add_params(
    label = "value_moderate_injury",
    value = 588000,
    source = "Benefit-Cost Analysis Sustainment and Enhancements: Standard Economic Values Methodology Report\
 (Version 12.0) (fema.gov). Link: https://www.fema.gov/sites/default/files/documents/fema_standard-economic-values-methodology-report_2023.pdf",
    source_year = 2023,
    description = "Based on the Abbreviated Injury Scale (AIS), which categorizes injuries into levels, ranging from\
 AIS 1 (Minor) to AIS 5 (Critical), with AIS 6 being Unsurvivable.",
    unit = "USD",
    type = "PARAMS",
)

add_params(
    label = "value_of_stat_life",
    value = 12500000,
    source = "Benefit-Cost Analysis Sustainment and Enhancements: Standard Economic Values Methodology Report\
 (Version 12.0) (fema.gov). Link: https://www.fema.gov/sites/default/files/documents/fema_standard-economic-values-methodology-report_2023.pdf",
    source_year = 2023,
    description = "Life safety is the value of lives saved and injuries prevented resulting from mitigation measures.",
    comment = "Updated the Value of Statistical Life to a base year of 2022",
    unit = "USD",
    type = "PARAMS",
)

add_params(
    label = "value_per_acre_marine",
    value = 8955,
    source = "FEMA Ecosystem Service Value Updates. Link: https://www.fema.gov/sites/default/files/documents/fema_ecosystem-service-value-updates_2022.pdf",
    source_year = 2022,
    description = "Value per acre of marine land (FEMA 2016) per year.",
    comment = "The originial dataset, Marine and Estuary category (and most of its associated values) was\
 merged with the Coastal Wetland category in the 2022 updates.",
    unit = "USD",
    type = "PARAMS",
)

add_params(
    label = "value_serious_injury",
    value = 1313000,
    source = "Benefit-Cost Analysis Sustainment and Enhancements: Standard Economic Values Methodology Report\
 (Version 12.0) (fema.gov). Link: https://www.fema.gov/sites/default/files/documents/fema_standard-economic-values-methodology-report_2023.pdf",
    source_year = 2023,
    description = "Based on the Abbreviated Injury Scale (AIS), which categorizes injuries into levels, ranging from\
 AIS 1 (Minor) to AIS 5 (Critical), with AIS 6 being Unsurvivable.",
    unit = "USD",
    type = "PARAMS",
)





# print(PARAMS["average coastal erosion rate_m"].comment)

# PATHNAMES - NOT USED, JUST EXAMPLE FOR URI 3.0. SEE path_names.py FOR USE IN URI 2.1
add_params(
    label = "Example",
    value = r'.\1_RAW_INPUTS\BOUNDARY_BOROUGH_FIPS\Borough_FIPS_1.xlsx',
    source = "Newman Library of Baruch College, https://guides.newman.baruch.cuny.edu/nyc_data",
    source_year = "2021",
    comment = "Lookup table that associates borough code with borough name and FIPS code.",
    unit = "N/A",
    type = "PATHNAMES",
)


## ABBREVIATIONS
 
class abbreviations:
  def __init__(self, abbreviation=None, definition=None, category=None):
    self.abbreviation = abbreviation
    self.definition = definition
    self.category = category

  

ABBREVIATIONS = {}


def add_abbre(**kwargs):
    """Create a new params instance, and add it to the index."""

    ABBREVIATIONS[kwargs["abbreviation"]] = abbreviations(**kwargs)


add_abbre(
    abbreviation = "OTH",
    definition = "Other or combination",
    category = "Data Type",
)

# Expected Loss Factor

add_abbre(
    abbreviation = "D",
    definition = "Mortality Loss",
    category = "Expected Loss Factor",
)

add_abbre(
    abbreviation = "E",
    definition = "Environmental Loss",
    category = "Expected Loss Factor",
)

add_abbre(
    abbreviation = "I",
    definition = "Indirect Cost",
    category = "Expected Loss Factor",
)

add_abbre(
    abbreviation = "J",
    definition = "Morbidity Loss",
    category = "Expected Loss Factor",
)

add_abbre(
    abbreviation = "P",
    definition = "Property Loss",
    category = "Expected Loss Factor",
)

add_abbre(
    abbreviation = "R",
    definition = "Response Cost",
    category = "Expected Loss Factor",
)

# Hazard

add_abbre(
    abbreviation = "CER",
    definition = "Coastal Erosion",
    category = "Hazard",
)

add_abbre(
    abbreviation = "CRN",
    definition = "CBRN",
    category = "Hazard",
)

add_abbre(
    abbreviation = "CST",
    definition = "Coastal Storm",
    category = "Hazard",
)

add_abbre(
    abbreviation = "CYB",
    definition = "Cyber Threats",
    category = "Hazard",
)

add_abbre(
    abbreviation = "EMG",
    definition = "Emerging Disease Epidemic",
    category = "Hazard",
)

add_abbre(
    abbreviation = "ERQ",
    definition = "Earthquake",
    category = "Hazard",
)

add_abbre(
    abbreviation = "EXH",
    definition = "Extreme Heat",
    category = "Hazard",
)

add_abbre(
    abbreviation = "FLD",
    definition = "Flooding",
    category = "Hazard",
)

add_abbre(
    abbreviation = "HIW",
    definition = "High Winds",
    category = "Hazard",
)

add_abbre(
    abbreviation = "RES",
    definition = "Respiratory Disease Pandemic",
    category = "Hazard",
)

add_abbre(
    abbreviation = "WIW",
    definition = "Winter Weather",
    category = "Hazard",
)

# Resilience Capacity Component

add_abbre(
    abbreviation = "CC",
    definition = "Community Capital",
    category = "Resilience Capacity Component",
)

add_abbre(
    abbreviation = "ML",
    definition = "Mitigation Landscape",
    category = "Resilience Capacity Component",
)

add_abbre(
    abbreviation = "RC",
    definition = "Response Capacity",
    category = "Resilience Capacity Component",
)

add_abbre(
    abbreviation = "RR",
    definition = "Recovery Resources",
    category = "Resilience Capacity Component",
)

# Resilience Capacity Factor

add_abbre(
    abbreviation = "AC",
    definition = "Air Conditioning in the Home",
    category = "Resilience Capacity Factor",
)

add_abbre(
    abbreviation = "BI",
    definition = "Bikability",
    category = "Resilience Capacity Factor",
)

add_abbre(
    abbreviation = "CC",
    definition = "Cooling Centers",
    category = "Resilience Capacity Factor",
)

add_abbre(
    abbreviation = "CI",
    definition = "Community Infrastructure",
    category = "Resilience Capacity Factor",
)

add_abbre(
    abbreviation = "EM",
    definition = "Emergency Medical Access",
    category = "Resilience Capacity Factor",
)

add_abbre(
    abbreviation = "EO",
    definition = "Education and Outreach",
    category = "Resilience Capacity Factor",
)

add_abbre(
    abbreviation = "EP",
    definition = "Evacuation Potential",
    category = "Resilience Capacity Factor",
)

add_abbre(
    abbreviation = "FP",
    definition = "Flood Insurance Coverage",
    category = "Resilience Capacity Factor",
)

add_abbre(
    abbreviation = "GI",
    definition = "Green Infrastructure",
    category = "Resilience Capacity Factor",
)

add_abbre(
    abbreviation = "HI",
    definition = "Health Insurance Coverage",
    category = "Resilience Capacity Factor",
)

add_abbre(
    abbreviation = "HO",
    definition = "Home Ownership",
    category = "Resilience Capacity Factor",
)

add_abbre(
    abbreviation = "IE",
    definition = "Income Equality",
    category = "Resilience Capacity Factor",
)

add_abbre(
    abbreviation = "IN",
    definition = "Institutional Experience",
    category = "Resilience Capacity Factor",
)

add_abbre(
    abbreviation = "MH",
    definition = "Median Household Income",
    category = "Resilience Capacity Factor",
)

add_abbre(
    abbreviation = "MI",
    definition = "Mitigation Investments",
    category = "Resilience Capacity Factor",
)

add_abbre(
    abbreviation = "NS",
    definition = "Presence of Natural Shorelines",
    category = "Resilience Capacity Factor",
)

add_abbre(
    abbreviation = "PA",
    definition = "Place Attachment",
    category = "Resilience Capacity Factor",
)

add_abbre(
    abbreviation = "PE",
    definition = "Political Engagement",
    category = "Resilience Capacity Factor",
)

add_abbre(
    abbreviation = "PW",
    definition = "Parks with Water Feature",
    category = "Resilience Capacity Factor",
)

add_abbre(
    abbreviation = "SC",
    definition = "Shelter Capacity",
    category = "Resilience Capacity Factor",
)

add_abbre(
    abbreviation = "TR",
    definition = "Transit",
    category = "Resilience Capacity Factor",
)

add_abbre(
    abbreviation = "VC",
    definition = "Vegetative Cover",
    category = "Resilience Capacity Factor",
)

add_abbre(
    abbreviation = "WA",
    definition = "Walkability",
    category = "Resilience Capacity Factor",
)

# URI Component

add_abbre(
    abbreviation = "ESL",
    definition = "Estimated Loss",
    category = "URI Component",
)

add_abbre(
    abbreviation = "RCA",
    definition = "Resilience Capacity",
    category = "URI Component",
)

add_abbre(
    abbreviation = "SOV",
    definition = "Social Vulnerability",
    category = "URI Component",
)
