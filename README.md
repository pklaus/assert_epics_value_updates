Assert EPICS value updates
==========================

A Python service that connects to EPICS process variables
and watches them for changing values. If the value
doesn't fluctuate for a configurable number of samples,
an external script is executed.

The need for this script came up as the readout of a
certain detector can get stuck. In that case, the number
of data words in each frame wouldn't change anymore and
the readout could be restarted by the external script.

CLI signature:

```
usage: assert_epics_value_updates.py [-h] [--pv PV] [--script SCRIPT]
                                     [--tolerance TOLERANCE]

optional arguments:
  -h, --help            show this help message and exit
  --pv PV               PV to monitor (can be used multiple times).
  --script SCRIPT       Script to run if the PVs don't update anymore.
  --tolerance TOLERANCE
                        Number of times we tolerate non-changing values
```

An example calling the service:

```
./assert_epics_value_updates.py  \
 --pv CBM:MVD:TRB:Mvd-0xd010-DataLength.0 \
 --pv CBM:MVD:TRB:Mvd-0xd010-DataLength.1 \
 --pv CBM:MVD:TRB:Mvd-0xd011-DataLength.0 \
 --pv CBM:MVD:TRB:Mvd-0xd011-DataLength.1 \
 --script ./restart_readout.sh
```
