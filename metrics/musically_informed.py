import partitura as pt
from mpteval.articulation import articulation_metrics_from_perf
from mpteval.timing import timing_metrics_from_perf
from mpteval.harmony import harmony_metrics_from_perf
from mpteval.dynamics import dynamics_metrics_from_perf


def compute_musically_informed_metrics(true_MIDI, pred_MIDI, namecheck=True):
    '''Computes all Musically Informed Metrics (MIMs) for a given pair of ground truth and prediction MIDI files.'''
    true_MIDI_basename = true_MIDI.split('/')[-1].split('.')[0]
    pred_MIDI_basename = pred_MIDI.split('/')[-1].split('.')[0]
    if namecheck:
        assert true_MIDI_basename in pred_MIDI_basename, f'{true_MIDI_basename} and {pred_MIDI_basename} files do not match.'
    
    true_perf = pt.load_performance_midi(true_MIDI)
    pred_perf = pt.load_performance_midi(pred_MIDI)

    # articulation
    art_metrics = articulation_metrics_from_perf(true_perf, pred_perf)
    melody_kor_corr_64, bass_kor_corr_64, ratio_kor_corr_64, _ = art_metrics[0]
    
    # timing
    timing_metrics = timing_metrics_from_perf(true_perf, pred_perf)
    melody_ioi_corr = timing_metrics[0]['melody_ioi_corr']
    acc_ioi_corr = timing_metrics[0]['acc_ioi_corr']
    
    # harmony ['cd_corr', 'cm_corr', 'ts_corr']
    harmony_metrics = harmony_metrics_from_perf(true_perf, pred_perf)
    cloud_diameter_corr = harmony_metrics[0]['cloud_diameter_corr']
    cloud_momentum_corr = harmony_metrics[0]['cloud_momentum_corr']
    tensile_strain_corr = harmony_metrics[0]['tensile_strain_corr']

    # dynamics
    dyn_corr = dynamics_metrics_from_perf(true_perf, pred_perf)

    metrics = {
        'piece_id': true_MIDI_basename,
        # articulation
        'melody_kor_corr_64': melody_kor_corr_64, 'bass_kor_corr_64': bass_kor_corr_64, 'ratio_kor_corr_64': ratio_kor_corr_64,
        # timing
        'melody_ioi_corr': melody_ioi_corr, 'acc_ioi_corr': acc_ioi_corr,
        # harmony
        'cloud_diameter_corr': cloud_diameter_corr, 'cloud_momentum_corr': cloud_momentum_corr, 'tensile_strain_corr': tensile_strain_corr,
        # dynamics
        'dyn_corr': dyn_corr
    }
    
    return metrics