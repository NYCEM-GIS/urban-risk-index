class params:
  def __init__(self, label, value, source, source_year, comment, unit, type):
    self.label = label
    self.value = value
    self.source = source
    self.source_year = source_year
    self.comment = comment
    self.unit = unit
    self.type = type
  


params_dict = {}

param_variables = {}


def add_params(**kwargs):
    """Create a new params instance, and add it to the index."""

    param_variables[kwargs["label"]] = params(**kwargs)


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
    comment = "start date for counting extreme heat events in HH&C to determine liklihood",
    unit = "",
    type = "HARDCODED",
)
add_params(
    label = "heat_event_count_end_date",
    value = "31/12/2019",
    source = "",
    source_year = "",
    comment = "end date for counting extreme heat events in HH&C to determine likilhood",
    unit = "",
    type = "HARDCODED",
)
add_params(
    label = "list_excluded_tracts",
    value = [5990100, 5008900],
    source = "",
    source_year = "",
    comment = "tract number of tracts to exclude.  990100 is Hoffman and Swinburne island, which are not inhabited. 8900 is a pier on Staten Island and is no longer a tract in the 2020 census data",
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
    value = "TRUE",
    source = "",
    source_year = "",
    comment = "Set to True to make plots, False otherwise.  ",
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
print(param_variables["make_plots"].value)