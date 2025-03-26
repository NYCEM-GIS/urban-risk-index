# NYC Urban Risk Index

## Table of Contents

- [NYC Urban Risk Index](#nyc-urban-risk-index)
- [Getting Started](#getting-started)
- [Contribution](#contribution)
- [License](#license)

## NYC Urban Risk Index

The [NYC Urban Risk Index](https://uri.nychazardmitigation.com) (URI) is a hazard and risk communication tool developed by NYC Emergency Management (NYCEM) to evaluate and understand the relative risks posed by natural hazards to New York City neighborhoods.

The URI is designed to provide a relative comparison of vulnerability between NYC neighborhoods to natural hazards. The URI is an informational tool to raise awareness about hazard exposure in NYC and to direct users to other sources, like the [NYC Hazard Mitigation Plan](https://nychazardmitigation.com), to learn more about the hazards and steps to reduce risk. Although the URI was built using the best-available data, given this is a city-wide index, the URI may have some inaccuracies, particularly for hazards where limited data was available. As such, the URI is not intended to inform hazard mitigation investments or response planning, nor should it supersede guidance provided by NYC or emergency management officials or agencies.

This repository contains scripts, primarily developed with Python, and Jupyter Notebooks that handle data processing and calculations to produce the risk assessment scores. It reflects the latest URI methodology, but the raw datasets are NOT included due to their size and confidentiality.
 
If you are interested in the URI 2.1 neighborhood-level results and subcomponents, visit our [ESRI-based platform](https://www.uri.nychazardmitigation.com).
![Alt Text – A Screenshot of the Front-end of the NYC Urban Risk Index](https://nychazardmitigation.com/wp-content/uploads/2025/03/Screenshot-2025-03-13-155611.png)

## Getting Started

> [!IMPORTANT]
> NYCEM internal members running and maintaining URI will need to first acquire the zip folder with source data and data directory setup before following the steps outlined below.
>
> For NYCEM members who are trying to run this repo on an agency-issued desktop or laptop, make sure your user privilege is set by running the following command in PowerShell before activating the virtual environment or running any scripts:
``` PowerShell
PS C:\> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Dependency
> [!IMPORTANT]
> For City employees, installing software on work computers can be difficult due to a lack of administrative access. But you may be able to install software "only for me" rather than "anyone who uses this computer".
>
> All of these prerequisites can be (and by default are) installed only for the user rather than system-wide.
>
- [Python 3.11.8](https://www.python.org/downloads/release/python-3118/) for running Python code
- [git](https://git-scm.com/downloads) for cloning the repo
- [ArcPy](https://pro.arcgis.com/en/pro-app/latest/arcpy/get-started/what-is-arcpy-.htm) `4_POSTPROCESS_GIS.ipynb` requires ArcPy. Ask the NYCEM GIS team for ArcPro installation.

### Installation

Read the project setup notes above and unzip the files into your project directory. Then change the directory into the unzipped folder, e.g.

```bash
cd .\URI_Calculator_v2_1_TEMPLATE_v2\
ls
```
should return the following:

```
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
dar--l         2/19/2025   9:32 AM                .venv
dar--l         2/14/2025   2:15 PM                1_RAW_INPUTS
dar--l         2/14/2025   2:20 PM                2_PROCESSED_INPUTS
dar--l         2/14/2025   2:20 PM                3_OUTPUTS
dar--l         3/24/2025  10:15 AM                4_CODE
```
Now change the directory into the `4_CODE` and clone the repository from GitHub:

```shell
cd .\4_CODE\
git clone https://github.com/NYCEM-GIS/urban-risk-index.git
```
If the `git clone` command was successful, you should now be able to install Python dependencies which are specified in the requirements.txt file. It's recommended to use `venv` and pip for the package installation:

```shell
python -m venv .venv

.venv\Scripts\Activate.ps1
```
and then use pip for installation:

```shell
pip install -r requirements.txt
```

### Usage

Urban Risk Index calculation is done with a series of Jupyter Notebooks.

`1_PRECALC_ESL_1.ipynb` calculates the loss factors for each of the hazards URI considers. After loss factors are calculated, they are then normalized by their respective normalization factors. Then they are written out to tract-level results as shapefiles.

`2_PRECALC_RCA_1.ipynb` calculates the Resiliency Capacity subcomponent. Refer to slide 12 in the [documentation](https://github.com/NYCEM-GIS/urban-risk-index/tree/main/docs/URI%20Public%20Facing%20Methodology_20250310.pdf) for what Resiliency Capacity subcomponent is applied to what types of hazard.

`3_CALC_URI_1.ipynb` calculates Social Vulnerability and calculates the risk score for each hazard and the overall hazard risk score.

`4_POSTPROCESS_GIS.ipynb` handles the process of cleaning the field names and exporting the final risk results as a geodatabase which is then imported into the [URI platform](https://www.uri.nychazardmitigation.com).

## Contribution

Contributions are welcomed but we require any changes to be made to a feature branch. _Any change directly to the main branch is prohibited._ If you want to make a pull request, please provide some descriptions of what changes were made and why you think the changes are helpful for improving the tool.

## Disclaimer

The URI was developed by NYC Emergency Management (NYCEM) using publicly available data and is provided solely for informational purposes. NYCEM makes no representation as to the accuracy of the information or to its suitability for any purpose. NYCEM disclaims any liability for errors that may be contained herein and shall not be responsible for any damages consequential or actual, arising out of or in connection with the use of this information. NYCEM makes no warranties, express or implied, including, but not limited to, implied warranties of merchantability and fitness for a particular purpose as to the quality, content, accuracy, or completeness of the information, text graphics, links and other items contained in the URI. The URI does not supersede other hazard guidance provided by NYCEM and the City of New York and should not be used for formal hazard mitigation or emergency response planning purposes.

## License

The NYC Urban Risk Index is released under the [BSD license](https://opensource.org/license/BSD-3-Clause).

Copyright 2025 NYC Emergency Management

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.









