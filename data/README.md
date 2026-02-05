To fetch the ADL Piano MIDI data from the originating GitHub repo

```bash
git clone git@github.com:lucasnfe/adl-piano-midi.git
cd adl-piano-midi/midi/
unzip adl-piano-midi.zip
cd ~/work/mds/data # back into this directory 'data'
ln -s /wherever/you/keep/adl-piano-midi/midi/adl-piano-midi apm
```

To fetch the MAESTRO MIDI and metadata

```bash
cd /data # or wherever you store your data
wget https://storage.googleapis.com/magentadata/datasets/maestro/v3.0.0/maestro-v3.0.0.csv
wget https://storage.googleapis.com/magentadata/datasets/maestro/v3.0.0/maestro-v3.0.0-midi.zip
unzip maestro-v3.0.0-midi.zip
cd ~/work/mds/data # back into this directory 'data'
ln -s /data/MAESTRO mae
```
