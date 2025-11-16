# README
Christoph Lechner, Nov 2025

## Summary

## Layout of the System
![Layout](doc/schematic.png)

## Details
* [Python program to store the wikimedia event stream](streamreader/)
* Python program to [import and merge](import_and_merge/) the files written by the streamreader into the SQL database
* To visualize the information contained in the database
  * Streamlit-based plotting solution can be found [here](sl/)
  * To make this Streamlit-based plotting solution available via HTTPS, a reverse proxy using Apache2 was set up. It also does user authentication. For a few configuration details, see [here](doc/apache2_revproxy/)
  * Finally a few several Python programs using `matplotlib.pyplot` are available in [misc/](misc/)
