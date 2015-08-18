def reduce_ec_xrt(obsid,DownloadsDir ='/Users/mcorcora/swift/tarfiles/' 
DesiredDirectory = '/Users/mcorcora/swift/quicklook/'
TemplateDirectory=DesiredDirectory+"templates/"
import os, sys, subprocess,glob , shutil, pyfits, urllib
from pprint import pprint ##allows you to print listings
DownloadsDir ='/Users/mcorcora/swift/tarfiles/' #Directory where file is currently placed in
DesiredDirectory = '/Users/mcorcora/swift/quicklook/'#Desired directory of the file
TemplateDirectory=DesiredDirectory+"templates/"
try:
	caldb=os.environ['CALDB']
except:
	print "CALDB not defined; STOPPING"
	sys.exit(0) # exits the script
print "$CALDB = %s" % caldb

#Required: Locate the tar file and copy the file into the desired directory.
#Solution:
os.chdir(DownloadsDir)# Changed directory to the Downloads directory
try :
    TarFilename = glob.glob("sw000*.tar")[0] #Locates the first file in the array with the '.tar' extension
except: 
    print "Cannot find '*.tar' file. Please verify that the file is in the "+DownloadsDir+" directory."
    print "The current working directory contains the following files: "
    pprint(os.listdir(DownloadsDir))
    sys.exit(0) #exits the script
print "Move", TarFilename, "to", DesiredDirectory+TarFilename #prints the directory the file should be moved too
os.rename(DownloadsDir + TarFilename,DesiredDirectory+TarFilename) #moves the files from the DownloadsDir to the DesiredDirectory
os.chdir(DesiredDirectory) #changes directories to the required directory


# In[3]:

#Given: File
import tarfile

#Required: untar the file 
#Solution:
theTarFile = TarFilename# tar file to extract
extractTarPath = '.' # tar file path to extract
tfile = tarfile.open(theTarFile) # open the tar file
if tarfile.is_tarfile(theTarFile):
    # list all contents
    print "tar file contents:"
    print tfile.list(verbose=False)
    # extract all contents
    tfile.extractall(extractTarPath)
else:
    print theTarFile + " is not a tarfile."
print "Untar complete!"


### Run XRT Pipeline

# In[4]:

#Given:
os.chdir(DesiredDirectory) #changes Directory to the Template Directory
Filename = TarFilename[2:13] #collects the ObsID
src1 = TemplateDirectory+"run_xrtpipeline_jamar_Temp.csh" #Location of XRTE pipeline Template
dst1 = DesiredDirectory+"run_xrtpipeline_jamar.csh" #Duplicate template
shutil.copy2(src1, dst1)
LASTKNOWN ="00000000000"#change file name from
CURRENT = Filename #change file name to
XRT = "run_xrtpipeline_jamar.csh" #name of file to edit

#Required: Replace all the numbers in the text, Run XRT Pipeline,
#solution:
text = open(XRT).read() #open the file as a text file
open(XRT, "w").write(text.replace(LASTKNOWN, CURRENT)) #replace the LASTKNOWN with the CURRENT obs ID
print "Running XRT pipeline on the following file:", Filename
print os.getcwd()
os.system("source "+ dst1) #run XRT pipline script


### Run Xselect

# In[151]:

#Given:
XselectDir = DesiredDirectory+"work/"+Filename+"/xsel/"
os.chdir(XselectDir)
src2 = TemplateDirectory+"run_xselect_Temp.xco" #Location of XRT pipeline Template
dst2 = XselectDir+"run_xselect.xco"#new destination for the XRT pipeline file
src3 = TemplateDirectory+"run_xselect_Temp2.xco"
dst3 = XselectDir+"run_xselect2.xco"

#Required: Open Xselect, read event file, promt user to select region files.
#Solution:
print "The current working directory is:", os.getcwd()
#shutil.copy2(src2, dst2) #copies xselect command file into xselect folder
XSELECT = "run_xselect.xco"#name of xselect command file to edit
XSELECTemp = "run_xselect_Temp.xco"#name of xselect command file to edit
tt = open(TemplateDirectory+XSELECTemp,"r") #opens xselect template command file 
a=tt.read()
tt.close()
b=a.replace("DESIREDDIRECTORY",DesiredDirectory).replace("OBSID",CURRENT)
xco=open(XselectDir+XSELECT,"w")
xco.write(b)
xco.close()
#open(XSELECT, "w").write(text.replace("OBSID", CURRENT)) #updates Lastknown name in file to current file name
#open(XSELECT, "w").write(text.replace("DESIREDDIRECTORY", DesiredDirectory)) #updates Lastknown name in file to current file name
shutil.copy2(src3, dst3) #copies second xselect command file into xselect folder
cmd="xselect @"+XselectDir+XSELECT
print cmd
os.system(cmd) #Runs Xselect command file opened terminal window


#### Copy/Group pha files

# In[152]:

#Given:
XspectDir = DesiredDirectory+"work/"+Filename+"/xspec/" #specifies the location of the Xspec directory
#Required: copy pha files into xspec directory.
#Solution:
os.chdir(XselectDir)# Changed directory to the Xselect directory
for file in glob.glob("*.pha"): #Locates all the files in the current direcotry with the .pha extension
    PhaFilename = file #set the file name to PhaFilename
    src4 = XselectDir+PhaFilename
    dst4 = XspectDir+PhaFilename
    shutil.copy2(src4, dst4) #copies all the pha files in the directory to the required folder
os.chdir(XspectDir)
print "Current working dir :",os.getcwd() #Displays current directory
os.system("grppha ec_src.pha ec_srcbin10.pha comm = 'group min 10' temp = exit") #runs the grppha command file.


#### Make Ancillary response Files

# In[199]:

#Given:
src5 = TemplateDirectory+"mk_xrt_arfs_jamar_Temp.csh" #Location of XRT make arf file Template
dst5 = XspectDir+"mk_xrt_arfs_jamar.csh" #Duplicate template
#shutil.copy2(src5, dst5)
ARF = "mk_xrt_arfs_jamar.csh" #name of file to edit

#Required: Replace all the numbers in the text, Run XRT Pipeline,
#solution:

tt = open(src5,"r") #opens xselect template command file 
a=tt.read()
tt.close()
b=a.replace("DESIREDDIRECTORY",DesiredDirectory).replace("OBSID",CURRENT)
arf=open(dst5,"w")
arf.write(b)
arf.close()

os.system("source "+ dst5) #make Ancillary Response File. 


#### Locate the Response file

# In[8]:
 
os.chdir(XspectDir) 

hdulist = pyfits.open('ec_srcbin10.arf') #open the Fits file.
hdulist.info() #show the information in the fits file
hdulist[1].header['RESPFILE'] #open the header file and locate the response file. 
Response = hdulist[1].header['RESPFILE']
hdulist.close()
#CALDB=os.environ['CALDB']
#src6 = CALDB+'/data/swift/xrt/cpf/rmf/'
#shutil.copy2(src6+Response, XspectDir+Response)

print "Getting rmf file %s from remote CALDB" % Response
swiftrmf="http://heasarc.gsfc.nasa.gov/FTP/caldb/data/swift/xrt/cpf/rmf/"
urllib.urlretrieve(swiftrmf+Response,XspectDir+Response)

# In[115]:

#Given:
src7 = TemplateDirectory+"ec_srcbin10all.xcm" #Location of XRTE make arf file Template
dst7 = XspectDir+"ec_srcbin10.xcm" #Duplicate template
#shutil.copy2(src7, dst7)
TempResponse = "swxwt00000000000.rmf"

tt = open(src7,"r") #opens xselect template command file 
a=tt.read()
tt.close()
#b=a.replace(TempResponse,src6+Response)
b=a.replace(TempResponse,XspectDir+Response)
rmf=open(dst7,"w")
rmf.write(b)
rmf.close()

os.system("xspec - ec_srcbin10.xcm")


# In[ ]:



