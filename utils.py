import fnmatch
import librosa.display
import numpy as np
import os
import pandas as pd
import pretty_midi as pm


def find_files(directory, pattern, path=True, sort=True, subdirs=True):
    '''
    Find files in a directory matching a specified pattern.

    Args:
        directory (str): The directory to search in.
        pattern (str): The pattern to match filenames against.
        path (bool): If True, return the full path of the files. Defaults to True.
        sort (bool): If True, return the list of files sorted. Defaults to True.
        subdirs (bool): If True, search in subdirectories. Defaults to True.

    Returns:
        list: A list of matching files, either with full paths or just filenames.
    '''
    files = []
    for root, _, filenames in os.walk(
        directory, followlinks=True):
        for filename in fnmatch.filter(filenames, pattern):
            if path:
                files.append(os.path.join(root, filename))
            else:
                files.append(filename)
        if not subdirs:
            break
    return sorted(files) if sort else files

def plot_piano_roll(instrument, start_pitch=21, end_pitch=109, fs=100):
    '''
    Display the piano roll of a musical instrument using librosa's specshow function.

    Parameters:
    instrument (Instrument): The instrument object containing the piano roll data.
    start_pitch (int): The starting MIDI pitch number (default is 21).
    end_pitch (int): The ending MIDI pitch number (default is 109).
    fs (int): The sampling frequency (default is 100).

    Returns:
    None: This function displays the piano roll plot and does not return any value.

    Source: https://nbviewer.org/github/craffel/pretty-midi/blob/main/Tutorial.ipynb
    '''
    librosa.display.specshow(instrument.get_piano_roll(fs)[start_pitch:end_pitch],
                             hop_length=1, sr=fs, x_axis='time', y_axis='cqt_note',
                             fmin=pm.note_number_to_hz(start_pitch))

def get_polyphony_degrees(instrument, fs=100, events_only=False):
    '''
    Calculate the degrees of polyphony for a given musical instrument's piano roll.

    Parameters:
    instrument (Instrument): The instrument object that provides the piano roll.
    fs (int): The sampling frequency for the piano roll (default is 100).
    events_only (bool): If True, only count the transitions in polyphony events (default is False).

    Returns:
    numpy.ndarray: An array representing the degree of polyphony for each time frame.
    '''
    piano_roll = instrument.get_piano_roll(fs=fs)
    
    # get degrees of polyphony for each time frame
    polyphonies = (piano_roll>0).sum(axis=0)
    t_poly = polyphonies>0 # time frames with polyphony degree of 1 and higher
    polyphonies = polyphonies[t_poly]

    if events_only:
        # don't count durations (frames) of individual polyphony events
        filter = np.argwhere(polyphonies != np.roll(polyphonies, 1)).squeeze()
        polyphonies = polyphonies[filter]

    return polyphonies

def pm_apply_sustain_pedal(midi, pedal_threshold=64):
    '''
    Extends the end times of notes in a PrettyMIDI object based on sustain pedal (CC64) events.

    Parameters:
    midi (PrettyMIDI): The PrettyMIDI object containing instruments and notes to be modified.
    pedal_threshold (int): The threshold value for the sustain pedal (default is 64). 
                           Only pedal values above this threshold will extend note end times.

    Returns:
    PrettyMIDI: The modified PrettyMIDI object with adjusted note end times.
    
    Warning:
    This implementation is inefficient and intended for toy sanity check experiments only.
    '''
    for instr in midi.instruments:
        sustain_candidates = list()
        # extend notes based on sustain pedal
        for cc in [cc for cc in instr.control_changes if cc.number == 64]:
            if cc.value >= pedal_threshold:
                for note in instr.notes:
                    if note.end > cc.time:
                        if note not in sustain_candidates:
                            sustain_candidates.append(note)
            else:
                while sustain_candidates:
                    note = sustain_candidates.pop()
                    if note.end < cc.time:
                        note.end = cc.time
        # eliminate possible overlaps, one pitch at a time
        for pitch in np.unique([note.pitch for note in instr.notes]):
            adjacent = sorted([note for note in instr.notes if note.pitch == pitch], key=lambda n: n.start)
            if len(adjacent) < 2:
                continue
            for i in range(len(adjacent) - 1):
                n1 = adjacent[i]
                n2 = adjacent[i + 1]
                if n1.end > n2.start:
                    n1.end = n2.start
    return midi

def convert_pm_note_list_to_pt_note_array(note_list, time_div=100):
    '''
    Converts a list of pretty_midi.Note objects to a partitura-style note array.

    Parameters:
    note_list (list): A list of pretty_midi.Note objects to be converted.
    time_div (int): A divisor for converting time from seconds to the desired time unit (default is 100).

    Returns:
    np.ndarray: A 2D numpy array where each row represents a note with the following columns:
                - Onset time (int)
                - Offset time (int)
                - Pitch (int)
                - Velocity (int)
    '''
    if len(note_list) == 0:
        return np.array([])
    
    onsets = np.array([n.start for n in note_list])
    onsets = np.round(onsets * time_div).astype(int)
    offsets = np.array([n.end for n in note_list])
    offsets = np.round(offsets * time_div).astype(int)
    pitches = np.array([n.pitch for n in note_list])
    velocities = np.array([n.velocity for n in note_list])
    note_array = np.column_stack((onsets, offsets, pitches, velocities))

    return note_array

def polish_postsustain_overlaps_to_adjacents(notes):
    '''
    Eliminate possible overlaps in musical notes, one pitch at a time.

    This function processes a structured numpy array of musical notes generated by partitura,
    where each note has at least the following fields: pitch, note_on, note_off, and sound_off.
    It addresses overlaps caused by the sustain pedal, ensuring that the sound_off time of a note
    is adjusted to the note_on time of the subsequent note if they overlap.

    Parameters:
    notes (numpy structured array): An array of notes with fields including pitch, note_on, note_off, and sound_off.

    Returns:
    None: The function modifies the input array in place.
    '''
    for pitch in np.unique([n["pitch"] for n in notes]):
        adjacent = sorted([n for n in notes if n["pitch"] == pitch], key=lambda n: n["note_on"])
        if len(adjacent) < 2:
            continue
        for i in range(len(adjacent) - 1):
            n1 = adjacent[i]
            n2 = adjacent[i + 1]
            if n1["sound_off"] > n2["note_on"]:
                n1["sound_off"] = n2["note_on"]
    
def get_rgba(color, alpha=0.5):
    '''
    Convert a color to RGBA format.

    Parameters:
    color (str): The color to convert, specified as a name or hex code.
    alpha (float): The alpha (transparency) value, between 0 (transparent) and 1 (opaque). Default is 0.5.

    Returns:
    tuple: A tuple representing the RGBA color.
    '''
    import matplotlib.colors as mcolors
    return mcolors.to_rgb(color) + (alpha,)

def concatenate_results_genre(genre_all, path_results='../results'):
    '''
    Concatenate all the results for (1) Genre set.

    Parameters:
    genre_all (str): The file path where the concatenated results will be saved.
    path_results (str): The directory path where the individual result CSV files are located.
    '''
    genre_oaf = f'{path_results}/1_genre_dk_oaf.csv'
    genre_kong = f'{path_results}/1_genre_dk_kong.csv'
    genre_T5 = f'{path_results}/1_genre_dk_T5.csv'
    genre_toyama = f'{path_results}/1_genre_dk_toyama.csv'
    genre_edwards = f'{path_results}/1_genre_dk_edwards.csv'

    genre_dk_path_model_tuples = [
        (genre_oaf, 'OaF'), (genre_kong, 'Kong'),
        (genre_T5, 'T5'), (genre_toyama, 'Toyama'), (genre_edwards, 'Edwards')]

    dfs = []
    for path_csv, model in genre_dk_path_model_tuples:
        df = pd.read_csv(path_csv)
        df['midiset'] = 'genre'
        df['audioset'] = 'disklavier'
        df['model'] = model
        df['genre'] = df['piece_id'].str.extract('(^.*?)_', expand=False)
        dfs.append(df)
    df = pd.concat(dfs).reset_index(drop=True)

    # Reorder columns
    n = len(df.columns)
    column_order = [n-2, n-1, n-4, n-3] + list(range(n-4))
    df = df.iloc[:, column_order]

    # Save to csv
    df.to_csv(genre_all, index=False)

def concatenate_results_random(random_all, path_results='../results'):
    '''
    Concatenate all the results for (2) Random set.

    Parameters:
    random_all (str): The file path where the concatenated results will be saved.
    path_results (str): The directory path where the individual result CSV files are located.
    '''
    random_oaf = f'{path_results}/2_random_dk_oaf.csv'
    random_kong = f'{path_results}/2_random_dk_kong.csv'
    random_T5 = f'{path_results}/2_random_dk_T5.csv'
    random_toyama = f'{path_results}/2_random_dk_toyama.csv'
    random_edwards = f'{path_results}/2_random_dk_edwards.csv'

    random_dk_path_model_tuples = [
        (random_oaf, 'OaF'), (random_kong, 'Kong'),
        (random_T5, 'T5'), (random_toyama, 'Toyama'), (random_edwards, 'Edwards')]

    dfs = []
    for path_csv, model in random_dk_path_model_tuples:
        df = pd.read_csv(path_csv)
        df['midiset'] = 'random'
        df['audioset'] = 'disklavier'
        df['model'] = model
        df['polyphony'] = df['piece_id'].str.extract('P(\d+)_D', expand=False).astype(int)
        df['dynamics'] = df['piece_id'].str.extract('_D(\d)', expand=False).astype(int)
        dfs.append(df)
    df = pd.concat(dfs).reset_index(drop=True)

    # Reorder columns
    n = len(df.columns)
    column_order = [n-3, n-2, n-1, n-5, n-4] + list(range(n-5))
    df = df.iloc[:, column_order]

    # Save to csv
    df.to_csv(random_all, index=False)

def concatenate_results_maetest(maetest_all, path_results='../results'):
    '''
    Concatenate all the results for (3) MAEtest set.

    Parameters:
    maetest_all (str): The file path where the concatenated results will be saved.
    path_results (str): The directory path where the individual result CSV files are located.
    '''
    maetest_mae_oaf = f'{path_results}/3_maetest_mae_oaf.csv'
    maetest_mae_kong = f'{path_results}/3_maetest_mae_kong.csv'
    maetest_mae_T5 = f'{path_results}/3_maetest_mae_T5.csv'
    maetest_mae_toyama = f'{path_results}/3_maetest_mae_toyama.csv'
    maetest_mae_edwards = f'{path_results}/3_maetest_mae_edwards.csv'

    maetest_dk_oaf = f'{path_results}/3_maetest_dk_oaf.csv'
    maetest_dk_kong = f'{path_results}/3_maetest_dk_kong.csv'
    maetest_dk_T5 = f'{path_results}/3_maetest_dk_T5.csv'
    maetest_dk_toyama = f'{path_results}/3_maetest_dk_toyama.csv'
    maetest_dk_edwards = f'{path_results}/3_maetest_dk_edwards.csv'

    maetest_mae_path_model_tuples = [
        (maetest_mae_oaf, 'OaF'), (maetest_mae_kong, 'Kong'),
        (maetest_mae_T5, 'T5'), (maetest_mae_toyama, 'Toyama'), (maetest_mae_edwards, 'Edwards')]
    maetest_dk_path_model_tuples = [
        (maetest_dk_oaf, 'OaF'), (maetest_dk_kong, 'Kong'),
        (maetest_dk_T5, 'T5'), (maetest_dk_toyama, 'Toyama'), (maetest_dk_edwards, 'Edwards')]

    dfs = []
    for path_csv, model in maetest_mae_path_model_tuples:
        df = pd.read_csv(path_csv)
        df['midiset'] = 'maetest'
        df['audioset'] = 'maestro'
        df['model'] = model
        dfs.append(df)
    for path_csv, model in maetest_dk_path_model_tuples:
        df = pd.read_csv(path_csv)
        df['midiset'] = 'maetest'
        df['audioset'] = 'disklavier'
        df['model'] = model
        dfs.append(df)

    df = pd.concat(dfs).reset_index(drop=True)

    # Reorder columns
    n = len(df.columns)
    column_order = [n-1, n-3, n-2] + list(range(n-3))
    df = df.iloc[:, column_order]

    # Save to csv
    df.to_csv(maetest_all, index=False)
