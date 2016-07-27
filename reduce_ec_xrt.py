def reduce_ec_xrt(obsid,ProcDir = '/Users/corcoran/Dropbox/Eta_Car/swift/quicklook',
                  TemplateDirectory='/Users/corcoran/Dropbox/Eta_Car/swift/quicklook/templates', pcmode=False):
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
    import os
    import glob
    import shutil
    import pyfits
    import urllib
    from ecswift.utils import create_xrtmkarf_script

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

    src1 = TemplateDirectory+"/run_xrtpipeline_jamar_Temp.csh" # Location of XRT pipeline Template
    XRT =  ProcDir+"/run_xrtpipeline_"+obsid+".csh"   #name of file to edit
    print "CREATING Processing Script %s" % XRT
    shutil.copy2(src1, XRT)
    dummyobsid ="00000000000"#change file name from
    if not pcmode:
        sregfile = "ec_src.reg"
        bregfile = "ec_bkg.reg"
    else:
        sregfile = "ec_src_pc.reg"
        bregfile = "ec_bkg_pc.reg"
    text = open(XRT).read() #open the file as a text file
    b=text.replace(dummyobsid, obsid).replace('TEMPLATEDIR', TemplateDirectory)
    b=b.replace("SRCREG",sregfile).replace("BKGREG",bregfile)
    open(XRT, "w").write(b)
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
    b=a.replace("DESIREDDIRECTORY",ProcDir).replace("OBSID",obsid)
    xco=open(XselectDir+XSELECT,"w")
    xco.write(b)
    xco.close()
    #open(XSELECT, "w").write(text.replace("OBSID", CURRENT)) #updates Lastknown name in file to current file name
    #open(XSELECT, "w").write(text.replace("DESIREDDIRECTORY", ProcDir)) #updates Lastknown name in file to current file name
    shutil.copy2(src3, dst3) #copies second xselect command file into xselect folder
    cmd="xselect @"+XselectDir+XSELECT
    print cmd
    os.system(cmd) #Runs Xselect command file opened terminal window
    
    

    """
    change to xspec directory
    """
    XspectDir = ProcDir+"/work/"+obsid+"/xspec/" #specifies the location of the Xspec directory
    os.chdir(XselectDir)# Changed directory to the Xselect directory

    #### Copy/Group pha files

    for file in glob.glob("*.pha"): #Locates all the files in the current direcotry with the .pha extension
        PhaFilename = file #set the file name to PhaFilename
        src4 = XselectDir+PhaFilename
        dst4 = XspectDir+PhaFilename
        shutil.copy2(src4, dst4) #copies all the pha files in the directory to the required folder
    os.chdir(XspectDir)
    print "Current working dir :",os.getcwd() #Displays current directory
    os.system("grppha ec_src.pha ec_srcbin10.pha comm = 'group min 10' temp = exit") #runs the grppha command file.
    
    
    #### Make Ancillary response Files

    marf_script = create_xrtmkarf_script(obsid, XspectDir, ProcDir=ProcDir, pcmode=pcmode)
    os.system("source "+ marf_script) #make Ancillary Response File.
    
    
    #### Locate the Response file


    hdulist = pyfits.open('ec_srcbin10.arf') #open the Fits file.
    Response = hdulist[1].header['RESPFILE']
    hdulist.close()

    print "Getting rmf file %s from remote CALDB" % Response
    swiftrmf="http://heasarc.gsfc.nasa.gov/FTP/caldb/data/swift/xrt/cpf/rmf"
    urllib.urlretrieve(swiftrmf+"/"+Response,XspectDir+"/"+Response)
    

    return
    
    

