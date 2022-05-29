
# FaceSwap WebApp using dlib, opencv, Flask

a web application which uses dlib and opencv to produce deepfake images by swapping the face of one image onto another.

##Screenshots
![App Screenshot]('https://github.com/Aditya-ahirwar/Face_Swap_Engage_Project/blob/master/static/Example_image1.jpg
')

## Dlib Installation

To install Dlib we have to install cmake first

```bash
  pip install cmake
```
Now download the "dlib-install" folder from my github repo. copy the path of downloaded folder and open command prompt.
inside commad prompt write following command

```bash
  pip install "downloaded_folder_path/dlib-19.22.99-cp39-cp39-win_amd64.whl"
```
This will install dlib on your local machine.

To use dlib we also need to download "shape_predictor_68_face_landmarks.dat". Available inside "install-dlib folder".

## Dlib Overview
Dlib is a machine learning library, using it we can locate 68 distinct coordinates points on human face.
Then we can divide the face into distinct triangles (Delaunay triangles) using these points. Then, using opencv, we can combine the triangles of one face with those of another to create a new face.
