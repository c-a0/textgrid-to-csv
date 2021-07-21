# textgrid-to-csv
Script to convert TextGrid data to .csv format, which can be opened in any spreadsheet program.

   Use:
       Put the script in the folder where your TextGrids are, cd to that folder, and run:
         python tg2csv.py

   Note: this script is designed only for songs in 4/4
   
　
 
The following are explanations of each column of the spreadsheet:

Syllable: The syllable text

Metric Absolute: How many beats into the song the syllable is

Micro Absolute: The starting time for the syllable's microtiming interval

Metric Measure: Formatted as X.Y, where X is which measure of the song the syllable is in, Y is which beat of that measure the syllable is on

Beat Strength: Out of tiers 1, 2, 3, and 4, which is the lowest number tier that the current metric interval lines up with?

Accent: Does the syllable have a strong accent (X), a weak accent (x), or no accent (not marked)?

Zone: Which zone the syllable is in

