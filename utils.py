from scipy.spatial.transform import Rotation as R

def rotate(points, yaw, pitch, roll):
		r = R.from_euler('xyz', [roll, pitch, yaw], degrees=True)
		return r.apply(points)
