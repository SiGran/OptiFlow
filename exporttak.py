"""
Only tested using IronPython 2.7!
utils.py has to be in path or same folder as exporttak.py
exporttak.py processes the .tak takes acquired from experiments. Basis for this scripts came from the folder:
C:\Program Files\OptiTrack\Motive\MotiveBatchProcessor\ExampleScripts\ExporterScripts
Functionality now:



Functionalities to be added in the future:

Author: Simon @LEOMO
"""


import sys
import clr
import logging

#Create and configure logger
logging.basicConfig(filename="tak_export_log.log",
                    format='%(asctime)s | %(levelname)s:	%(message)s',
                    filemode='w')
logger = logging.getLogger(".Tak exporter")
#Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)

# IronPython 2.7 must be installed in order to use python scripting.
sys.path.append(r'C:\Program Files\OptiTrack\Motive\MotiveBatchProcessor\platforms')

# for exporting to C3D take limit is
import os

# Add a reference to the NMotive assembly
clr.AddReference("NMotive")

from System import *
# Import everything from NMotive.
from NMotive import *
from utils import processAndExportTakes, takesInDirectory, changeFileExtension

# ======================================================================================================================
# FUNCTIONS
# ======================================================================================================================


def ProcessTake_tocsv(take, output_file, quaternionformat=True):
	# Construct an NMotive CSV exporter object with the desired options.
	exporter = CSVExporter()
	# -== CSVExporter Class ==-
	"""
	Rotation type determines whether Quaternion or Euler Angles is used for orientation convention in exported CSV files. 
	For Euler rotation, right-handed coordinate system is used and all different orders (XYZ, XZY, YXZ, YZX, ZXY, ZYX) 
	of elemental rotation is available. More specifically, the XYZ order indicates pitch is degree about the X axis, 
	yaw is degree about the Y axis, and roll is degree about the Z axis.
	"""
	if quaternionformat:
		exporter.RotationType = Rotation.QuaternionFormat  # QuaternionFormat, XYZ, XZY, YXZ, YZX, ZXY, ZYX
	else:
		exporter.RotationType = Rotation.XYZ

	exporter.Units = LengthUnits.Units_Millimeters
	exporter.UseWorldSapceCoordinates = False
	exporter.WriteUnlabeledMarkers = False
	#exporter.WriteBoneMarkers = True
	#exporter.WriteBones = True
	exporter.WriteHeader = True
	exporter.WriteMarkers = True
	exporter.WriteQualityStats = False
	exporter.WriteRigidBodies = True
	exporter.WriteRigidBodyMarkers = True
	# -== Exporter Class ==-
	# exporter.StartFrame = 0
	# exporter.EndFrame = 1000
	# exporter.FrameRate = 120
	# exporter.Scale = 1

	# Create a file in the same folder with the same name, but with a different extension.
	# path, full_filename = os.path.split(take.FileName)
	# filename_no_extension, extension = os.path.splitext(full_filename)
	# outputFile = path + "/" + filename_no_extension + ".csv"

	# Export the file.
	# progress.SetMessage("Writing to File")
	# progress.SetProgress(float(0.1))
	return exporter.Export(take, output_file, True)
# ----------------------------------------------------------------------------------------------------------------------


def ProcessTake_toc3d(take, output_file, progress):
	# Construct an NMotive C3D exporter object with the desired options.
	exporter = C3DExporter()
	#-== C3DExporter Class ==-
	exporter.ColonNameSeparator = False
	exporter.RenameUnlabeledMarkers = False
	exporter.Units = LengthUnits.Units_Centimeters
	exporter.UseTimeCode = True
	exporter.UseZeroBasedFrameIndex = True
	exporter.WriteFingerTipMarkers = False
	exporter.WriteUnlabeledMarkers = False
	exporter.XAxis = Axis.Axis_NegativeX	    # Axis_PositiveX, Axis_NegativeX
	exporter.YAxis = Axis.Axis_PositiveZ	    # Axis_PositiveY, Axis_NegativeY
	exporter.ZAxis = Axis.Axis_PositiveY		# Axis_PositiveZ, Axis_NegativeZ
	# # Export the file.
	# progress.SetMessage("Writing to File")
	# progress.SetProgress( float(0.1) )
	return exporter.Export(take, output_file, True)
# ======================================================================================================================
# Main function for processing .tak
# ======================================================================================================================
# folder = 'G:/My Drive/Project OptiFlow/data'
def process_tak(folder):
	try:
		os.path.isdir(folder)
	except NotADirectoryError:
		logger.error("No directory found at: %s", folder)

	logger.info('entering the directory: %s', folder)
	exporterC3D = C3DExporter()
	exporterCSV = CSVExporter()

	processAndExportTakes(folder, [], exporterC3D)
	processAndExportTakes(folder, [], exporterCSV)



def process_taks_for_csv(folder):
	for take in takesInDirectory(folder):
		output_file = changeFileExtension(take, '_quat', 'csv')
		output_folder = os.path.join(folder, 'processed_to_csv')
		if not os.path.isdir(output_folder):
			os.mkdir(output_folder)
		output_path = os.path.join(output_folder, output_file)
		ProcessTake_tocsv(take, output_path)
		output_file = changeFileExtension(take, '_XYZ', 'csv')
		output_path = os.path.join(output_folder, output_file)
		ProcessTake_tocsv(take, output_path, quaternionformat=False)
	return

folder = 'G:/My Drive/R&D Test Data/2019/20190808_S&C_ConorSimon_SquatsRR/MOCAP_reconstructed'

process_taks_for_csv(folder)






	# for dirpath, dirname, filenames in os.walk(folder):
	# 	# Go through filenames in current folder
	#
	# 	for file in filenames:
	# 		# only take the .tak files
	# 		filename, extension = os.path.splitext(file)
	# 		if extension == 'tak':
	# 			print('Processing', file)
	# 			c3d_path = os.path.join(dirpath, 'C3Ds')
	# 			if not os.path.exists(c3d_path):
	# 				logger.info("created directory: %s", c3d_path)
	# 				os.mkdir(c3d_path)
	# 			csv_path = os.path.join(dirpath, 'CSVs')
	# 			if not os.path.exists(csv_path):
	# 				logger.info("created directory: %s", csv_path)
	# 				os.mkdir(csv_path)
	#
	# 			output_file_c3d = os.path.join(c3d_path, filename + '.c3d')
	# 			output_file_csv = os.path.join(csv_path, filename + '.csv')
	# 			progress = ProgressIndicator()
	# 			progress.SetMessage("Accessing file")
	# 			progress.SetProgress(float(0.0))
	# 			logger.debug("Loading take %s", file)
	# 			take = Take(os.path.join(dirpath, file))
	# 			logger.info("Begin exporting the take to C3D")
	# 			exported_c3d = ProcessTake_toc3d(take, output_file_c3d, progress)
	# 			logger.info("Begin exporting the take to CSV")
	# 			ProcessTake_tocsv(take, output_file_csv, progress)