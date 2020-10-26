# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from ..dti import ProbTrackX


def test_ProbTrackX_inputs():
    input_map = dict(
        args=dict(
            argstr="%s",
        ),
        avoid_mp=dict(
            argstr="--avoid=%s",
            extensions=None,
        ),
        c_thresh=dict(
            argstr="--cthr=%.3f",
        ),
        correct_path_distribution=dict(
            argstr="--pd",
        ),
        dist_thresh=dict(
            argstr="--distthresh=%.3f",
        ),
        environ=dict(
            nohash=True,
            usedefault=True,
        ),
        fibst=dict(
            argstr="--fibst=%d",
        ),
        force_dir=dict(
            argstr="--forcedir",
            usedefault=True,
        ),
        fsamples=dict(
            mandatory=True,
        ),
        inv_xfm=dict(
            argstr="--invxfm=%s",
            extensions=None,
        ),
        loop_check=dict(
            argstr="--loopcheck",
        ),
        mask=dict(
            argstr="-m %s",
            extensions=None,
            mandatory=True,
        ),
        mask2=dict(
            argstr="--mask2=%s",
            extensions=None,
        ),
        mesh=dict(
            argstr="--mesh=%s",
            extensions=None,
        ),
        mod_euler=dict(
            argstr="--modeuler",
        ),
        mode=dict(
            argstr="--mode=%s",
            genfile=True,
        ),
        n_samples=dict(
            argstr="--nsamples=%d",
            usedefault=True,
        ),
        n_steps=dict(
            argstr="--nsteps=%d",
        ),
        network=dict(
            argstr="--network",
        ),
        opd=dict(
            argstr="--opd",
            usedefault=True,
        ),
        os2t=dict(
            argstr="--os2t",
        ),
        out_dir=dict(
            argstr="--dir=%s",
            genfile=True,
        ),
        output_type=dict(),
        phsamples=dict(
            mandatory=True,
        ),
        rand_fib=dict(
            argstr="--randfib=%d",
        ),
        random_seed=dict(
            argstr="--rseed",
        ),
        s2tastext=dict(
            argstr="--s2tastext",
        ),
        sample_random_points=dict(
            argstr="--sampvox",
        ),
        samples_base_name=dict(
            argstr="--samples=%s",
            usedefault=True,
        ),
        seed=dict(
            argstr="--seed=%s",
            mandatory=True,
        ),
        seed_ref=dict(
            argstr="--seedref=%s",
            extensions=None,
        ),
        step_length=dict(
            argstr="--steplength=%.3f",
        ),
        stop_mask=dict(
            argstr="--stop=%s",
            extensions=None,
        ),
        target_masks=dict(
            argstr="--targetmasks=%s",
        ),
        thsamples=dict(
            mandatory=True,
        ),
        use_anisotropy=dict(
            argstr="--usef",
        ),
        verbose=dict(
            argstr="--verbose=%d",
        ),
        waypoints=dict(
            argstr="--waypoints=%s",
            extensions=None,
        ),
        xfm=dict(
            argstr="--xfm=%s",
            extensions=None,
        ),
    )
    inputs = ProbTrackX.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value


def test_ProbTrackX_outputs():
    output_map = dict(
        fdt_paths=dict(),
        log=dict(
            extensions=None,
        ),
        particle_files=dict(),
        targets=dict(),
        way_total=dict(
            extensions=None,
        ),
    )
    outputs = ProbTrackX.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
