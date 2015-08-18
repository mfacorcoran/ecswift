def reduce_ec_xrt(obsid,ProcDir = '/Users/corcoran/Dropbox/Eta_Car/swift/quicklook', TemplateDirectory='/Users/corcoran/Dropbox/Eta_Car/swift/quicklook/templates', pcmode=False):
    """
    For a given obsid, this routine runs 
      1) runs xrt pipeline on the downloaded data (in the ProcDir directory) and outputs to the work directory
      2) runs xselect to time filter, region filter and extract the source and background spectra, and copy them to the xsel work  directory; 
      3) links the pha files in the work/obsid/xspec directory and runs grppha
      4) runs xrtmkarf in the work/obsid/xspec directory
      5) then fits the grouped spectrum with xspec and outputs the results
      
      Directory structure:
      ProcDir is where the data directory from the archive (or untarred from the quicklook data) is located
      xrtpipeline outputs to ProcDir/work/obsid
      xsel is run in ProcDir/work/obsid/xsel
      xspec is run in ProcDir/work/obsid/xspec

      changes:
      20150818 MFC added flag for analysis of pcmode data (and created associated template file)
     """
    import os, sys, subprocess,glob , shutil, pyfits, urllib, tarfile
    #from pprint import pprint ##allows you to print listings
    # import fit_ecsrcbin10
    obsid = obsid.strip()
    WorkDir = ProcDir+"/work"
    print "Writing Output to %s" % WorkDir
    """
    need to have CALDB defined for xrtpipeline to work
    """
    try:
        caldb=os.environ['CALDB']
    except:
        print "CALDB not defined; Returning"
        return # exits the script
    print "$CALDB = %s" % caldb
        
    ### Run XRT Pipeline
    
    os.chdir(ProcDir) # changes Directory 
    #Filename = TarFilename[2:13] #collects the ObsID
    src1 = TemplateDirectory+"/run_xrtpipeline_jamar_Temp.csh" # Location of XRT pipeline Template
    XRT =  ProcDir+"/run_xrtpipeline_"+obsid+".csh"   #name of file to edit
    print "CREATING Processing Script %s" % XRT
    shutil.copy2(src1, XRT)
    LASTKNOWN ="00000000000"#change file name from
    CURRENT = obsid  
    text = open(XRT).read() #open the file as a text file
    open(XRT, "w").write(text.replace(LASTKNOWN, CURRENT)) #replace the LASTKNOWN with the CURRENT obs ID
    print "Running XRT pipeline on "+ obsid
    print os.getcwd()
    os.system("source "+ XRT) #run XRT pipline script
    
    
    ### Run Xselect
    
    XselectDir = ProcDir+"/work/"+obsid+"/xsel/"
    os.chdir(XselectDir)
    # src2 = TemplateDirectory+"/run_xselect_Temp.xco" #Location of XRT pipeline Template
    # dst2 = XselectDir+"/run_xselect.xco"#new destination for the XRT pipeline file
    src3 = TemplateDirectory+"/run_xselect_Temp2.xco"
    dst3 = XselectDir+"/run_xselect2.xco"
    
    #Required: Open Xselect, read event file, promt user to select region files.
    #Solution:
    print "The current working directory is:", os.getcwd()
    #shutil.copy2(src2, dst2) #copies xselect command file into xselect folder
    XSELECT = "run_xselect.xco"#name of xselect command file to edit
    if pcmode:
        XSELECTemp = "run_xselect_Temp_pc.xco"#name of xselect command file to edit for pcmode data
    else:
        XSELECTemp = "run_xselect_Temp.xco"  # name of xselect command file to edit
    tt = open(TemplateDirectory+"/"+XSELECTemp,"r") #opens xselect template command file 
    a=tt.read()
    tt.close()
    b=a.replace("DESIREDDIRECTORY",ProcDir).replace("OBSID",CURRENT)
    xco=open(XselectDir+XSELECT,"w")
    xco.write(b)
    xco.close()
    #open(XSELECT, "w").write(text.replace("OBSID", CURRENT)) #updates Lastknown name in file to current file name
    #open(XSELECT, "w").write(text.replace("DESIREDDIRECTORY", ProcDir)) #updates Lastknown name in file to current file name
    shutil.copy2(src3, dst3) #copies second xselect command file into xselect folder
    cmd="xselect @"+XselectDir+XSELECT
    print cmd
    os.system(cmd) #Runs Xselect command file opened terminal window
    
    
    #### Copy/Group pha files
    
    # In[152]:
    
    #Given:
    XspectDir = ProcDir+"/work/"+obsid+"/xspec/" #specifies the location of the Xspec directory
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
    src5 = TemplateDirectory+"/mk_xrt_arfs_jamar_Temp.csh" #Location of XRT make arf file Template
    dst5 = XspectDir+"/mk_xrt_arfs_jamar.csh" #Duplicate template
    #shutil.copy2(src5, dst5)
    ARF = "mk_xrt_arfs_jamar.csh" #name of file to edit
    
    #Required: Replace all the numbers in the text, Run XRT Pipeline,
    #solution:
    
    tt = open(src5,"r") #opens xselect template command file 
    a=tt.read()
    tt.close()
    b=a.replace("DESIREDDIRECTORY",ProcDir).replace("OBSID",CURRENT)
    arf=open(dst5,"w")
    arf.write(b)
    arf.close()
    
    os.system("source "+ dst5) #make Ancillary Response File. 
    
    
    #### Locate the Response file
    
    # In[8]:
     
    os.chdir(XspectDir) 
    
    hdulist = pyfits.open('ec_srcbin10.arf') #open the Fits file.
    #hdulist.info() #show the information in the fits file
    #hdulist[1].header['RESPFILE'] #open the header file and locate the response file.
    Response = hdulist[1].header['RESPFILE']
    hdulist.close()
    #CALDB=os.environ['CALDB']
    #src6 = CALDB+'/data/swift/xrt/cpf/rmf/'
    #shutil.copy2(src6+Response, XspectDir+Response)
    
    print "Getting rmf file %s from remote CALDB" % Response
    swiftrmf="http://heasarc.gsfc.nasa.gov/FTP/caldb/data/swift/xrt/cpf/rmf"
    urllib.urlretrieve(swiftrmf+"/"+Response,XspectDir+"/"+Response)
    
#    # fit the spectrum
#    
#    ecwift.fit_ecsrcbin10(obsid, workdir=WorkDir)
#    
# In[115]:
    
#   #Given:
#   src7 = TemplateDirectory+"/ec_srcbin10all.xcm" #Location of XRT make arf file Template
#   dst7 = XspectDir+"/ec_srcbin10.xcm" #Duplicate template
#   #shutil.copy2(src7, dst7)
#   TempResponse = "swxwt00000000000.rmf"
#   
#   tt = open(src7,"r") #opens xselect template command file 
#   a=tt.read()
#   tt.close()
#   #b=a.replace(TempResponse,src6+Response)
#   b=a.replace(TempResponse,XspectDir+"/"+Response)
#   rmf=open(dst7,"w")
#   rmf.write(b)
#   rmf.close()
    return
    
    

