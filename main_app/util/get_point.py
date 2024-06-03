import cv2

list_of_points = []

# Get the mouse position
def get_point(event, x, y, flags, param):
    global list_of_points
    if event == cv2.EVENT_LBUTTONDOWN:
        print(x, y)
        w = image.shape[1]
        h = image.shape[0]
        print(w, h)
        
        cv2.circle(image, (x, y), 3, (0, 0, 255), -1)
        list_of_points.append((float(x/w), float(y/h)))
        cv2.imshow('image', image)


# Create a window
scale = 0.5
path = r"rtsp://192.168.1.198:50004/profile/2"
# path = "../Video/new_camera.mp4"
cap = cv2.VideoCapture(path)
# cap = cv2.VideoCapture('1.png')
ret, image = cap.read()
print(image.shape)
# image = cv2.imread('img1.jpg')
image = cv2.resize(image, dsize=None, fx=scale, fy=scale)

cv2.namedWindow('image')
cv2.setMouseCallback('image', get_point)
cv2.imshow('image', image)

key = cv2.waitKey()
if key == ord('q'):
    print(list_of_points)
    cv2.destroyAllWindows()
elif key == ord('s'):
    with open(r'D:\company\yen_bai_project\face\face\Polygon\detect_zone_109.txt', 'w+') as f:
        for point in list_of_points:
            f.write(str(float(point[0])) + ' ' + str(float(point[1])) + '\n')
    cv2.destroyAllWindows()
