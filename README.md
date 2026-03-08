# Fourier-Art
# Fourier Epicycles Visualizer

**Live Demo:** [https://fourier-art.vercel.app/](https://fourier-art.vercel.app/)

A full-stack web application that transforms static images into continuous line drawings animated by rotating mathematical vectors (Fourier Epicycles). 

This project calculates the Discrete Fourier Transform (DFT) of a 2D contour path to reconstruct and animate complex shapes using nothing but circles drawing in real-time based on Euler's construction.

## Features
* **Live Mathematical Animation:** Watch as hundreds of rotating circles calculate and draw your uploaded images in real-time.
* **Hybrid Computer Vision Pipeline:** Uses OpenCV to smartly detect faces (keeping sharp details like eyes and lips) while applying bilateral filtering and morphological closing to body/clothes to remove messy fabric textures.
* **Custom Path Stitching:** Utilizes a Nearest Neighbor heuristic algorithm to connect disjointed, shattered contours into one single, continuous fluid path.
* **Euler Construction & Epicycles:** Utilizes complex exponentials to represent 2D coordinates, applying Euler's formula ($e^{i\theta} = \cos\theta + i\sin\theta$) to mathematically stack rotating vectors tip-to-tail.
* **Interactive UI Controls:** Real-time sliders for the number of epicycles ($K$), animation speed, zoom tracking, path fading, and custom color pickers.
* **Multi-User Backend Scaling:** Stateless Flask backend utilizes UUID generation to handle simultaneous image uploads from multiple devices without data collision.

## Tech Stack
* **Frontend:** HTML5 Canvas, CSS3, Vanilla JavaScript (Deployed on Vercel)
* **Backend:** Python 3, Flask, Werkzeug (Deployed on Render)
* **Image & Signal Processing:** OpenCV (`cv2`), NumPy, Base64

## Pipeline
1. **Edge Extraction:** The user uploads an image. The Flask backend converts it to grayscale and applies adaptive thresholding and Gaussian/Median blurs to extract structural contours.
2. **Stitching:** A custom algorithm sorts and connects these broken contour fragments by calculating the shortest Euclidean distance between endpoints, preventing the "horizontal scanline" effect.
3. **Signal Resampling:** The 2D coordinates are converted into a complex signal ($x + yi$) and resampled uniformly by arc-length to ensure constant drawing velocity.
4. **Discrete Fourier Transform (DFT):** The backend calculates the frequency, amplitude, and phase for $N$ harmonics. 
5. **Euler Construction & Rendering:** The frontend receives the sorted Fourier data and uses Euler's construction to animate the epicycles. Each circle represents a complex exponential vector rotating at a specific frequency, stacked tip-to-tail on the HTML5 Canvas to trace the final image.

## Local Installation

If you want to run this project locally on your machine:

**1. Clone the repository:**
```bash
git clone [https://github.com/YOUR-USERNAME/Project_fourier.git](https://github.com/YOUR-USERNAME/Project_fourier.git)
cd Project_fourier
