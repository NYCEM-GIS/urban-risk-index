import arcpy
import pandas as pd
import os
import sys
import datetime as dt
from pathlib import Path
sys.path.extend([Path(__file__).parent.parent.parent])
import URI.PARAMS.path_names as PATHNAMES
arcpy.env.overwriteOutput = True

alias_path = PATHNAMES.dashboard_aliases
combined_path = PATHNAMES.OUTPUTS_folder + r'\Dashboard\URI_Combined_NTA.shp'
gdb_path = PATHNAMES.OUTPUTS_folder + rf'\Dashboard\URI_{dt.datetime.today().strftime("%Y%m%d")}.gdb'

fc_name='URI_NTA'
out_path = os.path.join(gdb_path, fc_name)
domain_name = "Score"
hazard_domain = 'Hazard_Score'  # No Impacts
resilience_domain = 'Resilience_Score'  # No Capacity

domain_dict = {
    0: "No Impacts",
    1: "Very Low", 
    2: "Low", 
    3: "Moderate", 
    4: "High", 
    5: "Very High"}

data_type_dict = {
    'Text': '80 Text',
    'Short': '24 Short'
}

end_string_dict = {
    'Text': ',0,79',
    'Short': ',-1,-1'
}

if not arcpy.Exists(gdb_path):
    print('Creating Geodatabase with domain...')
    output_directory = os.path.dirname(gdb_path)
    output_gdb = os.path.basename(gdb_path)
    arcpy.CreateFileGDB_management(output_directory, output_gdb)
    arcpy.management.CreateDomain(
        in_workspace=gdb_path, 
        domain_name=domain_name, 
        domain_description=domain_name, 
        field_type='SHORT', 
        domain_type='CODED')
    for code in domain_dict.keys():        
        arcpy.management.AddCodedValueToDomain(gdb_path, domain_name, code, domain_dict[code])

# Rename field names with aliases
print('Renaming fields with aliases and converting to integer fields...')
aliases = pd.read_excel(alias_path)
aliases['Data Type'] = aliases['Type'].map(data_type_dict)
aliases['End String'] = aliases['Type'].map(end_string_dict)
first_string = 'true true false'
mid_string = f'0 0,First,#,{combined_path},'
aliases['Field Mapping'] = aliases.apply(
    lambda row: f'{row["Field Name"]} "{row["Alias"]}" {first_string} {row["Data Type"]} {mid_string}{row["Field Name"]}{row["End String"]}', 
    axis=1)
field_mapping = ';'.join(aliases['Field Mapping'].to_list())
arcpy.FeatureClassToFeatureClass_conversion(
    in_features=combined_path,
    out_path=gdb_path,
    out_name=fc_name,
    field_mapping=field_mapping
)

# Apply domain to all score fields
print('Applying domain to score fields...')
score_fields = aliases[aliases['Category'] == 'Score']['Field Name']
for score_field in score_fields:
    arcpy.management.AssignDomainToField(out_path, score_field, domain_name)

# Repair Geometry
arcpy.management.RepairGeometry(
    in_features=out_path
)
print('Done!')