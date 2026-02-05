import pretty_midi
import numpy as np
import pandas as pd
from scipy.sparse import csc_matrix
from typing import List

def midi_pitch_to_name_formatted(midi_pitch: int, formatted: bool = True) -> str:
    """
    Convert a MIDI pitch number to a note name with octave, optionally formatted for LaTeX.

    Parameters
    ----------
    midi_pitch : int
        the MIDI pitch number (0-127).
    formatted : bool, defaults to True
        If True, returns the note name formatted for LaTeX. If False, returns a plain string. Default is True.

    Returns
    -------
    str: The note name with octave, formatted as a LaTeX string if `formatted` is True, otherwise as a plain string.
    """
    note_names = ['C', 'C{\sharp}', 'D', 'D{\sharp}', 'E', 'F', 'F{\sharp}', 'G', 'G{\sharp}', 'A', 'A{\sharp}', 'B']
    if not formatted:
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (midi_pitch // 12) - 1  # MIDI pitch to octave number
    note = note_names[midi_pitch % 12]  # Note name
    formatted_label = fr"$\mathregular{{{note}}}_{{{octave}}}$"
    if not formatted: return f'{note}{octave}'
    else: return formatted_label

# GLOBALS
PITCH_RANGE = range(21, 109)  # MIDI pitches for the 88 piano keys
PITCH_NAMES = [midi_pitch_to_name_formatted(p) for p in PITCH_RANGE]


def extract_pitch_distribution(midi_file: str, pitch_range: range = PITCH_RANGE) -> np.ndarray:
    """
    Extract the pitch distribution from a MIDI file.
    
    Parameters
    ----------
    midi_file : str
        Path to the MIDI file.
    pitch_range : range, optional
        The range of MIDI pitches to consider. Default is PITCH_RANGE (21-108).    
    
    Returns
    -------
    np.ndarray: An array of pitch counts where each index corresponds to a pitch within the range, and the value at each index represents the count of that pitch in the MIDI file.

    Raises:
        Exception: If there is an error processing the MIDI file, an error message is printed and an array of zeros is returned.
    """
    try:
        midi_data = pretty_midi.PrettyMIDI(midi_file)
        pitch_counts = np.zeros(len(pitch_range))

        for instrument in midi_data.instruments:
            for note in instrument.notes:
                if note.pitch in pitch_range:
                    pitch_counts[note.pitch - pitch_range.start] += 1

        return pitch_counts
    except Exception as e:
        print(f"Error processing {midi_file}: {e}")
        return np.zeros(len(pitch_range))

def get_polyphony_levels(piano_roll: csc_matrix) -> np.ndarray:
    """
    Calculate the polyphony levels of a piano roll.
    Polyphony level is defined as the number of simultaneous notes being played
    at each time step.

    Parameters
    ----------
    piano_roll : scipy.sparse.csc_matrix
        A sparse matrix representation of the piano roll, where rows represent pitches and columns represent time steps.

    Returns
    -------
    np.ndarray: An array containing the polyphony levels for each time step.
    """
    return np.diff(piano_roll.indptr)  # columnwise sum of non-zero elements

def compute_polyphony_proportions(group_piano_rolls: List[np.ndarray], max_n: int = 15) -> np.ndarray:
    """
    Compute the proportions of different polyphony levels in a group of piano rolls.

    Parameters
    ----------
    group_piano_rolls : list of np.ndarray
        A list of piano roll arrays, where each array represents a piano roll.
    max_n : int, defaults to 15
        The maximum polyphony level to consider

    Returns
    -------
    np.ndarray: An array of proportions for each polyphony level from 0 to max_n.
    """
    
    polyphony_counts = np.zeros(max_n + 1, dtype=int)
    for piano_roll in group_piano_rolls:
        levels = get_polyphony_levels(piano_roll)
        for n in range(max_n + 1):
            polyphony_counts[n] += np.sum(levels == n)
    total_columns = sum(piano_roll.shape[1] for piano_roll in group_piano_rolls)
    proportions = polyphony_counts / total_columns
    return proportions


def midi_to_piano_roll(midi_file: str, time_step: float = 0.01) -> csc_matrix:
    """
    Convert a MIDI file to a piano roll with unified absolute time information.

    Parameters
    ----------
    midi_file : str
        Path to the MIDI file.
    time_step : float, optional
        Time resolution in seconds (e.g., 0.01 for 10 ms steps). Default is 0.01.

    Returns
    -------
    scipy.sparse.csc_matrix : A sparse matrix of shape (88, n), where n is the number of time steps.
    """
    # get note events
    midi_data = pretty_midi.PrettyMIDI(midi_file)
    
    notes = []
    for instrument in midi_data.instruments:
        for note in instrument.notes:
            notes.append((note.start, note.end, note.pitch))

    # discretize time
    max_time = max(note[1] for note in notes)
    time_steps = np.arange(0, max_time + time_step, time_step)
    n_steps = len(time_steps)

    # init pianoroll
    piano_roll = np.zeros((88, n_steps), dtype=bool)
    
    for start, end, pitch in notes:
        if 21 <= pitch <= 108:
            start_idx = int(np.round(start / time_step))
            end_idx = int(np.round(end / time_step))
            piano_roll[pitch - 21, start_idx:end_idx] = True # map pitch to piano roll index

    return csc_matrix(piano_roll)


def list_notes_in_dicts(midi_file: str) -> List[dict]:
    """
    Collect notes from a MIDI file into a list of note dictionaries.

    Parameters
    ----------
    midi_file : str
        Path to the MIDI file.

    Returns
    -------
    List[dict]: A list of dictionaries, each representing a note event with the following keys:
        - 'midi_pitch': int, the MIDI pitch number.
        - 'piano_pitch': int, the piano pitch number (MIDI pitch - 21).
        - 'note_name': str, the note name.
        - 'onset': float, the onset time of the note in seconds.
        - 'offset': float, the offset time of the note in seconds.
        - 'velocity': int, the velocity of the note.
    """
    pm = pretty_midi.PrettyMIDI(midi_file)
    
    # create a list of note events, where each note event is a dict
    note_events = []
    for instrument in pm.instruments:
        for note in instrument.notes:
            midi_pitch = note.pitch
            piano_pitch = midi_pitch - 21
            note_name = midi_pitch_to_name_formatted(midi_pitch, formatted=False)
            onset = float(note.start)
            offset = float(note.end)
            velocity = note.velocity
            
            note_dict = {
                'midi_pitch': midi_pitch,
                'piano_pitch': piano_pitch,
                'note_name': note_name,
                'onset': onset,
                'offset': offset,
                'velocity': velocity
            }
            note_events.append(note_dict)
            
    return note_events


def count_harmonic_chords(note_events: List[dict], delta_time: float = 0.2, max_chord: bool = False) -> dict:
    """
    Count intervals/chords within an octave in a list of note events.
    Intervals/chords larger than an octave are collapsed such that, e.g., C4 and D5 are considered two semitones apart instead of 14.
    The function is intended for analysis for harmonic joint onsets (intervals and chords), i.e., it assumes octave, transpositional, and inversional equivalence and homogeneity of piano timbre across registers.g

    Parameters
    ----------
    note_events : list of dict
        A list of note events, where each event is represented as a dictionary with keys:
            - 'midi_pitch': int, the MIDI pitch number.
            - 'onset': float, the onset time of the note in seconds.
            - 'offset': float, the offset time of the note in seconds.
            - 'velocity': int, the velocity of the note.
    delta_time : float, optional, defaults to 0.2
        The cutoff time for treating notes at different onsets as belonging to the same chord
    max_chord : bool, defaults to False
        If True, only the maximum constellation of a chord (i.e., all onsets that fall within delta_time) is counted.  If False, all unique interval constellations that fall within delta_time are counted.
    
    Returns
    -------
    dict: A dictionary where keys are interval/chord representations and values are their frequencies.
        Example: {'{0}': 207, '{0, 3}': 129, '{0, 8, 3}': 47, '{0, 8}': 163, '{0, 4}': 917, ...}
    """
    
    def _get_sorted_transposed_interval_key(chord_list: List[int]) -> str:
        """
        Take a list of MIDI pitches and return a string representation of the sorted and transposed interval key. Sorts the pitches, transposes them to start from zero, collapses intervals to within an octave, and ensures unique intervals.

        Parameters
        ----------
        chord_list : list
            A list of MIDI pitches making up a chord, e.g., [76, 66, 79].

        Returns
        -------
        str: A string representation of the sorted and transposed interval key.
        """
        chord_arr = np.array(sorted(chord_list))
        chord_arr -= np.min(chord_arr)
        chord_arr_collapsed = chord_arr % 12
        
        intervals, counts = np.unique(chord_arr_collapsed, return_counts=True)
        if any(counts != 1):
            chord_arr_collapsed = np.append(chord_arr_collapsed, 12)
        
        transposed_interval_key = str(sorted(set(chord_arr_collapsed.tolist())))
        return transposed_interval_key
        
    def _add_chord_to_key(chord_key: str, interval_dict: dict) -> dict:
        """
        Adds a chord to the interval dictionary. If the chord key already exists in the dictionary,
        increments its count by 1. Otherwise, adds the chord key to the dictionary with a count of 1.

        Parameters
        ----------
        chord_key : str
            The key of the chord to add.
        interval_dict : dict
            The dictionary containing chord keys and their counts.

        Returns
        -------
        dict: The updated interval dictionary with the chord key added or incremented.
        """
        if chord_key in interval_dict:
            interval_dict[chord_key] += 1
        else: 
            interval_dict[chord_key] = 1
        return interval_dict

    if not note_events:
        return {}

    # init
    chord_dict = dict()
    curr_anchor = note_events[0]['onset']
    curr_chord = [note_events[0]['midi_pitch']]
    
    for i, n in enumerate(note_events[1:], 1):
        if n['onset'] - curr_anchor > delta_time: 
            if max_chord or (not max_chord and i == 1):
                interval_key = _get_sorted_transposed_interval_key(curr_chord)
                chord_dict = _add_chord_to_key(interval_key, chord_dict)
            curr_anchor = n['onset']
            curr_chord = [n['midi_pitch']]    
        else: 
            curr_chord.append(n['midi_pitch'])
            if not max_chord:
                interval_key = _get_sorted_transposed_interval_key(curr_chord)
                chord_dict = _add_chord_to_key(interval_key, chord_dict)
    
    chord_dict = dict(sorted(chord_dict.items(), key=lambda item: (len(eval(item[0])), eval(item[0]))))
    
    return chord_dict
    

def summarize_equivalent_chords(chords_df, chord_dict):
    """
    Summarize chord data by summing columns based on chord combinations in the chord_dict, where each key is a chord name and the values are lists of interval combinations resulting in the root or inversional form of the same chord.

    Parameters
    ----------
    trichord_df : pd.DataFrame
        DataFrame containing trichord data, where columns correspond to chord combinations.
    chord_dict : dict
        Dictionary mapping chord names to their root and inversional forms.

    Returns
    -------
    pd.DataFrame: Summarized DataFrame with where each columns sums the count of the respective chord in all its equivalent forms, aggregated per genre
    """
    # init summarized df
    summarized_chords_df = pd.DataFrame()
    summarized_chords_df['genre'] = chords_df['genre']

    for chord_name, chord_combinations in chord_dict.items():
        cols_to_sum = []
        
        for chord in chord_combinations:
            chord_str = str(chord)
            if chord_str in chords_df.columns:
                cols_to_sum.append(chord_str)
        
        if cols_to_sum:
            summarized_chords_df[chord_name] = chords_df[cols_to_sum].sum(axis=1)
    # aggregate per genre
    summarized_chords_df = summarized_chords_df.groupby('genre').sum().reset_index()

    return summarized_chords_df



def get_piano_key_color(midi_pitch):
    black_keys = {1, 3, 6, 8, 10}
    if (midi_pitch % 12) in black_keys:
        return 'black'
    else:
        return 'white'

def note_to_pitch_class_distribution(piano_distribution, return_pitch_class_names=False):
    """
    Converts a piano note distribution (88 notes) to a pitch class distribution (12 classes).
    piano_distribution (numpy.ndarray): Array of shape (88,) representing the note distribution.
    """
    if piano_distribution.shape[0] != 88:
        raise ValueError("Input array must have 88 elements for the piano note range.")

    pitch_class_distribution = np.zeros(12, dtype=piano_distribution.dtype)
    pitch_class_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    pitch_class_names_formatted = ['C', 'C{\sharp}', 'D', 'D{\sharp}', 'E', 'F', 'F{\sharp}', 'G', 'G{\sharp}', 'A', 'A{\sharp}', 'B']
    
    for note_index in range(88):
        pitch_class = (note_index + 9) % 12
        pitch_class_distribution[pitch_class] += piano_distribution[note_index]
        
    if return_pitch_class_names: return pitch_class_distribution, pitch_class_names
    return pitch_class_distribution

