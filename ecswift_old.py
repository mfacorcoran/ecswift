if __name__ == "__main__":
    """
    run a test
    """
    from ecswift import *
    obsid="00031308041"
    tardir = '/Users/corcoran/Downloads'
    ProcDir = '/Users/corcoran/Dropbox/Eta_Car/swift/quicklook'
    untar_ecswift(obsid, tardir=tardir, ProcDir=ProcDir)
    WorkDir = ProcDir+'/work'
    reduce_ec_xrt(obsid, ProcDir=ProcDir)
    obs, xcm = fit_ecsrcbin10(obsid, WorkDir=WorkDir, emin=2.0, emax=10.0)





	

