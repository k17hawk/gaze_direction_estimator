import sys
from exception import QbitException
from entity import VideoPredictionConfig
import os
from logger import logging
from Constants.constants import *
import cv2 
import mediapipe as mp
import time
import  math
import numpy as np
import csv
from utility.utils import *
import shutil



class GetVideo_class:
    def __init__(self,batch_config:VideoPredictionConfig):
        try:
            self.batch_config=batch_config 
            self.mp_face_mesh = mp.solutions.face_mesh
            self.image_paths = ImagePathFinder(self.batch_config.inbox_dir)
        except Exception as e:
            raise QbitException(e, sys)
    
    def euclidean_distance(self, point1, point2):
        x1, y1 = point1.ravel()
        x2, y2 = point2.ravel()
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return distance

    # Function to determine iris position based on distances
    def iris_position(self, iris_center, right_point, left_point):
        center_to_right_dist = self.euclidean_distance(iris_center, right_point)
        total_distance = self.euclidean_distance(right_point, left_point)
        ratio = center_to_right_dist / total_distance
        iris_position = ""
        if ratio <= 0.42:
            iris_position = "right"
        elif ratio > 0.42 and ratio <= 0.57:
            iris_position = "center"
        else:
            iris_position = "left"
        return iris_position, ratio

    # Function to update CSV file with new image paths
    def update_csv_file(self, csv_file_path, old_path, new_path):
        # Read CSV file and update image path
        with open(csv_file_path, mode='r', newline='') as file:
            csv_reader = csv.reader(file)
            rows = list(csv_reader)

        # Update the image path in the CSV rows
        for row in rows:
            if row[0] == old_path:
                row[0] = new_path

        # Write the updated CSV rows back to the file
        with open(csv_file_path, mode='w', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerows(rows)

    def delete_files_and_folders(self,folder_path):
        try:
            for root, dirs, files in os.walk(folder_path, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    shutil.rmtree(os.path.join(root, dir))
        except Exception as e:
                raise QbitException(e, sys)

    
    def start_prediction(self):
        try:
            with self.mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
                # location to save csv file
                csv_file_path = os.path.join(self.batch_config.outbox_dir, 'iris_positions.csv')
                
                with open(csv_file_path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Image_Path','Iris_Position', 'Ratio'])
                    
                    for image_path in self.image_paths:
                        frame = cv2.imread(image_path)  # Read the image
                        if frame is None:
                            print(f"Error: Unable to read image {image_path}.")
                            continue
                        
                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB for MediaPipe
                        img_h, img_w = frame.shape[:2]
                        results = face_mesh.process(rgb_frame)
                        if results.multi_face_landmarks:
                            mesh_points = np.array([np.multiply([p.x, p.y], [img_w, img_h]).astype(int) for p in results.multi_face_landmarks[0].landmark])
          
                            (l_cx, l_cy), l_radius = cv2.minEnclosingCircle(mesh_points[LEFT_IRIS])
                            (r_cx, r_cy), r_radius = cv2.minEnclosingCircle(mesh_points[RIGHT_IRIS])

                            center_left = np.array([l_cx, l_cy], dtype=np.int32)
                            center_right = np.array([r_cx, r_cy], dtype=np.int32)

                            cv2.circle(frame, center_left, int(l_radius), (255, 0, 255), 1, cv2.LINE_AA)
                            cv2.circle(frame, center_right, int(r_radius), (255, 0, 255), 1, cv2.LINE_AA)

                        
                            cv2.circle(frame, mesh_points[L_H_RIGHT][0], 3, (255, 255, 255), -1, cv2.LINE_AA)
                            cv2.circle(frame, mesh_points[L_H_LEFT][0], 3, (0, 255, 255), -1, cv2.LINE_AA)

                            iris_pos, ratio = self.iris_position(center_right, mesh_points[L_H_RIGHT], mesh_points[L_H_LEFT][0])

                            writer.writerow([image_path,iris_pos, ratio])  # Write iris position and ratio to CSV file

                            
                            # Move image file to archive_dir
                            new_image_path = os.path.join(self.batch_config.archive_dir, os.path.basename(image_path))
                            shutil.move(image_path, new_image_path)

                            # Update image path in CSV file
                            updated_image_path = os.path.join(self.batch_config.archive_dir, os.path.basename(image_path))
                            self.update_csv_file(csv_file_path, image_path, updated_image_path)
                        
                        cv2.waitKey(0)  # Wait for any key press to move to the next image

            # Close OpenCV windows after processing all images
            cv2.destroyAllWindows()
            self.delete_files_and_folders(self.batch_config.inbox_dir)
        except Exception as e:
            raise QbitException(e, sys)