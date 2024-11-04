ANGLE_ROTATE_X = 10
ANGLE_ROTATE_Y = 10
ANGLE_ROTATE_Z = 10


# Ворочает камеру
def rotate_camera(Facade, text):
    if text == 'X+':
        Facade.camera_rotate_x(ANGLE_ROTATE_X)
    elif text == 'X-':
        Facade.camera_rotate_x(-ANGLE_ROTATE_X)
    elif text == 'Y+':
        Facade.camera_rotate_y(ANGLE_ROTATE_Y)
    elif text == 'Y-':
        Facade.camera_rotate_y(-ANGLE_ROTATE_Y)
    elif text == 'Z+':
        Facade.camera_rotate_z(ANGLE_ROTATE_Z)
    elif text == 'Z-':
        Facade.camera_rotate_z(-ANGLE_ROTATE_Z)