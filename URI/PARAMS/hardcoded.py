import datetime
list_excluded_tracts = [5990100, 5008900]  # Tract IDs to be excluded from analysis. 990100 is Hoffman and Swinburne island, which are not inhabited. 8900 is a pier on Staten Island and is no longer a tract in the 2020 census data.
heat_event_count_start_date = datetime.datetime(year=2000, month=1, day=1)  # Start date for counting extreme heat events in HH&C to determine liklihood
heat_event_count_end_date = datetime.datetime(year=2019, month=12, day=31)  # End date for counting extreme heat events in HH&C to determine likilhood
hhc_event_count_start_date = datetime.datetime(year=2000, month=1, day=1)  # Start date for  events in HH&C to determine liklihood
hhc_event_count_end_date = datetime.datetime(year=2019, month=12, day=31)  # End date for  events in HH&C to determine likilhood
search_buffer_for_natural_shoreline_ft = 250  # Search buffer (in feet)used to look for  shoreline around each tract.
search_buffer_for_shelter_capacity_ft = 5280  # Search buffer (in feet) used to look for shelter.
average_duration_CST_displacement_days = 30  # Assumed duration of displacement if flood flooded.
buffer_period_power_outage_days = 2  # Number of days after the end of storm during which power outages are attributed to that storm.
buffer_period_tree_servicing_days = 2  # Number of days after the end of storm during which tree service calls are attributed to that storm.
building_floor_height_flood_threshold_ft = 1  # Threshold for flooding floor and displacing all residents.
building_floor_height_ft = 10  # Assumed height of building floor in NYC. Heights can vary depending on factors such as building codes and building type.
