#! /usr/bin/env python

#DICIEMBRE 2020

#ESTE PROGRAMA OBTIENE LAS 4 FUERZAS DE LA PLATAFORMA WII, CALCULA EL CENTRO DE PRESIONES (APROXIMADO, YA QUE SOLAMENTE SE DISPONE DE LAS FUERZAS VERTICALES) Y ESCRIBE LOS DATOS EN UN ARCHIVO. ESTE REGISTRO SE REALIZA DURANTE UN TIEMPO ESTIPULADO
#ESTA VERSION SEPARA LA CALIBRACION DEL REGISTRO PORQUE HACERLO SEGUIDO PUEDE DAR PROBLEMAS EN ALGUNOS ADAPTADORES O EQUIPOS.

#AMPLIADO EN ABRIL, 2021 PARA QUE INTERPOLE EL MUESTREO ERRATICO DE LA WII A UN VALOR CONSTANTE QUE PERMITA CALCULAR CORRECTAMENTE
#LAS VELOCIDADES.

#Para que funcione:
#python3 COP_wii.py

import time
import bluetooth #Es necesario instalar la libreria pyBluez. Solo funciona en Linux
import math


#FUNCIONES AUXILIARES

#Funcion de calibracion
def calibrar_wii(controlsocket, receivesocket, direccion):
 
    cal = open("calibracion.txt", 'w') #Archivo para guardar la calibracion
 
    #Ordenes de recuperar valores de calibracion (unicos para cada wii board)
    controlsocket.send(b"\x52\x17\x04\xA4\x00\x24\x00\x18")
    controlsocket.send(b"\x52\x16\x04\xA4\x00\x40\x00")
    calibration = [[1e4]*4]*3

    for cl in [1,2,3]: #Cada uno de los 3 tramos de iterpolacion para los 4 sensores.

        data = receivesocket.recv(25) #Se leen los datos de calibracion
        #print(data[1]) #Primero envia un modo 32. Status, pero parece que tambien envia los datos de calibracion.

        length = (data[4])/16 + 1
        length = int(length)

        data = data[7:7 + length]
        cl = lambda d: [b2i(d[j:j+2]) for j in [0, 2, 4, 6]]
                          
        if length == 16: # First packet of calibration data
            calibration = [cl(data[0:8]), cl(data[8:16]), [1e4]*4]
        elif length < 16: # Second packet of calibration data
            calibration[2] = cl(data[0:8])
        
        
    print(calibration)
    
    cal.write(str(time.time())); cal.write('\n') #Se escribe la fecha y hora de la calibracion (en formato acumulativo)
    cal.write(str(direccion)); cal.write('\n') #Se escribe la direccion MAC en el archivo
    
    cal.write(str(calibration[0][0])); cal.write('\n')
    cal.write(str(calibration[0][1])); cal.write('\n')
    cal.write(str(calibration[0][2])); cal.write('\n')
    cal.write(str(calibration[0][3])); cal.write('\n')
    
    cal.write(str(calibration[1][0])); cal.write('\n')
    cal.write(str(calibration[1][1])); cal.write('\n')
    cal.write(str(calibration[1][2])); cal.write('\n')
    cal.write(str(calibration[1][3])); cal.write('\n')
    
    cal.write(str(calibration[2][0])); cal.write('\n')
    cal.write(str(calibration[2][1])); cal.write('\n')
    cal.write(str(calibration[2][2])); cal.write('\n')
    cal.write(str(calibration[2][3]))
    
    print('\nSe ha guardado la calibracion de la maquina')

    print('\nPor favor, ejecute el programa de nuevo para obtener los registros. A menos que elimine el archivo de calibracion o cambie de plataforma no será preciso volver a calibrar.')


#Funcion para calcular la masa de los sensores
def calc_mass(raw, pos, calibration_0, calibration_1, calibration_2):

    # Calculates the Kilogram weight reading from raw data at position pos
    # calibration_0 is calibration values for 0kg
    # calibration_1 is calibration values for 17kg
    # calibration_2 is calibration values for 34kg   
    
    if raw < calibration_0[pos]:
        return 0.0
    elif raw < calibration_1[pos]:
        return 17 * ((raw - calibration_0[pos]) /
                         float((calibration_1[pos] -
                                calibration_0[pos])))
    else: # if raw >= self.calibration[1][pos]:
        return 17 + 17 * ((raw - calibration_1[pos]) /
                              float((calibration_2[pos] -
                                     calibration_1[pos])))

#Para pasar de hexadecimal a decimal
b2i = lambda b: int.from_bytes(b, byteorder='big')

#Variables para almacenar las masas (kg)
tiempos = []
WPD = []
WAD = []
WPI = []
WAI = []

#Variables para controlar la transmision bluetooth
controlsocket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
receivesocket = bluetooth.BluetoothSocket(bluetooth.L2CAP)


#SE CONECTA LA PLATAFORMA WII

sin_uso = input('CONECTANDO: \nPULSE EL BOTON ROJO INFERIOR DE LA WII. PARA QUE EL PROGRAMA FUNCIONE CORRECTAMENTE LA PLATAFORMA DEBE PARTIR DEL REPOSO (LUZ FRONTAL APAGADA), DE LO CONTRARIO NO ENVIARA LOS COMANDOS NECESARIOS Y EL PRORAMA SE DETENDRA \n\nPRESIONE UNA TECLA CUANDO ESTE LISTO \n \n')

nombre_wii = "Nintendo RVL-WBC-01"
devices = bluetooth.discover_devices(duration=1, lookup_names=True)

if (len(devices) == 0):
    print('PRESIONE EL BOTON ROJO INFERIOR DE LA WII ANTES DE EJECUTAR ESTE PROGRAMA')
    exit()

found = 0

for dev in range(len(devices)):
    nombre = devices[dev][1]
    
    if (nombre == nombre_wii):
        direccion = devices[dev][0]
        print('\nPlataforma encontrada : ', direccion)
        found = 1
        break
     
#Si se trata de una wii, se conecta.
if found:
    controlsocket.connect((direccion, 0x11))
    receivesocket.connect((direccion, 0x13))
else:
    print('PRESIONE EL BOTON ROJO INFERIOR DE LA WII ANTES DE EJECUTAR ESTE PROGRAMA')
    exit()

try:
    #Si no hay calibracion
    cal = open("calibracion.txt", 'r')
    continuar = 1
    
except IOError:
    print('\nNo se ha encontrado una calibracion para la plataforma, leyendo calibracion')
    
    calibrar_wii(controlsocket, receivesocket, direccion)    
    
    print('\nPara volver a lanzar el programa, por favor espere a que la tabla deje de parpadear')
    
    controlsocket.close()
    receivesocket.close()
    continuar = 0
    
    
if continuar:

    print('Calibracion encontrada')
    calibracion = cal.readlines()
    
    #Se comprueba que la direccion mac de la plataforma coincide con la de la calibracion existente
    mac = calibracion[1]
    
    mac_ok = 1
    for check in range(17):
        if mac[check] != direccion[check]:
            mac_ok = 0
            break
            
    if mac_ok:

        calibration_0 = [0]*4
        calibration_1 = [0]*4
        calibration_2 = [0]*4

        calibration_0[0] = int(calibracion[2])
        calibration_0[1] = int(calibracion[3])
        calibration_0[2] = int(calibracion[4])
        calibration_0[3] = int(calibracion[5])
    
        calibration_1[0] = int(calibracion[6])
        calibration_1[1] = int(calibracion[7])
        calibration_1[2] = int(calibracion[8])
        calibration_1[3] = int(calibracion[9])
    
        calibration_2[0] = int(calibracion[10])
        calibration_2[1] = int(calibracion[11])
        calibration_2[2] = int(calibracion[12])
        calibration_2[3] = int(calibracion[13])
          
        cal.close()
    
        print('\n\nREGISTRANDO')
        tiempo_registro = input('\n\nPor favor, indique el tiempo que desea registrar\n')

        tiempo_0 = time.time();
        controlsocket.send(b"\x52\x12\x04\x32") #Orden de arranque del reporte continuo de masas
        
        #Bucle de registro durante el tiempo marcado.
        while ((time.time() - tiempo_0) < float(tiempo_registro)):
    
            data = receivesocket.recv(25) #Se leen los datos de masas
    
            tiempos.append((time.time() - tiempo_0))
            data_m = data[4:12]
        
            #Cada sensor tiene 2 bytes: 16 bits
            WPD.append(b2i(data_m[0:2])) #Posterior derecha
            WAD.append(b2i(data_m[2:4])) #Anterior derecha
            WPI.append(b2i(data_m[4:6])) #Posterior izquierda
            WAI.append(b2i(data_m[6:8])) #Anterior izquierda
        
        
        #SE INTERPOLAN LOS RESULTADOS
        #Esto se podria implementar en una funcion a parte.
        
        #La wii board tiene un muestreo errático, siendo el paso de tiempo altamente variable.
        #Cuando utiliza el muestreo mas rapido (rafagas) es incapaz de distinguir cambios en 
        #los datos y esto conduce a una velocidad 0 que perjudica la media. Esto ha sido 
        #reportado en numerosas ocasiones en la literatura. Esta interpolación se ha realizado
        #siguiendo la siguiente publicación:
        
        #Preprocessing the Nintendo Wii Board Signal to Derive More Accurate Descriptors
        #of Statokinesigrams
        #Julien Audiffren 1,2,∗ and Emile Contal
        
        #El codigo se ha adaptado desde el original: Copyright 2016 Julien Audiffren.
        
        #Se inicializan las variables a interpolar
        WPD_interp = []
        WAD_interp = []
        WPI_interp = []
        WAI_interp = []
        tiempos_interpolados = []
        
        #Sliding window ################################################################################################################
        frecuencia_de_muestreo = 25 #25 ciclos de salida es lo recomendado por los autores del articulo, este valor es el
        #que define el tiempo entre puntos medios de las ventanas.
        tiempo_entre_ventanas = 1/frecuencia_de_muestreo
        longitud_ventana = 0.5 #Tiempo de duracion de cada ventana de suavizado. Puede ser mayor que el tiempo entre ventanas
        #con los valores por defecto lo es.#############################################################################################

        if len(tiempos) < tiempo_entre_ventanas/2:
            print('\n SON MUY POCOS PUNTOS PARA PODER INTERPOLAR CON EL MUESTREO REQUERIDO')
        
        #Pimer tiempo interpolado.
        #centro_ventana = tiempo_entre_ventanas/2; 
        centro_ventana = 0;
        #Si se quiere tener el origen de tiempos en 0, como cada ventana genera un valor en su centro, el valor de 0 solamente podra 
        #contener la ponderacion de los valores de la semi ventana hacia adelante, contando con la mitad de puntos. De otra manera
        #los tiempos interpolados comenzarían a contar desde 0 + longitud_ventana/2. Es preferible la primera opcíon ya que el "sacrificio" 
        #del primer punto es asumible.
        
        #Para el ultimo punto, en la version del paper se utilizaban todos los datos, 
        #aunque fuesen 1. Aqui simplemente se opta porque la ultima ventana sea completa y no aprovechar hasta el ultimo punto de los datos si el resto no es una 
        #unidad entera del tiempo entre las ventanas.
        
        while (centro_ventana <= tiempos[-1]): #Hasta llegar al final de los puntos
            
            wpd_interpolacion = 0
            wad_interpolacion = 0
            wpi_interpolacion = 0
            wai_interpolacion = 0
        
            tiempos_ventana = [t for t in range(len(tiempos)) if abs(tiempos[t] - centro_ventana) < longitud_ventana * 0.5] #Desde el punto medio, la mitad hacia cada sentido.
            
            #Para cada punto de la ventana. 
            for i, w in enumerate(tiempos_ventana): #i recorre los puntos de cada ventana y w los puntos totales
                
                #Calculo de los factores de ponderación temporal, que tienen en cuenta la duración de cada intervalo de reporte de datos
                #if i == 0 or w == 0: #Primer punto de la ventana o primer punto absoluto (depende de como se defina la primea ventana)
                    #if (centro_ventana-longitud_ventana/2 < 0): #Primer punto de las ventanas que no tienen la longitud total (al principio)
                    #    bcl = 0
                    #else:
                    #    bcl = (centro_ventana-longitud_ventana/2)
                    #ponderacion_temporal = 0.5*(tiempos[w+1]-tiempos[w]) - bcl
                    #ponderacion_temporal = 0.5*(tiempos[w+1]-tiempos[w-1])
                
                #if 0 < i < (len(tiempos_ventana) - 1):  #Puntos intermedios de la ventana
                    #ponderacion_temporal = 0.5*(tiempos[w+1]-tiempos[w-1])
                
                #if i == len(tiempos_ventana) - 1: #Ultimo punto de la ventana
                    #if (centro_ventana+longitud_ventana/2 > len(tiempos) - 1): #Por si, por un casual se llega al final total de los datos.
                        #bcr = tiempos[-1]
                    #else:
                        #bcr = (centro_ventana+longitud_ventana/2)
                    #ponderacion_temporal = bcr - 0.5*(tiempos[w]-tiempos[w-1])
                
                if w == tiempos_ventana[0]:
                    ponderacion_temporal = 0.5*(tiempos[w+1]-tiempos[w])
                if (tiempos_ventana[0] < w < tiempos_ventana[-1]):
                    ponderacion_temporal = 0.5*(tiempos[w+1]-tiempos[w-1])
                if (w == tiempos_ventana[-1]):
                    ponderacion_temporal = 0.5*(tiempos[w]-tiempos[w-1])
                
                
                #Aqui hay un problema. Si se usa la pondeacion temporal en 1 hace un alisado de media movil en cada punto de la nueva interpoalcion.
                #En el paper de referencia se incluye un factor de relevancia que le da mas peso a las medidas cuando el intervalo de registro es mayor
                #y menos cuando es menor. El problema es que, en la formulacion original no existen bases de calculo para esos factores y el resultado puede
                #salir abitariametne grande o pequeño ...
                ponderacion_temporal = 1
                wpd_interpolacion = wpd_interpolacion + WPD[w]*ponderacion_temporal
                wad_interpolacion = wad_interpolacion + WAD[w]*ponderacion_temporal
                wpi_interpolacion = wpi_interpolacion + WPI[w]*ponderacion_temporal
                wai_interpolacion = wai_interpolacion + WAI[w]*ponderacion_temporal
                
                
            #Se añaden los valores promediados con la longitud de la ventana (en puntos), para el tiempo 0 solo se calcula la mitad de la ventana.
            WPD_interp.append(wpd_interpolacion/(i+1))
            WAD_interp.append(wad_interpolacion/(i+1))
            WPI_interp.append(wpi_interpolacion/(i+1))
            WAI_interp.append(wai_interpolacion/(i+1))

            tiempos_interpolados.append(centro_ventana)
                        
            #Se avanza al siguiente punto de interpolacion
            centro_ventana = centro_ventana + tiempo_entre_ventanas;

        
        #Se aprovechan las variables anteriores unicamente por reciclar el codigo a continuacion. Esto se podría hacer con más orden en futuras versiones.
        WPD = WPD_interp
        WAD = WAD_interp
        WPI = WPI_interp
        WAI = WAI_interp
        tiempos = tiempos_interpolados


        #SE PROCESAN LOS RESULTADOS Y SE GUARDAN EN UN ARCHIVO
        archivo = open('datos_wii.csv', 'w')

        COP_lateral = []
        COP_sagital = []
        desplazamiento = 0

        #CABECERAS
        archivo.write('TIEMPOS (s) ')
        archivo.write(',')
        archivo.write('masa PD (kg) ')
        archivo.write(',')
        archivo.write('masa AD (kg) ')
        archivo.write(',')
        archivo.write('masa PI (kg) ')
        archivo.write(',')
        archivo.write('masa AI (kg) ')
        archivo.write(',')
        archivo.write('MASA TOTAL (kg)')
        archivo.write(',')
        archivo.write('xCOP (mm)  ')
        archivo.write(',')
        archivo.write('yCOP (mm)  ')
        archivo.write(',')
        archivo.write('v_COP_lateral (mm)  ')
        archivo.write(',')
        archivo.write('v_COP_lateral (mm)  ')
        archivo.write(',')
        archivo.write('v_COP (mm)  ')
        archivo.write(',')
        archivo.write('Desplazamiento (mm)  ')
        archivo.write(',')
        archivo.write('\n') #Fin de línea

        #Dimensiones plataforma (mm)
        dimension_lateral = 511
        dimension_sagital = 316

        #Escritura
        for x in range(len(WPD)):
    
            masa_posterior_derecha = calc_mass(WPD[x], 0, calibration_0, calibration_1, calibration_2)
            masa_anterior_derecha = calc_mass(WAD[x], 1, calibration_0, calibration_1, calibration_2)
            
            masa_posterior_izquierda = calc_mass(WPI[x], 2, calibration_0, calibration_1, calibration_2)
            masa_anterior_izquierda = calc_mass(WAI[x], 3, calibration_0, calibration_1, calibration_2)

            #Tiempos
            archivo.write(str(tiempos[x]))
            archivo.write(',')
    
            #Masas
            archivo.write(str(masa_posterior_derecha))
            archivo.write(',')
            archivo.write(str(masa_anterior_derecha))
            archivo.write(',')
            archivo.write(str(masa_posterior_izquierda))
            archivo.write(',')
            archivo.write(str(masa_anterior_izquierda))
            archivo.write(',')
    
            #Masa total
            masa_total = masa_posterior_derecha + masa_anterior_derecha + masa_posterior_izquierda +  masa_anterior_izquierda
    
            archivo.write(str(masa_total))
            archivo.write(',')
    

            #CALCULO DEL CENTRO DE PRESIONES
            if masa_total > 0:
                COP_lateral.append(dimension_lateral*(masa_posterior_derecha + masa_anterior_derecha)/masa_total -  dimension_lateral/2)
                COP_sagital.append(dimension_sagital*(masa_anterior_derecha + masa_anterior_izquierda)/masa_total - dimension_sagital/2)
            else:
                COP_lateral.append(0)
                COP_sagital.append(0)
    
            archivo.write(str(COP_sagital[x]))
            archivo.write(',')
            archivo.write(str(COP_lateral[x]))
            archivo.write(',')


            if x>1:
                #CALCULO DE LA VELOCIDAD DE MOVIMIENTO DEL CENTRO DE PRESIONES
                v_COP_lateral = (COP_lateral[x] - COP_lateral[x-1])/(tiempos[x] - tiempos[x-1])
                v_COP_sagital = (COP_sagital[x] - COP_sagital[x-1])/(tiempos[x] - tiempos[x-1])
                v_COP = math.sqrt(v_COP_lateral*v_COP_lateral + v_COP_sagital*v_COP_sagital) #Modulo de la velocidad

                archivo.write(str(v_COP_lateral))
                archivo.write(',')
                archivo.write(str(v_COP_sagital))
                archivo.write(',')
                archivo.write(str(v_COP))
                archivo.write(',')


                #CALCULO Y ACUMULACION DE LA LONGITUD DE DESPLAZAMIENTO
                desplazamiento = desplazamiento + math.sqrt((COP_lateral[x]-COP_lateral[x-1])*(COP_lateral[x]-COP_lateral[x-1]) + (COP_sagital[x]-COP_sagital[x-1])*(COP_sagital[x]-COP_sagital[x-1]))

                archivo.write(str(desplazamiento))
                archivo.write(',')

            #CALCULO DEL ELIPSOIDE DEL 95% DEL AREA. 
            #En obras


            archivo.write('\n') #Fin de linea. Siguiente paso de tiempo


        print('Muchas gracias por utilizar este programa')
        print('Ha sido construido basandose en diversas versiones que se pueden encontrar online como wiiboard simple y wiiboard de Pierrik. \n\nP DIAZ 2021.')

        archivo.close()
        controlsocket.close()
        receivesocket.close()
        
    else:
    
        cal.close()
        print('La calibracion encontrada no corresponde a la maquina actual. \nSe procederá a calibrar la maquina. Por favor, cuando la calibracion haya concluido inicie de nuevo el programa para registrar los datos')
        calibrar_wii(controlsocket, receivesocket, direccion)
