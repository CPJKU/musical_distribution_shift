import partitura as pt
from mpteval.utils import PERF_PIANO_ROLL_PARAMS, create_note_list
from mpteval.benchmarks import compute_transcription_benchmark_framewise, ir_metrics_notewise, ir_metrics_notewise_with_velocity


def compute_standard_benchmark_metrics(true_MIDI, pred_MIDI, namecheck=True):
    '''Computes all benchmark metrics for a given pair of ground truth and prediction MIDI files. Uses partitura
    to load and parse MIDI files.'''
    true_MIDI_basename = true_MIDI.split('/')[-1].split('.')[0]
    pred_MIDI_basename = pred_MIDI.split('/')[-1].split('.')[0]
    if namecheck:
        assert true_MIDI_basename in pred_MIDI_basename, f'{true_MIDI_basename} and {pred_MIDI_basename} files do not match.'

    true_perf = pt.load_performance_midi(true_MIDI)
    true_na = true_perf.note_array()
    
    pred_perf = pt.load_performance_midi(pred_MIDI)
    pred_na = pred_perf.note_array()

    # Frame-level metrics
    true_pr = pt.utils.compute_pianoroll(true_na, remove_silence=False, **PERF_PIANO_ROLL_PARAMS)
    pred_pr = pt.utils.compute_pianoroll(pred_na, remove_silence=False, **PERF_PIANO_ROLL_PARAMS)
    p_frame, r_frame, f_frame = compute_transcription_benchmark_framewise(true_pr, pred_pr)
        
    # Note-level metrics
    true_notelist = create_note_list(true_na, remove_silence=False)
    pred_notelist = create_note_list(pred_na, remove_silence=False)
    p_note_on, r_note_on, f_note_on, _ = ir_metrics_notewise(true_notelist, pred_notelist, onset_only=True)
    p_note_on_off, r_note_on_off, f_note_on_off, _ = ir_metrics_notewise(true_notelist, pred_notelist)
    p_note_on_vel, r_note_on_vel, f_note_on_vel, _ = ir_metrics_notewise_with_velocity(
        true_notelist, pred_notelist, onset_only=True)
    p_note_on_off_vel, r_note_on_off_vel, f_note_on_off_vel, _ = ir_metrics_notewise_with_velocity(
        true_notelist, pred_notelist)
    
    metrics = {
        'piece_id': true_MIDI_basename,
        'p_frame': p_frame, 'r_frame': r_frame, 'f_frame': f_frame,
        'p_note_on': p_note_on, 'r_note_on': r_note_on, 'f_note_on': f_note_on,
        'p_note_on_off': p_note_on_off, 'r_note_on_off': r_note_on_off, 'f_note_on_off': f_note_on_off,
        'p_note_on_vel': p_note_on_vel, 'r_note_on_vel': r_note_on_vel, 'f_note_on_vel': f_note_on_vel,
        'p_note_on_off_vel': p_note_on_off_vel, 'r_note_on_off_vel': r_note_on_off_vel, 'f_note_on_off_vel': f_note_on_off_vel}
    
    return metrics


import numpy as np
import pretty_midi as pm
import sys
sys.path.append('..')
from utils import pm_apply_sustain_pedal, convert_pm_note_list_to_pt_note_array


def compute_standard_benchmark_metrics_pm(true_MIDI, pred_MIDI, namecheck=True):
    '''Computes all benchmark metrics for a given pair of ground truth and prediction MIDI files. Uses pretty_midi
    to load and parse MIDI files.'''
    true_MIDI_basename = true_MIDI.split('/')[-1].split('.')[0]
    pred_MIDI_basename = pred_MIDI.split('/')[-1].split('.')[0]
    if namecheck:
        assert true_MIDI_basename in pred_MIDI_basename, f'{true_MIDI_basename} and {pred_MIDI_basename} files do not match.'

    true_pm = pm.PrettyMIDI(true_MIDI)
    true_pm = pm_apply_sustain_pedal(true_pm)
    true_notes = sum([instr.notes for instr in true_pm.instruments], [])

    pred_pm = pm.PrettyMIDI(pred_MIDI)
    pred_pm = pm_apply_sustain_pedal(pred_pm)
    pred_notes = sum([instr.notes for instr in pred_pm.instruments], [])

    # Frame-level metrics
    assert PERF_PIANO_ROLL_PARAMS['time_unit'] == 'sec'
    assert PERF_PIANO_ROLL_PARAMS['onset_only'] is False
    import scipy
    true_pr = true_pm.get_piano_roll(fs=PERF_PIANO_ROLL_PARAMS['time_div'])
    if PERF_PIANO_ROLL_PARAMS['piano_range']:
        true_pr = true_pr[21:109, :]
    true_pr = scipy.sparse.csc_matrix(true_pr)
    pred_pr = pred_pm.get_piano_roll(fs=PERF_PIANO_ROLL_PARAMS['time_div'])
    if PERF_PIANO_ROLL_PARAMS['piano_range']:
        pred_pr = pred_pr[21:109, :]
    pred_pr = scipy.sparse.csc_matrix(pred_pr)
    p_frame, r_frame, f_frame = compute_transcription_benchmark_framewise(true_pr, pred_pr)
        
    # Note-level metrics
    true_notelist = convert_pm_note_list_to_pt_note_array(true_notes, time_div=PERF_PIANO_ROLL_PARAMS['time_div'])
    pred_notelist = convert_pm_note_list_to_pt_note_array(pred_notes, time_div=PERF_PIANO_ROLL_PARAMS['time_div'])
    p_note_on, r_note_on, f_note_on, _ = ir_metrics_notewise(true_notelist, pred_notelist, onset_only=True)
    p_note_on_off, r_note_on_off, f_note_on_off, _ = ir_metrics_notewise(true_notelist, pred_notelist)
    p_note_on_vel, r_note_on_vel, f_note_on_vel, _ = ir_metrics_notewise_with_velocity(
        true_notelist, pred_notelist, onset_only=True)
    p_note_on_off_vel, r_note_on_off_vel, f_note_on_off_vel, _ = ir_metrics_notewise_with_velocity(
        true_notelist, pred_notelist)
    
    metrics = {
        'piece_id': true_MIDI_basename,
        'p_frame': p_frame, 'r_frame': r_frame, 'f_frame': f_frame,
        'p_note_on': p_note_on, 'r_note_on': r_note_on, 'f_note_on': f_note_on,
        'p_note_on_off': p_note_on_off, 'r_note_on_off': r_note_on_off, 'f_note_on_off': f_note_on_off,
        'p_note_on_vel': p_note_on_vel, 'r_note_on_vel': r_note_on_vel, 'f_note_on_vel': f_note_on_vel,
        'p_note_on_off_vel': p_note_on_off_vel, 'r_note_on_off_vel': r_note_on_off_vel, 'f_note_on_off_vel': f_note_on_off_vel}
    
    return metrics
