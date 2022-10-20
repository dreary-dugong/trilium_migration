# TL;DR
A small and dirty Python script to transfer data to a new version of the note-taking app I use.
Migrates data from 0.45.8 to 0.55.1.

This was put together pretty hastily and is missing a lot of error checking. If for some godforsaken reason you feel you need to use this script, make backups first. If you desperately need added functionality, reach out. 

# Background
I've been knowingly using an extremely outdated version of the open source notetaking app Trilium for the past 3 or so years because it was the version in the AUR at the time of installation and I needed to have the same version between Windows and Linux. I put the trilium-data folder on a shared partition and created symlinks on both my windows and linux partitions so I could access the same data no matter which OS I was using (I'm aware that Trilium has self-hosted sync features, but this way saves bandwidth and time). Eventually when I did a system upgrade on Manjaro, the Trilium package was updated and ceased to work with the database from the previous version. So from now on I'll be manually installing the most recent version of Trilium as it comes out on both operating systems. The most recent version at the time of writing is 0.55.1 so I wrote this script to transfer my data from the previous database that was on 0.45.8. 


