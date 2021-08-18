from fv3gfs.physics.physics_state import PhysicsState
from fv3gfs.physics.stencils.get_phi_fv3 import get_phi_fv3
from fv3gfs.physics.stencils.get_prs_fv3 import get_prs_fv3
from fv3gfs.physics.stencils.microphysics import Microphysics, MicrophysicsState
from fv3gfs.physics.global_constants import *
import fv3core.utils.gt4py_utils as utils
from fv3core.utils.typing import FloatField, Float
from fv3core.decorators import FrozenStencil, get_namespace
import gt4py.gtscript as gtscript
from gt4py.gtscript import (
    PARALLEL,
    FORWARD,
    BACKWARD,
    computation,
    horizontal,
    interval,
)
import numpy as np  # used for debugging only
from fv3core.stencils.fv_dynamics import DynamicalCore  # need argspecs for state


def atmos_phys_driver_statein(
    prsik: FloatField,
    phii: FloatField,
    prsi: FloatField,
    delz: FloatField,
    delp: FloatField,
    qvapor: FloatField,
    qliquid: FloatField,
    qrain: FloatField,
    qice: FloatField,
    qsnow: FloatField,
    qgraupel: FloatField,
    qo3mr: FloatField,
    qsgs_tke: FloatField,
    qcld: FloatField,
    pt: FloatField,
    dm: FloatField,
):
    from __externals__ import nwat, ptop, pk0inv, pktop

    with computation(BACKWARD), interval(0, -1):
        phii = phii[0, 0, 1] - delz * grav

    with computation(PARALLEL), interval(...):
        prsik = 1.0e25
        qvapor = qvapor * delp
        qliquid = qliquid * delp
        qrain = qrain * delp
        qice = qice * delp
        qsnow = qsnow * delp
        qgraupel = qgraupel * delp
        qo3mr = qo3mr * delp
    # The following needs to execute after the above (TODO)
    with computation(PARALLEL), interval(...):
        if nwat == 6:
            delp = delp - qliquid - qrain - qice - qsnow - qgraupel

    with computation(PARALLEL), interval(0, 1):
        prsi = ptop

    with computation(FORWARD), interval(1, None):
        prsi = prsi[0, 0, -1] + delp[0, 0, -1]

    with computation(PARALLEL), interval(0, -1):
        prsik = log(prsi)
        qvapor = qvapor / delp
        qliquid = qliquid / delp
        qrain = qrain / delp
        qice = qice / delp
        qsnow = qsnow / delp
        qgraupel = qgraupel / delp
        qo3mr = qo3mr / delp
        qsgs_tke = qsgs_tke / delp

    with computation(PARALLEL), interval(-1, None):
        prsik = log(prsi)

    with computation(PARALLEL), interval(0, 1):
        prsik = log(ptop)

    with computation(PARALLEL), interval(0, -1):
        qmin = 1.0e-10  # set it here since externals cannot be 2D
        qgrs_rad = max(qmin, qvapor)
        rTv = rdgas * pt * (1.0 + con_fvirt * qgrs_rad)
        dm = delp[0, 0, 0]
        delp = dm * rTv / (phii[0, 0, 0] - phii[0, 0, 1])
        delp = min(delp, prsi[0, 0, 1] - 0.01 * dm)
        delp = max(delp, prsi + 0.01 * dm)

    with computation(PARALLEL), interval(-1, None):
        prsik = exp(KAPPA * prsik) * pk0inv

    with computation(PARALLEL), interval(0, 1):
        prsik = pktop


def prepare_microphysics(
    dz: FloatField,
    phii: FloatField,
    wmp: FloatField,
    omga: FloatField,
    qvapor: FloatField,
    pt: FloatField,
    delp: FloatField,
):
    with computation(BACKWARD), interval(...):
        dz = (phii[0, 0, 1] - phii[0, 0, 0]) * rgrav
        wmp = -omga * (1.0 + con_fvirt * qvapor) * pt / delp * (rdgas * rgrav)


@gtscript.function
def forward_euler(q_t0, q_dt, dt):
    return q_t0 + q_dt * dt


def update_physics_state_with_tendencies(
    qvapor: FloatField,
    qliquid: FloatField,
    qrain: FloatField,
    qice: FloatField,
    qsnow: FloatField,
    qgraupel: FloatField,
    qcld: FloatField,
    pt: FloatField,
    ua: FloatField,
    va: FloatField,
    qv_dt: FloatField,
    ql_dt: FloatField,
    qr_dt: FloatField,
    qi_dt: FloatField,
    qs_dt: FloatField,
    qg_dt: FloatField,
    qa_dt: FloatField,
    pt_dt: FloatField,
    udt: FloatField,
    vdt: FloatField,
    qvapor_t1: FloatField,
    qliquid_t1: FloatField,
    qrain_t1: FloatField,
    qice_t1: FloatField,
    qsnow_t1: FloatField,
    qgraupel_t1: FloatField,
    qcld_t1: FloatField,
    pt_t1: FloatField,
    ua_t1: FloatField,
    va_t1: FloatField,
    dt: Float,
):
    with computation(PARALLEL), interval(...):
        qvapor_t1 = forward_euler(qvapor, qv_dt, dt)
        qliquid_t1 = forward_euler(qliquid, ql_dt, dt)
        qrain_t1 = forward_euler(qrain, qr_dt, dt)
        qice_t1 = forward_euler(qice, qi_dt, dt)
        qsnow_t1 = forward_euler(qsnow, qs_dt, dt)
        qgraupel_t1 = forward_euler(qgraupel, qg_dt, dt)
        qcld_t1 = forward_euler(qcld, qa_dt, dt)
        pt_t1 = forward_euler(pt, pt_dt, dt)
        ua_t1 = forward_euler(ua, udt, dt)
        va_t1 = forward_euler(va, vdt, dt)


class Physics:
    def __init__(self, grid, namelist):
        self.grid = grid
        self.namelist = namelist
        origin = self.grid.compute_origin()
        shape = self.grid.domain_shape_full(add=(1, 1, 1))
        self.setup_statein()
        self._dt_atmos = self.namelist.dt_atmos
        self._ptop = 300.0  # hard coded before we can call ak from grid: state["ak"][0]
        self._pktop = (self._ptop / self._p00) ** KAPPA
        self._pk0inv = (1.0 / self._p00) ** KAPPA
        self._prsi = utils.make_storage_from_shape(shape, origin=origin, init=True)
        self._prsik = utils.make_storage_from_shape(shape, origin=origin, init=True)
        self._dm3d = utils.make_storage_from_shape(shape, origin=origin, init=True)
        self._del_gz = utils.make_storage_from_shape(shape, origin=origin, init=True)

        self._get_prs_fv3 = FrozenStencil(
            func=get_prs_fv3,
            origin=self.grid.grid_indexing.origin_full(),
            domain=self.grid.grid_indexing.domain_full(add=(0, 0, 1)),
        )
        self._get_phi_fv3 = FrozenStencil(
            func=get_phi_fv3,
            origin=self.grid.grid_indexing.origin_full(),
            domain=self.grid.grid_indexing.domain_full(add=(0, 0, 1)),
        )
        self._atmos_phys_driver_statein = FrozenStencil(
            func=atmos_phys_driver_statein,
            origin=self.grid.grid_indexing.origin_compute(),
            domain=self.grid.grid_indexing.domain_compute(add=(0, 0, 1)),
            externals={
                "nwat": self._nwat,
                "ptop": self._ptop,
                "pk0inv": self._pk0inv,
                "pktop": self._pktop,
            },
        )
        self._prepare_microphysics = FrozenStencil(
            func=prepare_microphysics,
            origin=self.grid.grid_indexing.origin_compute(),
            domain=self.grid.grid_indexing.domain_compute(),
        )
        self._update_physics_state_with_tendencies = FrozenStencil(
            func=update_physics_state_with_tendencies,
            origin=self.grid.grid_indexing.origin_compute(),
            domain=self.grid.grid_indexing.domain_compute(),
        )
        self._microphysics = Microphysics(grid, namelist)

    def setup_statein(self):
        self._NQ = 8  # state.nq_tot - spec.namelist.dnats
        self._dnats = 1  # spec.namelist.dnats
        self._nwat = 6  # spec.namelist.nwat
        self._p00 = 1.0e5

    def setup_const_from_state(self, state: dict):
        self._ptop = state["ak"][0]
        self._pktop = (self._ptop / self._p00) ** KAPPA
        self._pk0inv = (1.0 / self._p00) ** KAPPA

    def __call__(self, state: dict, rank):
        self.setup_const_from_state(state)
        shape = self.grid.domain_shape_full(add=(1, 1, 1))
        origin = self.grid.compute_origin()
        storage = utils.make_storage_from_shape(shape, origin=origin, init=True)
        state = get_namespace(DynamicalCore.arg_specs, state)
        physics_state = PhysicsState.from_dycore_state(state, storage)
        self._atmos_phys_driver_statein(
            self._prsik,
            physics_state.phii,
            self._prsi,
            physics_state.delz,
            physics_state.delp,
            physics_state.qvapor,
            physics_state.qliquid,
            physics_state.qrain,
            physics_state.qice,
            physics_state.qsnow,
            physics_state.qgraupel,
            physics_state.qo3mr,
            physics_state.qsgs_tke,
            physics_state.qcld,
            physics_state.pt,
            self._dm3d,
        )
        debug = {}
        debug["prsik"] = self._prsik
        debug["phii"] = physics_state.phii
        debug["prsi"] = self._prsi
        debug["delz"] = physics_state.delz
        debug["delp"] = physics_state.delp
        debug["qvapor"] = physics_state.qvapor
        debug["qliquid"] = physics_state.qliquid
        debug["qrain"] = physics_state.qrain
        debug["qice"] = physics_state.qice
        debug["qsnow"] = physics_state.qsnow
        debug["qgraupel"] = physics_state.qgraupel
        debug["qo3mr"] = physics_state.qo3mr
        debug["qsgs_tke"] = physics_state.qsgs_tke
        debug["qcld"] = physics_state.qcld
        debug["pt"] = physics_state.pt
        np.save(
            "integrated_after_prep_physics_stencil_rank_" + str(rank) + ".npy", debug
        )

        self._get_prs_fv3(
            physics_state.phii,
            self._prsi,
            physics_state.pt,
            physics_state.qvapor,
            physics_state.delprsi,
            self._del_gz,
        )
        debug = {}
        debug["phii"] = physics_state.phii
        debug["prsi"] = self._prsi
        debug["pt"] = physics_state.pt
        debug["qvapor"] = physics_state.qvapor
        debug["delp"] = physics_state.delp
        debug["del"] = physics_state.delprsi
        debug["del_gz"] = self._del_gz
        np.save("integrated_after_prsfv3_rank_" + str(rank) + ".npy", debug)
        # If PBL scheme is present, physics_state should be updated here
        self._get_phi_fv3(
            physics_state.pt,
            physics_state.qvapor,
            self._del_gz,
            physics_state.phii,
            physics_state.phil,
        )
        debug = {}
        debug["phii"] = physics_state.phii
        debug["phil"] = physics_state.phil
        debug["pt"] = physics_state.pt
        debug["qvapor"] = physics_state.qvapor
        debug["del_gz"] = self._del_gz
        np.save("integrated_after_phifv3_rank_" + str(rank) + ".npy", debug)
        self._prepare_microphysics(
            physics_state.dz,
            physics_state.phii,
            physics_state.wmp,
            physics_state.omga,
            physics_state.qvapor,
            physics_state.pt,
            physics_state.delp,
        )
        microph_state = physics_state.microphysics(storage)
        self._microphysics(microph_state, rank)
        # Fortran uses IPD interface, here we use var_t1 to denote the updated field
        self._update_physics_state_with_tendencies(
            physics_state.qvapor,
            physics_state.qliquid,
            physics_state.qrain,
            physics_state.qice,
            physics_state.qsnow,
            physics_state.qgraupel,
            physics_state.qcld,
            physics_state.pt,
            physics_state.ua,
            physics_state.va,
            microph_state.qv_dt,
            microph_state.ql_dt,
            microph_state.qr_dt,
            microph_state.qi_dt,
            microph_state.qs_dt,
            microph_state.qg_dt,
            microph_state.qa_dt,
            microph_state.pt_dt,
            microph_state.udt,
            microph_state.vdt,
            physics_state.qvapor_t1,
            physics_state.qliquid_t1,
            physics_state.qrain_t1,
            physics_state.qice_t1,
            physics_state.qsnow_t1,
            physics_state.qgraupel_t1,
            physics_state.qcld_t1,
            physics_state.pt_t1,
            physics_state.ua_t1,
            physics_state.va_t1,
            self._dt_atmos,
        )
        debug = {}
        debug["IPD_gt0"] = physics_state.pt_t1
        debug["IPD_gu0"] = physics_state.ua_t1
        debug["IPD_gv0"] = physics_state.va_t1
        debug["qv_t1"] = physics_state.qvapor_t1
        debug["ql_t1"] = physics_state.qliquid_t1
        debug["qr_t1"] = physics_state.qrain_t1
        debug["qi_t1"] = physics_state.qice_t1
        debug["qs_t1"] = physics_state.qsnow_t1
        debug["qg_t1"] = physics_state.qgraupel_t1
        debug["qa_t1"] = physics_state.qcld_t1
        np.save("integrated_after_physics_driver_rank_" + str(rank) + ".npy", debug)