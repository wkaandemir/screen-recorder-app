---

## Screen Recorder Application PyQt

---

## Features

This application allows you to select from multiple screens and record the screen for a specified duration. The recordings are saved in `.avi` format to a chosen directory.

- Select from multiple screens.
- Set the recording duration in seconds.
- Track the remaining time in real-time during recording.
- Save recordings to a specified folder and automatically clean up old recordings.
- Easily view recorded files within the application.

---

## Requirements

The following libraries are required for this application to run:

- **Python 3.8 or later**
- PyQt6
- mss
- opencv-python (`cv2`)
- screeninfo
- numpy

You can install the required libraries by running the following command:

```bash
pip install PyQt6 mss opencv-python screeninfo numpy
```

---

## Usage

1. **Launch the Application:**
   ```bash
   python screen_recorder.py
   ```

2. **Screen Selection:** 
   Select the screen you want to record from the dropdown menu.

3. **Recording Duration:**
   Set the recording duration in seconds using the spinbox.

4. **Start Recording:** 
   Click the `Start Recording` button to begin recording.

5. **Stop Recording:** 
   Click the `Stop Recording` button to stop the recording.

6. **View Recordings:** 
   Click the `Show Recordings` button to open the folder where the recordings are saved.

7. **Exit the Application:** 
   Use the `Exit` button to close the application.

---

## Folder and Recording Management

- On the first launch, you will be asked to select a folder for the recordings. A folder named `Screen Recordings` will be created inside the selected directory.
- The maximum number of recordings is set to `10`. When this limit is exceeded, the oldest recording is automatically deleted.

---

## Important Notes

- During recording, the application may heavily use your CPU and disk space. Adjust the recording time and resolution accordingly.
- If the application crashes during a recording, your last recording may not be completed.

---

## Known Issues and Solutions

1. **Error: 'mss' or another library not found.**
   - Solution: Install the required libraries using the `pip install` command above.

2. **Screen list displays incorrectly.**
   - Solution: Check your computer's display settings and try again.

---

## Contribution and Development

If you would like to contribute to or develop this application:

1. Fork the project.
2. Add new features or fix existing issues.
3. Create a pull request.

---

## License

This project is licensed under the MIT License. For more information, please refer to the `LICENSE` file.

---

