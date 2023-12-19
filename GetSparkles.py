import cv2
import numpy as np

# Function for non-maximum suppression
def non_max_suppression(boxes, overlap_thresh):
    if len(boxes) == 0:
        return []

    boxes = np.array(boxes)
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]

    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    indices = np.argsort(y2)

    selected_boxes = []
    while len(indices) > 0:
        last = len(indices) - 1
        i = indices[last]
        selected_boxes.append(i)

        xx1 = np.maximum(x1[i], x1[indices[:last]])
        yy1 = np.maximum(y1[i], y1[indices[:last]])
        xx2 = np.minimum(x2[i], x2[indices[:last]])
        yy2 = np.minimum(y2[i], y2[indices[:last]])

        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)

        overlap = (w * h) / area[indices[:last]]

        indices = np.delete(indices, np.concatenate(([last], np.where(overlap > overlap_thresh)[0])))

    return boxes[selected_boxes].astype("int")

template = cv2.imread('sparkle.png')

def GetSparkles(main_image):
    # Convert both images to grayscale
    main_gray = cv2.cvtColor(main_image, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # Define a list of scales to resize the template image
    scales = np.linspace(0.2, 1.0, 20)[::-1]  # Adjust the range of scales as needed

    matches = []
    for scale in scales:
        # Resize the template image according to the scale
        resized_template = cv2.resize(template_gray, None, fx=scale, fy=scale)

        # Match the resized template using cv2.matchTemplate()
        res = cv2.matchTemplate(main_gray, resized_template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8  # Adjust this threshold based on your use case
        loc = np.where(res >= threshold)

        for pt in zip(*loc[::-1]):
            matches.append([pt[0], pt[1], pt[0] + int(template_gray.shape[1] * scale), pt[1] + int(template_gray.shape[0] * scale)])

    # Apply non-maximum suppression to filter overlapping bounding boxes
    filtered_boxes = non_max_suppression(matches, 0.5)
    min_area = 60
    max_area = 50000
    filtered_boxes = [box for box in filtered_boxes if (box[2] - box[0]) * (box[3] - box[1]) >= min_area and (box[2] - box[0]) * (box[3] - box[1]) <= max_area]

    # Draw bounding boxes on the main image
    count = 0
    for (startX, startY, endX, endY) in filtered_boxes:
        cv2.rectangle(main_image, (startX, startY), (endX, endY), (0, 255, 0), 2)
        count += 1


    return count,main_image