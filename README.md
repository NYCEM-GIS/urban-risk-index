# NYC Urban Risk Index 

 

## Table of Contents 

 

- [NYC Urban Risk Index](#NYC_Urban_Risk_Index) 
- [Components](#Components) 
- [Getting Started](#Getting_Started)
- [Contribution](#Contribution)
- [Getting Started](#This_Repository) 
- [License](#license) 

 

## NYC Urban Risk Index 

 

The [NYC Urban Risk Index] (https://uri.nychazardmitigation.com) (URI) is a hazard and risk communication tool developed by NYC Emergency Management (NYCEM) to evaluate and understand the various relative risks posed by natural hazards to New York City neighborhoods. 

The URI is designed to provide a relative comparison of vulnerability between NYC neighborhoods to natural hazards. The URI is an informational tool to raise awareness about hazard exposure in NYC and to direct users to other sources, like the [NYC Hazard Mitigation Plan] (https://nychazardmitigation.com), to learn more about the hazards and steps to reduce risk. Although the URI was built using the best-available data, given this is a city-wide index, the URI may have some inaccuracies, particularly for hazards where limited data was available. As such, the URI is not intended to inform hazard mitigation investments or response planning, nor should it supersede guidance provided by NYC or emergency management officials or agencies. 

### This Repository
This repo holds scripts functions and Jupyter Notebooks that are used to perform pre-processing of over fifty datasets and  sub-components including Estimated Loss, Resilience Capacity, and Social Vulnerability that are required to calculate the risk score on census tract level. Please note this repo is currently not operational as source datasets required are not provided. The purpose of the repo is to publish the methodology so that the open data community and the public will have a chance to look behind the curtain to see how a risk index calculation is performed and facilitate conversation around risk indexing for hazards in New York City.  
 

![Alt Text – A Screenshot of the Front-end of the NYC Urban Risk Index]( https://nychazardmitigation.com/wp-content/uploads/2025/03/Screenshot-2025-03-13-155611.png) 

 

## Components 

The URI comprises several distinct components. 

 

### Back-end 

Primarily developed in Python, handling data processing and analysis to generate the risk assessments. Those scripts are found in this repository. This component also includes large datasets not found in this repository. 

 

### Front-end 

Provides a user-friendly interface where users can interact with the data visualizations and retrieve relevant information about the risks in different NYC neighborhoods. This component was developed using Esri ArcGIS Dashboards, leveraging agency capabilities and maintaining inheritability. 

 

## Getting Started 
 

### Dependency 

- [Python 3.11.8](https://www.python.org/downloads/release/python-3118/) for running python code

- [git](https://git-scm.com/downloads) for cloning repo

`4_POSTPROCESS_GIS.ipynb` use arcpy which can be acquired with ArcPro installation from GIS team. 



### Installation 

> [!IMPORTANT]
> For City employees, installing software on work computers can be difficult due to a lack of administrative access. But you may be able to install software "only for me" rather than "anyone who uses this computer".
>
> All of these prerequisites can be (and by default are) installed only for the user rather than system-wide.
> 
> for NYCEM members who are trying to run this repo on agency issued desktop or laptopso make sure your user privilege is set by running following command in PowerShell before activating virtual environment or running any scripts 

``` 
PS C:\> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser 
``` 

Python dependencies are specified in the requirements.txt files. It's recommended to use `venv`and pip installation for the package required

```shell 
python -m venv .venv 

.venv\Scripts\Activate.ps1 
``` 
and then use pip for installation 

``` 
pip install -r requirements.txt
``` 


### Usage

 

Index calculation is done with a series Jupyter Notebooks.  

 

`1_PRECALC_ESL_1.ipynb` calculates the loss factors for each of hazards URI considers. After loss factors are calculated, they are then normalized by their respective normalization factors. Then they are written out to a tract-level results as shapefiles.   

 

`2_PRECALC_RCA_1.ipynb` calculates the Resiliency Capacity subcomponent. Refer to slide 12 in [documentation]() for what Resiliency Capacity subcomponent is applied to what types of hazard.   

 

`3_CALC_URI_1.ipynb` calculates Social Vulnerability and calculates risk score for each hazards and all hazard risk score.  

 

`4_POSTPROCESS_GIS.ipynb` handles the process cleaning the fields and export final risk results as geodatabase which is then imported in to the URI platform.  

 

 

 ## Contribution

 Contribution are welcomed but we require any changes are made to a feature branch. _Any change directly to the main branch is prohibited._ If you want to make pull request, please provide some descriptions what are changes made and why do you think the change are helpful in improving the tool. See [an example] for a pull request. 

 

## Disclaimer 

The URI was developed by NYC Emergency Management (NYCEM) using publicly available data and is provided solely for informational purposes. NYCEM makes no representation as to the accuracy of the information or to its suitability for any purpose. NYCEM disclaims any liability for errors that may be contained herein and shall not be responsible for any damages consequential or actual, arising out of or in connection with the use of this information. NYCEM makes no warranties, express or implied, including, but not limited to, implied warranties of merchantability and fitness for a particular purpose as to the quality, content, accuracy, or completeness of the information, text graphics, links and other items contained in the URI. The URI does not supersede other hazard guidance provided by NYCEM and the City of New York and should not be used for formal hazard mitigation or emergency response planning purposes. 

 

## License 

The NYC Urban Risk Index is released under the [BSD license](https://opensource.org/license/BSD-3-Clause). 

 

Copyright 2025 NYC Emergency Management 

 

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met: 

 

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer. 

 

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution. 

 

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission. 

 

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. 

 

 

 

 

 