# -*- coding: utf-8 -*-A
# Authors: Yücel Kılıç, Murat Kaplan, Nurdan Karapınar, Tolga Atay.
# This is an open-source software licensed under GPLv3.

try:
    import pandas as pd
except ImportError:
    print('Python cannot import pandas. Make sure pandas is installed.')
    raise SystemExit

try:
    import sources
except ImportError:
    print('Python cannot import sources.py. Make sure sources.py is in',
          'the same folder as atrack.py.')
    raise SystemExit

try:
    import asteroids
except ImportError:
    print('Python cannot import asteroids.py. Make sure asteroids.py is in',
          'the same folder as atrack.py.')
    raise SystemExit

try:
    import visuals
except ImportError:
    print('Python cannot import visuals.py. Make sure visuals.py is in',
          'the same folder as atrack.py.')
    raise SystemExit

try:
    from astropy.io import fits
    from astropy.table import Table, vstack
    from astropy.table import QTable
    from astropy.coordinates import SkyCoord
    import astropy.units as u
    from astropy.io import ascii
except ImportError:
    print('Python cannot import astropy. Make sure astropy is installed.')
    raise SystemExit

import time
import os
import glob
import argparse
from mpcreporter import astronomy
from mpcreporter import io
import numpy as np


from configparser import ConfigParser

config = ConfigParser()

if os.path.exists('./atrack.config'):
    config.read('./atrack.config')
else:
    print('Python cannot open the configuration file. Make sure atrack.config',
          'is in the same folder as atrack.py.')
    raise SystemExit

if __name__ == '__main__':

    start = time.time()
    parser = argparse.ArgumentParser(prog='python3 atrack.py',
                                     description='A-Track.')
    parser.add_argument('fits_dir',
                        help='FITS image directory')
    parser.add_argument('-r', '--ref',
                        type=str,
                        metavar='ref_image',
                        help='reference FITS image for alignment (with path)')
#    parser.add_argument('-a', '--skip-align',
#                        action='store_true',
#                        help='skip alignment if alignment is already done')
    parser.add_argument('-c', '--skip-cats',
                        action='store_true',
                        help='skip creating catalog files ' +
                        'if they are already created')
    parser.add_argument('-m', '--skip-mpcreport',
                        action='store_true',
                        help='skip creating MPC file')
    parser.add_argument('-i', '--skip-pngs',
                        action='store_true',
                        help='skip creating PNGs')
    parser.add_argument('-g', '--skip-gif',
                        action='store_true',
                        help='skip creating animation file')
    parser.add_argument('-p', '--plot-objects',
                        type=str,
                        metavar='catalog_file',
                        help='plot all objects in the catalog file on FITS file.')
    parser.add_argument('-v', '--version',
                        action='version',
                        help='show version',
                        version='A-Track version 1.0')

    arguments = parser.parse_args()

    """
    This section will be applied if there is a catalog file in atrack directory.
    """
    if arguments.plot_objects:
        print(arguments.plot_objects)
        catalog_file = arguments.plot_objects
        cathead, catextension = os.path.splitext(catalog_file)
        visuals.object_plot("{0}.fits".format(cathead),
                            catalog_file)
        raise SystemExit
    """
    This section will be applied if there is a catalog file in atrack directory.
    """

    fitsdir, reference = arguments.fits_dir, arguments.ref

    types = (fitsdir + '/*.fits', fitsdir + '/*.fit',
             fitsdir + '/*.fts')  # the tuple of file types
    fits_grabbed = []
    for fits_files in types:
        fits_grabbed.extend(glob.glob(fits_files))

    if len(sorted(fits_grabbed)) < 3:
        print(
            'Please provide at least 3 FITS images to the {0}'.format(fitsdir))
        raise SystemExit

    outdir = fitsdir + '/atrack'

    if not os.path.isdir(outdir):
        os.makedirs(outdir)

#    if not arguments.skip_align:
#        print('\nAligning images...', end=' ')
#        sources.align(fitsdir, reference, outdir)
#        count_aligned = len(glob.glob("{0}/*affineremap.fits".format(outdir)))
#        if count_aligned < 3:
#            print('Could not aligned at least 3 FITS images!')
#            print('A-Track can not proceed!')
#            raise SystemExit
#        elapsed = int(time.time() - start)
#        print('Complete!')
#        print('Aligned images are saved as *affineremap.fits.')
#        print('Elapsed time: {0} min {1} sec.'
#              .format(elapsed // 60, elapsed % 60))

    if not arguments.skip_cats:
        print('\nCreating catalog files...', end=' ')
        sources.make_catalog(fitsdir, outdir)
        elapsed = int(time.time() - start)
        print('Complete!')
        print('Catalog files are saved as *.pysexcat.')
        print('Elapsed time: {0} min {1} sec.'
              .format(elapsed // 60, elapsed % 60))

    print('\nBuilding master catalog file...', end=' ')
    sources.make_master(outdir)
    elapsed = int(time.time() - start)
    print('Complete!')
    print('Master catalog file is saved as master.pysexcat.')
    print('Elapsed time: {0} min {1} sec.'
          .format(elapsed // 60, elapsed % 60))

    print('\nDetecting candidates...', end=' ')
    asteroids.all_candidates(outdir, outdir)
    elapsed = int(time.time() - start)
    print('Complete!')
    print('Candidates for each image are saved as *.cnd.')
    print('Elapsed time: {0} min {1} sec.'.format(elapsed // 60, elapsed % 60))

    print('\nDetecting moving objects...\n')
    lines = asteroids.detect_lines(outdir, fitsdir)

    if len(lines) == 0:
        print('A-Track could not find any moving objects in the images.')
        raise SystemExit

    moving_objects, uncertain_objects = asteroids.results(fitsdir, lines)
    pd.set_option('expand_frame_repr', False)

    wcs_status = config.get('sources', 'solve_field')

    COLUMNS = ['FileID', 'Flags', 'x', 'y', 'R.A. (J2000)', 'Decl.', 'Flux', 'FluxErr',
               'Background', 'Mag', 'MagErr', 'FWHM', 'Elongation', 'ObjectID',
               'Sky Motion']

    NEWCOLS = ['ObjectID', 'FileID', 'Flags', 'x', 'y', 'R.A. (J2000)', 'Decl.', 'Flux', 'FluxErr',
               'Background', 'Mag', 'MagErr', 'FWHM', 'Elongation', 'Sky Motion']

    elapsed = int(time.time() - start)
    print('\nMoving object detection completed.')
    print('Elapsed time: {0} min {1} sec.'.format(elapsed // 60, elapsed % 60))

    if moving_objects.size:

        moving_objects = pd.DataFrame.from_records(moving_objects,
                                                   columns=COLUMNS)
        moving_objects = moving_objects.reindex(NEWCOLS, axis=1)
        moving_objects[['FileID',
                        'Flags',
                        'ObjectID']] = moving_objects[['FileID',
                                                       'Flags',
                                                       'ObjectID']].astype(int)

        moving_objects = QTable.from_pandas(moving_objects)

        p = SkyCoord(moving_objects['R.A. (J2000)'] *
                     u.degree, moving_objects['Decl.'] * u.degree)

        moving_objects['R.A. (J2000)'].unit = "hourangle"
        moving_objects['R.A. (J2000)'] = p.ra.to_string(u.hour, sep=":")

        moving_objects['Decl.'].unit = "deg"
        moving_objects['Decl.'] = p.dec.to_string(
            u.deg, sep=":", alwayssign=True)

        moving_objects['x'].unit = "pixel"
        moving_objects['x'].info.format = '0.4f'
        moving_objects['y'].unit = "pixel"
        moving_objects['y'].info.format = '0.4f'
        moving_objects['Background'].unit = "count"
        moving_objects['Background'].info.format = '0.3f'
        moving_objects['Mag'].unit = "mag"
        moving_objects['Mag'].info.format = '0.4f'
        moving_objects['MagErr'].unit = "mag"
        moving_objects['MagErr'].info.format = '0.4f'
        moving_objects['Flux'].unit = "count"
        moving_objects['Flux'].info.format = '0.3f'
        moving_objects['FluxErr'].unit = "count"
        moving_objects['FluxErr'].info.format = '0.3f'
        moving_objects['Elongation'].info.format = '0.3f'
        moving_objects['FWHM'].unit = 'pixel'
        moving_objects['FWHM'].info.format = '0.2f'
        moving_objects['Sky Motion'].unit = u.arcsec/u.min
        moving_objects['Sky Motion'].info.format = '0.2f'
        moving_objects['Sky Motion'] = moving_objects['Sky Motion'] * 3600 * 180 /np.pi
        with open('{0}/results.txt'.format(outdir), 'w') as f:
            f.seek(0, os.SEEK_END)
            print('========================================================\n')
            print('MOVING OBJECTS:\n')
            print(moving_objects)
            f.write('# MOVING OBJECTS:\n')
            ascii.write(moving_objects, f)

    if uncertain_objects.size:

        uncertain_objects = pd.DataFrame.from_records(uncertain_objects,
                                                      columns=COLUMNS)

        uncertain_objects = uncertain_objects.reindex(NEWCOLS, axis=1)
        uncertain_objects[['FileID',
                           'Flags',
                           'ObjectID']] = uncertain_objects[[
                               'FileID',
                               'Flags',
                               'ObjectID']].astype(int)

        uncertain_objects = QTable.from_pandas(uncertain_objects)

        p = SkyCoord(uncertain_objects['R.A. (J2000)'] *
                     u.degree, uncertain_objects['Decl.'] * u.degree)

        uncertain_objects['R.A. (J2000)'].unit = "hourangle"
        uncertain_objects['R.A. (J2000)'] = p.ra.to_string(u.hour, sep=":")

        uncertain_objects['Decl.'].unit = "deg"
        uncertain_objects['Decl.'] = p.dec.to_string(
            u.deg, sep=":", alwayssign=True)

        uncertain_objects['x'].unit = "pixel"
        uncertain_objects['x'].info.format = '0.4f'
        uncertain_objects['y'].unit = "pixel"
        uncertain_objects['y'].info.format = '0.4f'
        uncertain_objects['Background'].unit = "count"
        uncertain_objects['Background'].info.format = '0.3f'
        uncertain_objects['Mag'].unit = "mag"
        uncertain_objects['Mag'].info.format = '0.4f'
        uncertain_objects['MagErr'].unit = "mag"
        uncertain_objects['MagErr'].info.format = '0.4f'
        uncertain_objects['Flux'].unit = "count"
        uncertain_objects['Flux'].info.format = '0.3f'
        uncertain_objects['FluxErr'].unit = "count"
        uncertain_objects['FluxErr'].info.format = '0.3f'
        uncertain_objects['Elongation'].info.format = '0.3f'
        uncertain_objects['FWHM'].unit = 'pixel'
        uncertain_objects['FWHM'].info.format = '0.2f'
        uncertain_objects['Sky Motion'].unit = u.arcsec/u.min
        uncertain_objects['Sky Motion'].info.format = '0.2f'
        uncertain_objects['Sky Motion'] = uncertain_objects['Sky Motion'] * 3600 * 180 /np.pi
        with open('{0}/results.txt'.format(outdir), 'a') as f:
            f.seek(0, os.SEEK_END)
            print('========================================================\n')
            print('UNCERTAIN OBJECTS:\n')
            print(uncertain_objects)
            f.write('# UNCERTAIN OBJECTS:\n')
            ascii.write(uncertain_objects, f)

    try:
#        n_moving = len(set(moving_objects['ObjectID']))
        n_moving = len(np.unique(moving_objects['ObjectID']))
        

    except (AttributeError,IndexError):
        n_moving = 0

    try:
        n_uncertain=len(np.unique(uncertain_objects['ObjectID']))
#        n_uncertain = len(uncertain_objects.ObjectID.unique())
       
    except (AttributeError,IndexError):
        n_uncertain = 0

    print('\nA-Track has detected',
          n_moving, 'moving objects and',
          n_uncertain,
          'uncertain objects.')

    if not arguments.skip_mpcreport:
        fileops = io.FileOps()
        timeops = astronomy.TimeOps()
        fitsops = astronomy.FitsOps()
        astcalc = astronomy.AstCalc()

        images_dir = fitsdir
        the_res_file = "{0}/results.txt".format(outdir)

        magnitude = float(config.get('mpcreport', 'LIM_MAG'))
        radius = float(config.get('mpcreport', 'RADIUS'))
        output = "{0}/mpc_out.txt".format(outdir)
        database = config.get('mpcreport', 'MPC_DATABASE_PATH')
        observatory = config.get('mpcreport', 'OBSERVATORY')

        print("Analysing A-Track result file...")

        my_files = fileops.get_file_list(images_dir)
        res_file = fileops.read_res(the_res_file)
        # print(res_file)

        try:
            hdu1 = fits.open(my_files[0])
            wsc_check = hdu1[0].header['ctype1']
            wcs_file = my_files[0]
        except:
            solve_wcs = astcalc.solve_field(my_files[0],
                                            ra_keyword=str(config.get('mpcreport',
                                                                      'RA')),
                                            dec_keyword=str(config.get('mpcreport',
                                                                       'DEC')),
                                            )
            if not solve_wcs:
                raise SystemExit

            root, extension = os.path.splitext(my_files[0])
            wcs_file = root + "_new.fits"

        observer = config.get('mpcreport', 'OBSERVER')

        if observer == 'OBSERVER':
            observer = fitsops.get_header(my_files[0],
                                          config.get('mpcreport',
                                                     'OBSERVER'))

        telescope = fitsops.get_header(my_files[0],
                                       config.get('mpcreport', 'TELESCOPE'))
        contact = config.get('mpcreport', 'CONTACT')
        catalog = config.get('mpcreport', 'CATALOG')

        print("----------------MPC Report File-----------------------")

        h = fitsops.return_out_file_header(observer=observer, tel=telescope,
                                           code=observatory,
                                           contact=contact,
                                           catalog=catalog)

        out_file = open(output, "w")
        out_file.write("{0}\n".format(h))
        print(h)
        for i in res_file:
            theid, frame, x, y, flux = i

            coors = astcalc.xy2sky(wcs_file, x, y)

            if not coors:
                coors = astcalc.xy2skywcs(wcs_file, x, y)

            coors2 = astcalc.xy2sky2(wcs_file, x, y)

            if not coors2:
                coors2 = astcalc.xy2sky2wcs(wcs_file, x, y)

            coors2ra = coors2.ra.degree
            coors2dec = coors2.dec.degree

            fltr = fitsops.get_header(my_files[0],
                                      config.get('mpcreport',
                                                 'FILTER'))
            fltr = str(fltr).strip().replace(" ", "_")

            tm = timeops.get_timestamp_exp(my_files[int(frame)])
            tmm = timeops.convert_time_format(tm)

            mag = astcalc.flux2mag(flux)

            # ccoor = afits_op.center_finder(wcs_file)

            namesky = astcalc.find_skybot_objects(tm,
                                                  coors2ra,
                                                  coors2dec)
            # print(namesky)

            for u in range(len(namesky)):
                # justID = namesky[u][0]
                justname = namesky[u][1]

                if astcalc.is_object(astcalc.radec2wcs(namesky[u][2],
                                                       namesky[u][3]),
                                     coors2):
                    mpcname = fileops.find_if_in_database_name(database,
                                                               justname)
                    if len(mpcname) == 5:
                        spc = "         "
                    elif len(mpcname) > 5:
                        spc = "  "

                    print("{0}{1}{2} {3}          {4} {5}      {6}".format(mpcname,
                                                                           spc,
                                                                           tmm,
                                                                           coors,
                                                                           mag,
                                                                           fltr,
                                                                           observatory))

                    out_file.write("{0}{1}{2} {3}          {4} {5}      {6}\n".format(
                        mpcname,
                        spc,
                        tmm,
                        coors,
                        mag,
                        fltr,
                        observatory))
                    break
                else:
                    p = "       NO{:03.0f}* {} {}          {} {}      {}".format(
                        theid,
                        tmm,
                        coors,
                        mag,
                        fltr,
                        observatory)

                    print(p)

                    out_file.write("{0}\n".format(p))
                    break
        print("----- end -----")
        out_file.write("----- end -----")
        out_file.close()

    if not arguments.skip_pngs:
        print('\nCreating PNG files...\n')

        if len(moving_objects) > 0 and len(uncertain_objects) > 0:
            objects = vstack([moving_objects, uncertain_objects],
                             metadata_conflicts='silent')
        elif not len(moving_objects) > 0 and len(uncertain_objects) > 0:
            objects = uncertain_objects
        elif not len(uncertain_objects) > 0 and len(moving_objects) > 0:
            objects = moving_objects

        images = sorted(glob.glob(fitsdir + '/*.fits'))

        for i, image in enumerate(images):
            asteroid = objects[objects['FileID'] == i]
            visuals.fits2png(image, outdir, asteroid)
            print('{0} converted to png.'.format(image))

        elapsed = int(time.time() - start)
        print('\nPNG conversion completed.')
        print('Elapsed Time: {0} min {1} sec.'
              .format(elapsed // 60, elapsed % 60))

        if not arguments.skip_gif:
            print('\nCreating GIF (animation) file...')
            os.popen('convert -delay 20 -loop 0 ' +
                     '{0}/*.png {0}/animation.gif'.format(outdir))
            print('{0}/animation.gif created.'.format(outdir))

    print('Elapsed Time: {0} min {1} sec.'.format(elapsed // 60, elapsed % 60))
    print()
