from matplotlib import pyplot
from mpl_toolkits.mplot3d import Axes3D

if __name__ == "__main__":
	fig = pyplot.figure()
	ax = Axes3D(fig)

	plot_file = open("coin_30x30.txt", "r")

	X = {}
	Y = {}
	Z = {}
	read_point = False
	offset_set = False
	z_offset = {}
	entry = 0
	for line in plot_file:
		if "COIN_PROBE" in line:
			#print(line)
			entry += 1
			X[entry] = []
			Y[entry] = []
			Z[entry] = []
			z_offset[entry] = []
			offset_set = False
		if "#" in line: continue
		pos_str = line.replace("[", "").replace("]", "").replace(" " , "").split(",")
		if not offset_set:
			z_offset[entry] = float(pos_str[2])
			offset_set = True
		X[entry].append(float(pos_str[0]))
		Y[entry].append(float(pos_str[1]))
		z_temp = z_offset[entry] - float(pos_str[2])
		if z_temp < 1: z_temp = 1
		Z[entry].append(z_temp)
	print(str(entry) + " entries")

	X_plt = X[3]
	Y_plt = Y[3]
	Z_plt = Z[3]
	#ax.scatter(X_plt, Y_plt, Z_plt)
	#ax.plot_surface(X_plt, Y_plt, Z_plt)
	ax.plot_trisurf(X_plt, Y_plt, Z_plt, cmap=pyplot.cm.Spectral)
	
	ax.set_xlabel("x")
	ax.set_ylabel("y")
	ax.set_zlabel("z")
	pyplot.xlim(100, 130)
	pyplot.ylim(100, 130)
	#ax.set_zlim3d(1, 2)
	pyplot.gca().set_aspect("equal")
	
	ax.view_init(90, 270)
	
	pyplot.show()
	#raw_input("STOP")
	