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


add_params(
    label = "null_value",
    value = "-999 or '-999'",
    source = "",
    source_year = "",
    comment = "",
    unit = "",
    type = "HARDCODED",
)
add_params(
    label = "heat_event_count_start_date",
    value = "1/01/2000",
    source = "",
    source_year = "",
    comment = "Start date for counting extreme heat events in HH&C to determine liklihood",
    unit = "",
    type = "HARDCODED",
)
add_params(
    label = "heat_event_count_end_date",
    value = "31/12/2019",
    source = "",
    source_year = "",
    comment = "End date for counting extreme heat events in HH&C to determine likilhood",
    unit = "",
    type = "HARDCODED",
)
add_params(
    label = "list_excluded_tracts",
    value = [5990100, 5008900],
    source = "",
    source_year = "",
    description = "Tract IDs to be excluded from analysis.",
    comment = "990100 is Hoffman and Swinburne island, which are not inhabited. 8900 is a pier on Staten Island and is no longer a tract in the 2020 census data.",
    unit = "",
    type = "HARDCODED",
)
add_params(
    label = "hhc_event_count_start_date",
    value = "1/01/2000",
    source = "",
    source_year = "",
    comment = "start date for  events in HH&C to determine liklihood",
    unit = "",
    type = "HARDCODED",
)
add_params(
    label = "hhc_event_count_end_date",
    value = "31/12/2019",
    source = "",
    source_year = "",
    comment = "end date for  events in HH&C to determine likilhood",
    unit = "",
    type = "HARDCODED",
)

# SETTINGS
add_params(
    label = "epsg",
    value = 2263,
    source = "",
    source_year = "",
    comment = "Default projection for all inputs",
    unit = "",
    type = "SETTINGS",
)
add_params(
    label = "target_year",
    value = 2024,
    source = "",
    source_year = "",
    comment = "all costs will be adjusted to dollars in this year using CPI index",
    unit = "",
    type = "SETTINGS",
)
add_params(
    label = "make_plots",
    value = True,
    source = "",
    source_year = "",
    description = "Flag for making plots in Jupyter Notebooks.",
    comment = "Set to True to make plots, False otherwise.",
    unit = "",
    type = "SETTINGS",
)
# add_params(
#     label = "",
#     value = "",
#     source = "",
#     source_year = "",
#     comment = "",
#     unit = "",
#     type = "",
# )
print(PARAMS["make_plots"].value)

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