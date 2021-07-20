# from AtmosPhysDriverStatein-OUT
OUT_VARS_APDS = ["IPD_vvl"]
# Serialized Variables from GFSPhysicsDriver-In Savepoint
IN_VARS_GFSPD = [
    "IPD_dtp",
    "IPD_area",
    "IPD_gq0",
    "IPD_gt0",
    "IPD_gu0",
    "IPD_gv0",
    "IPD_kdt",
    "IPD_levs",
    "IPD_lradar",
    "IPD_ntrac",
    "IPD_phii",
    "IPD_prsi",
    "IPD_qgrs",
    "IPD_refl_10cm",
    "IPD_tgrs",
    "IPD_xlon",
    "IPD_vvl",
    "IPD_prsl",
    "IPD_ugrs",
    "IPD_vgrs",
]

# Serialized Variables from GFSPhysicsDriver-Out Savepoint
OUT_VARS_GFSPD = ["IPD_gq0", "IPD_gt0", "IPD_gu0", "IPD_gv0"]

# Serialized Variables for inputs into get_prs_fv3
IN_VARS_PRS = [
    "prs_ix",
    "prs_levs",
    "prs_ntrac",
    "prs_phii",
    "prs_prsi",
    "prs_tgrs",
    "prs_qgrs",
    "prs_del",
    "prs_del_gz",
]

# Serialized Variables for outputs from get_prs_fv3
OUT_VARS_PRS = ["prs_del", "prs_del_gz"]

# Serialized Variables for inputs into get_phi_fv3
IN_VARS_PHI = [
    "phi_del_gz",
    "phi_gq0",
    "phi_gt0",
    "phi_ix",
    "phi_levs",
    "phi_ntrac",
    "phi_phii",
    "phi_phil",
]

# Serialized Variables for outputs from get_phi_fv3
OUT_VARS_PHI = ["phi_del_gz", "phi_phii", "phi_phil"]

IN_VARS_MICROPH = [
    "mph_area",
    "mph_delp",
    "mph_dtp_in",
    "mph_dz",
    "mph_graupel0",
    "mph_ice0",
    "mph_im",
    "mph_land",
    "mph_levs",
    "mph_lradar",
    "mph_p123",
    "mph_pt",
    "mph_pt_dt",
    "mph_qa1",
    "mph_qa_dt",
    "mph_qg1",
    "mph_qg_dt",
    "mph_qi1",
    "mph_qi_dt",
    "mph_ql1",
    "mph_ql_dt",
    "mph_qn1",
    "mph_qr1",
    "mph_qr_dt",
    "mph_qs1",
    "mph_qs_dt",
    "mph_qv1",
    "mph_qv_dt",
    "mph_rain0",
    "mph_refl",
    "mph_reset",
    "mph_seconds",
    "mph_snow0",
    "mph_udt",
    "mph_uin",
    "mph_vdt",
    "mph_vin",
    "mph_w",
]

OUT_VARS_MICROPH = [
    "mph_graupel0",
    "mph_ice0",
    "mph_pt_dt",
    "mph_qa_dt",
    "mph_qg_dt",
    "mph_qi1",
    "mph_qi_dt",
    "mph_ql_dt",
    "mph_qr_dt",
    "mph_qs1",
    "mph_qs_dt",
    "mph_qv_dt",
    "mph_rain0",
    "mph_refl",
    "mph_snow0",
    "mph_udt",
    "mph_vdt",
    "mph_w",
]

OUT_VARS_FVDYN = [
    "cxd",
    "cyd",
    "delp",
    "delz",
    "diss_estd",
    "mfxd",
    "mfyd",
    "omga",
    "pe",
    "peln",
    "phis",
    "pk",
    "pkz",
    "ps",
    "pt",
    "q_con",
    "qcld",
    "qgraupel",
    "qice",
    "qliquid",
    "qo3mr",
    "qrain",
    "qsgs_tke",
    "qsnow",
    "qvapor",
    "u",
    "ua",
    "uc",
    "v",
    "va",
    "vc",
    "w",
]

IN_VAR_APDS = [
    "IPD_atm_ts",
    "IPD_diss_est",
    "IPD_dycore_hydrostatic",
    "IPD_nwat",
    "IPD_pgr",
    "IPD_phii",
    "IPD_phil",
    "IPD_prsi",
    "IPD_prsik",
    "IPD_prsl",
    "IPD_prslk",
    "IPD_qgrs",
    "IPD_tgrs",
    "IPD_ugrs",
    "IPD_vgrs",
    "IPD_vvl",
]

OUT_VAR_APDS = [
    "IPD_atm_ts",
    "IPD_diss_est",
    "IPD_dycore_hydrostatic",
    "IPD_nwat",
    "IPD_pgr",
    "IPD_phii",
    "IPD_phil",
    "IPD_prsi",
    "IPD_prsik",
    "IPD_prsl",
    "IPD_prslk",
    "IPD_qgrs",
    "IPD_tgrs",
    "IPD_ugrs",
    "IPD_vgrs",
    "IPD_vvl",
]

IN_VARS_FVPHY = [ 
     "delp", 
     "omga", 
     "pe", 
     "peln", 
     "phis", 
     "pk", 
     "pkz", 
     "ps", 
     "pt", 
     "q_con", 
     "qcld", 
     "qgraupel", 
     "qice", 
     "qliquid", 
     "qo3mr", 
     "qrain", 
     "qsnow", 
     "qvapor", 
     "t_dt", 
     "u", 
     "u_dt", 
     "u_srf", 
     "ua", 
     "v", 
     "v_dt", 
     "v_srf", 
     "va", 
     "w" 
] 

OUT_VARS_FVPHY = [ 
     "delp", 
     "omga", 
     "pe", 
     "peln", 
     "phis", 
     "pk", 
     "pkz", 
     "ps", 
     "pt", 
     "q_con", 
     "qcld", 
     "qgraupel", 
     "qice", 
     "qliquid", 
     "qo3mr", 
     "qrain", 
     "qsnow", 
     "qvapor", 
     "u", 
     "ua", 
     "v", 
     "va", 
     "w" 
] 