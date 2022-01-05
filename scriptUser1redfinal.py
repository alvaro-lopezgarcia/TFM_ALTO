#Paquetes y librerías
import iperf3
import os
from random import choice
import pandas as pd
import time
import paramiko
import json



#Creación del diccionario y el datafrafe
dataset = {}
dataframe = pd.DataFrame()

#Posibles valores de los parámetros de TC
delay_set = [0.0001, 100, 1500]  # ms      
loss_set = [0.0001, 5, 35]  # %                  
rate_set = [3000, 15000, 21000]  # kbps 
bandwidth_set = [5000000, 10000000, 20000000] #bps

#Módulos del script
tc = True
iperf = True
alto = True

#bucle
try:
	while True:

		if tc:

			#Selección aleatoria de los valores de los tres parámetros 
			delay = choice(delay_set)
			loss = choice(loss_set)
			rate = choice(rate_set)

      #Borro reglas anteriores 
			os.system('tcdel enp6s0 --all')

			#Aplico todas las nuevas a la vez  
			os.system('tcset enp6s0 --direction incoming --rate {}kbps --delay {}ms --loss {}%'.format(rate,delay,loss))        

      #Muestro las reglas nuevas
			os.system('tcshow enp6s0')

      #Guardo los valores en el dataset			
			dataset['delay_1'] = delay
			dataset['loss_set_1'] = loss
			dataset['lim_bw_1'] = rate
 


		try:
		  if iperf:
  
		    #time.sleep(2)
  
		    bandwidth = choice(bandwidth_set)
  
		    client = iperf3.Client()
		    client.duration = 20
		    client.bandwidth = bandwidth
		    client.server_hostname = '11.11.11.2'          
		    client.port = 5201
		    client.protocol = 'udp'
		    client.reverse = True
		    client.blksize = 1448		#AUMENTA EL NÚMERO DE PAQUETES PERO NO DE BYTES
  			#client.num_streams = 4	#AUMENTA EL NÚMERO DE FLUJOS (DUPLICA BYTES Y PAQUETES TRANSMITIDOS Y SUBE LAS PÉRDIDAS
   
  
		    print('Connecting to {0}:{1}'.format(client.server_hostname, client.port))
		    result_iperf = client.run()
  
		    print('-------')
  			#print(result_iperf)
		    print('-------')
  
  			# Parámetros para el dataset
		    dataset['bytes_tx_1'] = result_iperf.bytes
		    dataset['jitter_ms_1'] = result_iperf.jitter_ms
		    dataset['avg_cpu_rx_1'] = result_iperf.local_cpu_total
		    dataset['avg_cpu_tx_1'] = result_iperf.remote_cpu_total
		    dataset['throughput(Mbps)_1'] = result_iperf.MB_s*8       
		    dataset['Vel_tx(Mbps)1'] = result_iperf.Mbps
		    dataset['packets_1'] = result_iperf.packets
		    dataset['lost_packets_1'] = result_iperf.lost_packets
		    dataset['lost_percent_1'] = result_iperf.lost_percent
		    dataset['local_host_1'] = result_iperf.local_host
		    dataset['remote_host_1'] = result_iperf.remote_host
		    json_dict = json.loads(result_iperf.text)                #PARA SACAR EL TIEMPO REAL DE LA PRUEBA
		    dataset['seconds_1'] = json_dict["end"]["streams"][0]["udp"]["end"]
  
		    print(iperf)
		    client = None
		    time.sleep(1)

		except (AttributeError):
		  client = None
		  time.sleep(1)
		  continue


		if alto:

			map = {}

			ssh = paramiko.SSHClient()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh.connect('192.168.27.105', username='centos', password='centos')
			ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('python3 /home/centos/Alto/alto_maps/generate_alto_maps.py')

			ssh_stdout.read()

			sftp_client = ssh.open_sftp()
			sftp_client.get('/home/centos/costmap.json','/home/ubuntu/costmap.json')
			with open('costmap.json') as file:
			  map = json.load(file)
			dataset['numero_saltos_1'] = map['pid0:01010105']['pid0:0a0a0102']         
			dataset['numero_saltos_2'] = map['pid0:01010105']['pid0:0a0a0103']     





		# Clean TC
		if tc:

			#Selección aleatoria de los valores de los tres parámetros 
			delay = choice(delay_set)
			loss = choice(loss_set)
			rate = choice(rate_set)

      #Borro reglas anteriores 
			os.system('tcdel enp6s0 --all')

			#Aplico todas las nuevas a la vez  
			os.system('tcset enp6s0 --direction incoming --rate {}kbps --delay {}ms --loss {}%'.format(rate,delay,loss))        

      #Muestro las reglas nuevas
			os.system('tcshow enp6s0')

      #Guardo los valores en el dataset			
			dataset['delay_2'] = delay
			dataset['loss_set_2'] = loss
			dataset['lim_bw_2'] = rate
      
      
		try:
		  if iperf:
  
		  
		    bandwidth = choice(bandwidth_set)
  
		    client = iperf3.Client()
		    client.duration = 20
		    client.bandwidth = bandwidth
		    client.server_hostname = '22.22.22.2'          
		    client.port = 5201
		    client.protocol = 'udp'
		    client.reverse = True
		    client.blksize = 1448		#AUMENTA EL NÚMERO DE PAQUETES PERO NO DE BYTES
  			#client.num_streams = 4	#AUMENTA EL NÚMERO DE FLUJOS (DUPLICA BYTES Y PAQUETES TRANSMITIDOS Y SUBE LAS PÉRDIDAS
   
  
		    print('Connecting to {0}:{1}'.format(client.server_hostname, client.port))
		    result_iperf = client.run()
  
		    print('-------')
  			#print(result_iperf)
		    print('-------')
  
  			# Parámetros para el dataset
		    dataset['bytes_tx_2'] = result_iperf.bytes
		    dataset['jitter_ms_2'] = result_iperf.jitter_ms
		    dataset['avg_cpu_rx_2'] = result_iperf.local_cpu_total
		    dataset['avg_cpu_tx_2'] = result_iperf.remote_cpu_total
		    dataset['throughput(Mbps)_2'] = result_iperf.MB_s*8       
		    dataset['Vel_tx(Mbps)2'] = result_iperf.Mbps
		    dataset['packets_2'] = result_iperf.packets
		    dataset['lost_packets_2'] = result_iperf.lost_packets
		    dataset['lost_percent_2'] = result_iperf.lost_percent
		    dataset['local_host_2'] = result_iperf.local_host
		    dataset['remote_host_2'] = result_iperf.remote_host
		    json_dict = json.loads(result_iperf.text)                #PARA SACAR EL TIEMPO REAL DE LA PRUEBA
		    dataset['seconds_2'] = json_dict["end"]["streams"][0]["udp"]["end"]
  
		    print(iperf)
		    client = None
		    time.sleep(1)

		except (AttributeError):
		  client = None
		  time.sleep(1)
		  continue



		#os.system('tcdel enp6s0 --all')
		dataframe = dataframe.append(dataset, ignore_index=True)
		#print(dataframe.head())
		dataframe.to_csv("dataset-CONTODO.csv",index=False)


		#exit(0)

except KeyboardInterrupt:
	# Export dataframe locally
	dataframe.to_csv("dataset-CONTODO.csv", index=False)

	exit(0)


