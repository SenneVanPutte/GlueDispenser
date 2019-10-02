from scale_handler import scale_handler
import time
import io

if __name__ == '__main__':
	#print(io.DEFAULT_BUFFER_SIZE)
	scale = scale_handler() 
	scale.calibrate()
	data = []
	data+=scale.read_out_time(10, record=True)
	scale.zero()
	data+=scale.read_out_time(10, record=True)
	print('Playtime')
	data+=scale.read_out_time(30, record=True)
	#time.sleep(30)
	
	
	#for tuple in data:
	#	print('time = ', tuple[0], 'data = ', tuple[1])
	scale.plot_data(data)
	