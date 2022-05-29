from distutils.log import error
import cv2
import numpy as np
import dlib
import os
 
def get_index(array):
    index = None
    for i in array[0]:
        index = i
        break
    return index

def assign_name(p1, p2):
    final_name = os.path.splitext(os.path.basename(p1))[0] + "-" + os.path.splitext(os.path.basename(p2))[0]
    # return os.path.splitext(os.path.basename(p1))[0], os.path.splitext(os.path.basename(p2))[0]
    return final_name

def readImg_and_landmarks(img_name):
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    img = cv2.imread(os.path.join("static/uploaded_files", img_name))
    # img = cv2.imread(img_name)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector(img)
    if len(faces) != 1:
        raise error
    else:
        landmarks = predictor(img_gray, faces[0])
        landmark_points = []
        for i in range(0,68):
            landmark_points.append((landmarks.part(i).x, landmarks.part(i).y))
        return img, img_gray, landmark_points

def slicing_triangle(img, img_gray,landmark_points, triangle_index):
    vertex1 = landmark_points[triangle_index[0]]
    vertex2 = landmark_points[triangle_index[1]]
    vertex3 = landmark_points[triangle_index[2]]
    triangle_vertices = np.array([vertex1, vertex2, vertex3], np.int32)
    rectangle = cv2.boundingRect(triangle_vertices)
    (x,y,w,h) = rectangle
    triangle_slice = img[y : y+h, x : x+w]
    relative_coordinates = np.array([[vertex1[0]-x, vertex1[1]-y],
                                        [vertex2[0]-x, vertex2[1]-y],
                                        [vertex3[0]-x, vertex3[1]-y]], np.int32)                   

    return triangle_vertices, triangle_slice, relative_coordinates,x,y,w,h


def swap_img(name_list):
    landmark_points1 = []
    landmark_points2 = []
    img1, img_gray1, landmark_points1 = readImg_and_landmarks(name_list[0])
    img2, img_gray2, landmark_points2 = readImg_and_landmarks(name_list[1])
    points1 = np.array(landmark_points1, np.int32)
    points2 = np.array(landmark_points2, np.int32)

    # faceImg_and_triangles
    convexhull = cv2.convexHull(points1)
    mask = np.zeros_like(img_gray1)
    cv2.fillConvexPoly(mask, convexhull, 255)
    rectangle = cv2.boundingRect(convexhull)
    subdiv = cv2.Subdiv2D(rectangle)
    subdiv.insert(landmark_points1)
    triangles = subdiv.getTriangleList()
    triangles = np.array(triangles, np.int32)

    triangle_indices = []
    for triangle in triangles:
        vertex1 = np.where((points1 == (triangle[0], triangle[1])).all(axis = 1))
        vertex1 = get_index(vertex1)

        vertex2 = np.where((points1 == (triangle[2], triangle[3])).all(axis = 1))
        vertex2 = get_index(vertex2)

        vertex3 = np.where((points1 == (triangle[4], triangle[5])).all(axis = 1))
        vertex3 = get_index(vertex3)
        triangle_index = [vertex1, vertex2, vertex3]
        triangle_indices.append(triangle_index)


    img1_face_mask = np.zeros_like(img_gray1)
    new_face_image2 = np.zeros_like(img2)
    for triangle_index in triangle_indices:
        triangle_vertices1, triangle_slice1, relative_coordinates1, x1, y1, w1, h1 = slicing_triangle(img1, img_gray1, landmark_points1, triangle_index)
        triangle_vertices2, triangle_slice2, relative_coordinates2, x2, y2, w2, h2 = slicing_triangle(img2, img_gray2, landmark_points2, triangle_index)
        cv2.line(img1_face_mask, triangle_vertices1[0],triangle_vertices1[1], 255)
        cv2.line(img1_face_mask, triangle_vertices1[1],triangle_vertices1[2], 255)
        cv2.line(img1_face_mask, triangle_vertices1[2],triangle_vertices1[1], 255)
        img1_face = cv2.bitwise_and(img1, img1, mask= img1_face_mask)
        triangle_slice_mask2 = np.zeros((h2,w2), np.uint8)
        cv2.fillConvexPoly(triangle_slice_mask2, relative_coordinates2, 255)


        relative_coordinates1 = np.float32(relative_coordinates1)
        relative_coordinates2 = np.float32(relative_coordinates2)  

        M = cv2.getAffineTransform(relative_coordinates1, relative_coordinates2)
        warped_triangle = cv2.warpAffine(triangle_slice1, M, (w2, h2))
        warped_triangle = cv2.bitwise_and(warped_triangle, warped_triangle, mask= triangle_slice_mask2)


        rectangle_slice2 = new_face_image2[y2:y2+h2, x2: x2+w2]
        rectangle_slice2_gray = cv2.cvtColor(rectangle_slice2, cv2.COLOR_BGR2GRAY)

        flag, mask_threshold = cv2.threshold(rectangle_slice2_gray,1,255,cv2.THRESH_BINARY_INV)
        warped_triangle = cv2.bitwise_and(warped_triangle, warped_triangle, mask= mask_threshold)

        rectangle_slice2 = cv2.add(rectangle_slice2,warped_triangle)
        new_face_image2[y2:y2+h2, x2: x2+w2] = rectangle_slice2


    convexhull2 = cv2.convexHull(points2)
    hullX, hullY, hullW, hullH = cv2.boundingRect(convexhull2)
    centre_face = (int((hullX + hullX + hullW)/2), int((hullY + hullY + hullH)/2))

    img2_mask = np.zeros_like(img_gray2)
    img2_mask = cv2.fillConvexPoly(img2_mask, convexhull2, 255)
    img2_mask_reverse = cv2.bitwise_not(img2_mask)
    img2_noface = cv2.bitwise_and(img2, img2, mask= img2_mask_reverse)
    final_img = cv2.add(img2_noface, new_face_image2)

    img_seamless_cloned = cv2.seamlessClone(final_img,  img2, img2_mask, centre_face, cv2.NORMAL_CLONE)
    resized_final_image = cv2.resize(img_seamless_cloned, (400,400))

    final_name = assign_name(name_list[0], name_list[1])
    path = os.path.join('static', 'output_files', final_name) + ".jpg"
    final_name = final_name + ".jpg"
    cv2.imwrite(path, img_seamless_cloned)
    cv2.destroyAllWindows()
    return path, final_name

if __name__ == "__main__":
    names = ["static/uploaded_files/emilia_clarke.jpg", "static/uploaded_files/bradley_cooper.jpg"]
    path = swap_img(names)