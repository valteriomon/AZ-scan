# AZ-Scan

...

# TO DO

## Map view
- P0
    - Save scanned file with filename according to prefix code + matrix position
        - Create new folder with project code
    - Re-scan specific matrix position
        - Warn if file exists will be overriden
    - Specify saving folder
    - Reset/New button
        - Destroy widgets
    - Set "Scanning" in status bar and disable next scan buttons until completed
    - Catch scanner error
    - Left click menu: Open, Rescan
    - Join/create PTO
    - Add patch image to project button: place in right place
    - Rotate grid ()
    - Volver al menu
    - Salir
    - Stitcher view
- P1
    - Open existing project
    - Back to main menu
    - Mapas v2 -> Join while scanning
- P2
    - Set map size
    - Rotate (90 degrees) scan and save
    - Add help, shortcuts, info on how to use
    - Rotate all images at once
        - All (that arent rotated already) or pick which ones
- P3
    - Drag and drop joints generator
    - Log errors


## Postcard view
- P0
    - Add "repeat/remake last scan" button
    - Preview scan
    - If code folder not created, create it
        - Check path name if matches code, if not create folder
    - Delete last scan option
    - Split saves into folders depending prefix
    - "Next" button?
        - Scan + Next instead of auto-update
            - Ask to delete previous scan
    - Skip B side
    - Checkbox "Guardar posición"

    - State not saving until you scan again, so "next" is last when you reopen

    - Enable scan button only if new and last scan are named differently (check last scan exists).
    - Enable scan button only after previous task finishes.
    - Catch scanner error
        - Acts as save, turns off on manual index change
    - Right click option, open editor
    - Split in-viewer options into a new class
    - Image viewer: Left click - Zoom out
        - Add quick rotate and save
- P1
    - Edit scan > Parallel to scan program (crop while scanning > Go back and forth between scans?)
        - Crop
        - Autocrop > ImageMagick or OpenCV?
        - Rotate by 90 degrees
        - Slight rotate
        - Undo action
- P2
    - Make font bigger
    - Bold on filenames
    - Add help, shortcuts, info on how to use





## Main
- P0
    - Add filename to viewer window
    - Check unused requirements
- P1
    - Remove git_pull hardcoded directories
    - Launch Editor
- P2
    - Improve updating remotely
        - Remove dev libraries from compilation
        - Patching option for data files?
    - Log of all scans

## Others
- Omeka-S
    - Check how related resources export in CSV
    - Check if thesaurus appears in datatype
    - Check if free added values show in future fill
- Google Appscript
    - Automove according to prefix (removing original as to free space in device)
    - Add scan code + drive link A and B sides (if exists).
    - Check sorting/tabs.
    - Optional: Add to original database
- Google sync
    - Set scan folder to the Drive sync folder
    - Check permissions so sync doesn't remove files