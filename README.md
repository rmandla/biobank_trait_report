# Create PDF reports for trait harmonization in biobanks

Traits/phenotypes in biobanks can be filled with errors that may be due to erroneous data points being entered into the biobank and/or specific sources or classifications of phenotypes/traits which are more or less error-prone than other sources. This script can be used for this latter case, to identify specific data sources or data descriptions which should be removed.

This script will create a pdf report of the distribution and descriptor statistics of all recorded instances of a trait and instances stratified by specific descriptor variables (unit of the measurement, source of the data, etc.). It can be run in multiple steps to create different reports for each filtering decision that is made.

## Dependencies

The following Python packages are required to run the script:

* pandas
* seaborn
* matplotlib
* numpy
* pylatex

The following packages are required to run the script:

* texlive

## Documentation

`python biobank_trait_report.py [arguments]`

 - -d,   --data: a table for input. The table should be organized as having one row per measurement, with additional columns for each descriptor variable for stratification, sex, and a participant id per measurement
 - -n,   --measurement_name: the name of the trait/measurement for report generation
 - -vn,  --value_name: the name of the column in `-d` that contains actual values of the trait of interest
 - -vd,  --value_descriptor: a short description of the trait/measurement and how it is pulled (used in the report generation)
 - -s,   --sex_col_name: the name of the column in `-d` with Sex information per participant. Values should include 'Male' and/or 'Female'
 - -b,   --biobank: the name of the biobank. Currently only AoU is supported
 - -pid, --participant_id: name of the column in `-d` that contains the participant id per measurement. DEFAULT to "person_id"
 - -dt,  --descriptor_table: the name of a table for input with two rows. The header contains the descriptor column names in `-d` to be used for stratification. The values include a short summary on what the descriptor column name means
 - -sep, --separator: character to be used to delimit the tables. DEFAULT to "\t"
 - -o,   --output: the output name of the PDF report


