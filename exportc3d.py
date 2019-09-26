"""
MOVED TO leomo-strenght-conditioning
is python 3

author: Simon @leomo
last updated: 2019-09-26
"""
import os
from ezc3d import c3d
import pandas as pd
import numpy as np
import logging
from pathlib import Path
# TODO: make all the paths be done with pathlib
# TODO: clean up the logging
# TODO: also clean up the printing


# Create and configure logger
logging.basicConfig(filename="c3d_export_log.log",
                    format='%(asctime)s | %(levelname)s:	%(message)s',
                    filemode='w')
logger = logging.getLogger('C3D exporter')

# Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)  # change to info when deployed and switch back when debugging

# TODO: Merge multiple files together (if it contains 'part' and a number), for if it's to big
def export_all_c3d_to_csv(folder, markers=False, forceplate=True, print_info=False):
    try:
        os.path.isdir(folder)
    except:
        raise LookupError('Given folder is not a directory')
    logger.info('entering the directory: %s', folder)
    for dirpath, dirname, filenames in os.walk(folder):
        # Go through filenames in current folder
        for file in filenames:
            if 'calibration' in file:
                continue
            filename = Path(file).stem
            extension = Path(file).suffix
            if extension == '.c3d':
                print(f"found file with c3d extension {file}")
                # TODO: could make this all more pythonic by using pathlib Path
                fp_folder = os.path.join(dirpath, 'FP')
                # Create target Directory if don't exist
                if not os.path.exists(fp_folder):
                    logger.info("creating folder %s", fp_folder)
                    os.mkdir(fp_folder)
                mr_folder = os.path.join(dirpath, 'markers')
                if not os.path.exists(mr_folder):
                    logger.info('creating folder %s', mr_folder)
                    os.mkdir(mr_folder)
                load_path = os.path.join(dirpath, file)
                save_fp_path = os.path.join(fp_folder, filename + '.csv')
                save_mr_path = os.path.join(mr_folder, filename + '.csv')
                logger.info('Attempting to process: %s', load_path)
                try:
                    data = c3d(load_path)
                except ValueError:
                    logger.error("The file you tried to parse is not a valid c3d file, it will be skipped from parsing")
                    logger.error(load_path)
                except OSError:
                    print("something's off, continue")
                    continue
                if print_info:
                    # Print the header
                    print("# ---- HEADER ---- #")
                    print(f"Number of points = {data['header']['points']['size']}")
                    print(f"Point frame rate = {data['header']['points']['frame_rate']}")
                    print(f"Index of the first point frame = {data['header']['points']['first_frame']}")
                    print(f"Index of the last point frame = {data['header']['points']['last_frame']}")
                    print("")
                    print(f"Number of analogs = {data['header']['analogs']['size']}")
                    print(f"Analog frame rate = {data['header']['analogs']['frame_rate']}")
                    print(f"Index of the first analog frame = {data['header']['analogs']['first_frame']}")
                    print(f"Index of the last analog frame = {data['header']['analogs']['last_frame']}")
                    print("")
                    print("")
                    # Print the parameters
                    print("# ---- PARAMETERS ---- #")
                    print(f"Number of points = {data['parameters']['POINT']['USED']['value'][0]}")
                    print(f"Name of the points = {data['parameters']['POINT']['LABELS']['value']}")
                    print(f"Point frame rate = {data['parameters']['POINT']['RATE']['value'][0]}")
                    print(f"Number of frames = {data['parameters']['POINT']['FRAMES']['value'][0]}")
                    print("")
                    print(f"Number of analogs = {data['parameters']['ANALOG']['USED']['value'][0]}")
                    print(f"Name of the analogs = {data['parameters']['ANALOG']['LABELS']['value']}")
                    print(f"Analog frame rate = {data['parameters']['ANALOG']['RATE']['value'][0]}")
                    print("")
                    print("")
                    # Print the data
                    print("# ---- DATA ---- #")
                    print(f" = {data['data']['points'][0:3, :, :]}")
                    print(f" = {data['data']['analogs']}")

                # Getting the marker data:
                if markers:
                    mr_data = data['data']['points'][0:3, :, :] # there's some weird 4th dimension dunno what that's about
                    mr_data_2d = mr_data.reshape(1, 3 * len(mr_data[0]), len(mr_data[0][0]), order='F')[0].T
                    mr_labels = data['parameters']['POINT']['LABELS']['value']
                    # For now we've only used 39 markers and the other markers are errors/ only the labels are useful
                    while any("Unlabeled" in marker for marker in mr_labels):  # while because maybe iterate multiple times if insanely many unlabeled and have numerical overflow
                        logger.debug("Starting to remove unlabeled markers. Current dimensions of "
                                     "dataframe: %i by %i", len(mr_data_2d), len(mr_data_2d[0]))
                        all_unlabeled = list(filter(lambda marker: 'Unlabeled' in marker, mr_labels))
                        logger.debug("We found %i unlabeled markers", len(all_unlabeled))
                        for marker in all_unlabeled:
                            mr_labels.remove(marker)
                        logger.debug("After attempting to discard dimensions are: %i by %i", len(mr_data_2d),
                                     len(mr_data_2d[0]))

                    axis = []
                    for i in range(1, len(mr_labels) + 1):
                        axis.append(['X' + str(i), 'Y' + str(i), 'Z' + str(i)])
                    multiple_columns = [np.array(mr_labels).repeat(3), np.array(axis).flatten()]
                    tuple_columns = list(zip(*multiple_columns))
                    header = pd.MultiIndex.from_tuples(tuple_columns)
                    mr_df = pd.DataFrame(mr_data_2d, columns=header)
                    F_s = data['parameters']['POINT']['RATE']['value'][0]  # sample frequency
                    times = [index / F_s for index in range(0, len(mr_data_2d))]
                    mr_df.insert(0, 'Time', times)
                    logger.info("Saving markers to csv as: %s", save_mr_path)

                    mr_df.to_csv(save_mr_path, index=False)

                if forceplate:
                    # Getting the force plate data
                    fp_data = data['data']['analogs'][0].T  # Somehow it's in 3D with first dimension being one, so that one is redundant and pandas likes it transposed
                    fp_labels = data['parameters']['ANALOG']['LABELS']['value']
                    fp_df = pd.DataFrame(fp_data, columns=fp_labels)
                    # Adding in the time column at the start
                    F_s = data['parameters']['ANALOG']['RATE']['value'][0]  # sample frequency
                    times = [index / F_s for index in range(0, len(fp_data))]
                    fp_df.insert(0, 'Time', times)
                    logger.info("Saving force plate data to csv as: %s", save_fp_path)
                    fp_df.to_csv(save_fp_path, index=False)



folder = r'G:\My Drive\R&D Test Data\2019\20190925_S&C_Dylan_Joe&Conor_Jumps'
folder = r"G:\My Drive\R&D Test Data\2019\20190925_S&C_Simon_Joe&Conor_Jumps"
export_all_c3d_to_csv(folder, markers=True)