import pandas as pd
from pathlib import Path
import os


## PARAMETERS

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
  

PARAMS = {
    row["label"]: params(**row) for idx, row in pd.read_csv(os.path.join(Path(__file__).parent, 'parameters.csv')).iterrows()
}


## ABBREVIATIONS
 
class abbreviations:
  def __init__(self, abbreviation=None, definition=None, category=None, status=None):
    self.abbreviation = abbreviation
    self.definition = definition
    self.category = category
    self.status = status

ABBREVIATIONS = {
    row["abbreviation"]: abbreviations(**row) for idx, row in pd.read_csv(os.path.join(Path(__file__).parent, 'abbreviations.csv')).iterrows()
}  
