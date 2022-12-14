### Open source asteroid detection algorithm is somehow hard to find, EURONEAR project is one but source code not provided. Thanks to [T. Atay](https://github.com/akdeniz-uzay),  writing codes for detecting asteroids has become much more easier.
### To be continued...
[A-Track](https://github.com/akdeniz-uzay/A-Track) works in (x,y) plane which is time consuming for wide field of view telescope, I simply changed it to celestial coordinate and fixed several mysterious bugs. 

Some problems remains unsolved including pool.py(error appear when input over 10 fits using multiprocessing) and list.append failed to be replaced by pandas.DataFrame.concat. For large CCD, plotting check images become to large to generate a gif.

 Testdata added in A-Track/testdata/
 
Dependencies not completely listed here...(be patient with warnings lol...)

WCS head needed

# Moving Object Detection(Slightly changed)

### Dependencies:

* [Python](https://www.python.org/) 3.4.x or later.
* [Numpy](http://www.numpy.org/) 1.8.x or later.
* [Pandas](http://pandas.pydata.org/) 0.16.x or later.
* [AliPy](http://obswww.unige.ch/~tewes/alipy/) 2.0.x or later.
* [PyFITS](http://www.stsci.edu/institute/software_hardware/pyfits) 3.3.x or later.
* [f2n](https://github.com/akdeniz-uzay/mod/tree/master/f2n) for Python 3

### <a name="usage"></a> Usage

```
usage: python3 atrack.py [-h] [-r ref_image] [-c] [-m] [-i] [-g]
                         [-p catalog_file] [-v]
                         fits_dir

A-Track.

positional arguments:
  fits_dir              FITS image directory

optional arguments:
  -h, --help            show this help message and exit
  -r ref_image, --ref ref_image
                        reference FITS image for alignment (with path)  
  -c, --skip-cats       skip creating catalog files if they are already
                        created
  -m, --skip-mpcreport  skip creating MPC file
  -i, --skip-pngs       skip creating PNGs
  -g, --skip-gif        skip creating animation file
  -p catalog_file, --plot-objects catalog_file
                        plot all objects in the catalog file on FITS file.
  -v, --version         show version
```

### Installation

A-Track is tested on Ubuntu 14.04 LTS, Fedora 22 and Mac OS X Yosemite. If you want to use A-Track on Windows, you need to install SExtractor first! This is a bit tricky. Please see [this thread](http://www.astromatic.net/forum/showthread.php?tid=948).

To install A-Track on Linux or Mac, you can simply download the A-Track package and run the installation scripts install_linux.sh (for Linux: `sudo sh install_linux.sh`) or install_mac.sh (for Mac: `sh install_mac.sh`).

<br>
Alternatively, you can install A-Track manually following these steps:

1. **Install Python3, pip3, imagemagick, git, and SExtractor:**

  **Ubuntu:**  
  `sudo apt-get install python3 python3-dev python3-pip imagemagick sextractor libxt-dev git build-essential`

  **Fedora:**  
  `sudo dnf install python3 python3-devel python3-pip imagemagick sextractor libXt-devel git make automake gcc gcc-c++ kernel-devel`  
  Install the latest SExtractor from [here](http://www.astromatic.net/download/sextractor/) (we recommend v2.19.5 as the older versions detect fewer objects).

  **Mac OS X:**  
  `brew install python3 python3-pip imagemagick git-all sextractor`  
  (You will need [Homebrew](http://brew.sh) to install the dependencies.)  
  
  
2. **Install Numpy, Pandas, Scipy, pyFITS, and pillow using pip3:**

  `sudo pip3 install scipy pandas numpy pyfits pillow`  
  (Mac users do not use `sudo`.)  
  

3. **Download and install astroasciidata:**  

  `cd A-Track-Modified-/A-Track dependency`  
  `sudo python3 setup.py install`

4. **Download and install Alipy:**  

  `cd A-Track-Modified-/A-Track dependency`  
  `sudo python3 setup.py install`  

5. **Download the A-Track package and install f2n:**  

  `https://github.com/Eririf/A-Track-Modified-.git`  
  `cd A-Track-Modified-/f2n`  
  `sudo python3 setup.py install`  
  (Mac users do not use `sudo`.)
 
 6. **Download and install Astrometry.net & catalogs!**

Now, you have A-Track! You can open a command-line interface in the A-Track directory and [run A-Track](#usage).

For academic use, please cite the paper:

> Atay, T., Kaplan, M., Kilic, Y., Karapinar, N.,
> 2016,
> *A-Track: A new approach for detection of moving objects in FITS images*,
> **Computer Physics Communications**, Volume 207, p. 524-530.

[Bibtex@ADS](http://adsabs.harvard.edu/cgi-bin/nph-bib_query?bibcode=2016CoPhC.207..524A&data_type=BIBTEX&db_key=PHY&nocookieset=1)
| [CPC](http://www.sciencedirect.com/science/article/pii/S0010465516302119)
| [doi:10.1016/j.cpc.2016.07.023](http://dx.doi.org/10.1016/j.cpc.2016.07.023)
