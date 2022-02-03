//#########################################################################//
//P DIAZ 2021
//Este programa ordena los marcadores y les hace un seguimiento tipo Kalman//

import java.io.FileReader;
import java.io.BufferedReader;
import java.io.IOException;
import java.util.Scanner;


//Clase principal
public class MocaPhg {

	public static void main(String[] args) throws IOException { //Funcion principal
						
		Scanner in = new Scanner(System.in);
				
		System.out.print("BIENVENIDO A PhG MOCAP PROCESSING. \n\n");
		System.out.println("Por favor, escribe la ruta del archivo de texto a procesar");
			
		//Se pide la ruta del archivo de marcadores
		String ruta;
		//ruta = in.nextLine();
		ruta = "archivo_ejemplo.trc";

		int contador_frame = 0;
		int ch; //Contar los caracteres
		String linea;
		
		char[] numero = new char[15]; //Variable auxiliar para leer caracteres
		for (int c=1; c<15; c++) //Se inicializa a 0
		{
			numero[c] = 0;
		}
			
		//Es mucho más sencillo pasar un string a float que a int, es mas permisivo con los espacios en blanco y nos ahorramos redimensionar el array.
		float num_frames = 0;
		float num_marc = 0;
		
		
		//LECTURA DE LA CABECERA DEL ARCHIVO
		BufferedReader inputStream_read = null;
		try {
						
			inputStream_read = new BufferedReader(new FileReader(ruta));
			
			contador_frame = 0;
			
			
			while ((linea = inputStream_read.readLine()) != null) { //Para cada frame
				
				contador_frame++;
				
				if (contador_frame == 4)
				{
					contador_frame = 0;
					break;
				}
				
				int num_count = 0; //Contador de cada número leído en una línea

				if (contador_frame == 3) //Se leen el numero de lineas y de marcadores en la cabecera del archivo
				{	
					ch = 0; //Se pone a 0 la cuenta de caracteres leídos
					for (int i = 2; i<linea.length(); i++) { //Para cada caracter a partir del principio
						
						numero[ch] = linea.charAt(i);
						
						if (linea.charAt(i) == ' ' || linea.charAt(i) == '	') //Si encuentra un espacio y no es al princio del numero convierte las cifras leídas en número
						{
														
							char[] aux = new char[ch]; //Variable auxiliar para leer caracteres
							for (int c = 0; c < ch; c++)
							{
								aux[c] = numero[c];
							}
							
							//Se ponen los 0 delante para leer correctamente el número
/* 							for (int c = ch; c==0; c--) {
								numero[14-(ch-c)] = numero[c];
								numero[c] = 0;
							} */
							
							num_count++;
							String nm = new String(numero);
							
							
							if (num_count == 3)
							{
								num_frames = Float.valueOf(nm);
							}
							
							//Numero total de líneas
							if (num_count == 4)
							{
								num_marc = Float.valueOf(nm);
								
								for (int c = 0; c<15; c++) {
									numero[c] = 0; //Se pone a 0 para reutiilzar la variable.
								}
								ch = 0;
								linea = null;
								
								break;
							}
							
							//Se pone a 0 el número leído para leer el siguiente
							for (int c = 0; c<15; c++) {
								numero[c] = 0;
							}

							ch = 0;
							
						} else {
							
							ch++;
							
						}
					}
				}
			}
			
		} finally { //Al acabar cierra el archivo
			if (inputStream_read != null) {
				inputStream_read.close();
			}
		}
		
		
		//Tiempos
		double[] tiempos = new double[(int)num_frames + 1];
		
		//Objetos marcador
		marcador[] marcadores = new marcador[(int)num_marc + 1];
		
		//Bucle para inicializar los marcadores
		for (int i=0; i<(int)num_marc; i++) {
			marcadores[i] = new marcador("Defecto", (int)num_frames + 1);
		}
		
		
		double valor = 0;
		
		
		//Se pone a 0 el número leído para leer el siguiente
		for (int c = 0; c<15; c++) {
			numero[c] = 0;
		}
		
		//LECTURA DE LOS VALORES
		try {
						
			inputStream_read = new BufferedReader(new FileReader(ruta));
			
			int sep = 2; //Numero de caracter para empezar a leer
			int limit = 100; //Se usa para avanzar un caracter cuando el numero de lineas gana un orden de magnitud
			
		
			while ((linea = inputStream_read.readLine()) != null) { //Para cada frame

				contador_frame++;
				
				int num_count = 0; //Contador de cada número leído en una línea

				if (contador_frame > 5) //Se leen los valores
				{
					ch = 0; //Indice de caracteres de cada número
						
					for (int i = sep; i<linea.length(); i++) //Para cada caracter de toda la línea
					{
						numero[ch] = linea.charAt(i);
							
						if ((numero[ch] == '	' || numero[ch] == ' ')  && ch > 0) //Si encuentra un espacio y no es al princio del numero convierte las cifras leídas en número
						{
							//Se ponen los 0 delante para leer correctamente el número
							/* for (int c = ch; c==0; c--) {
								numero[14-(ch-c)] = numero[c];
								numero[c] = 0;
							} */

							String nm = new String(numero); //Se aglutinan los caracteres en un string
							
							try { //Si el valor se puede convertir a entero
							
                                if (nm != "NaN"){ //Si el marcador falta del frame
                                    
                                    valor = Double.valueOf(nm); //Se convierte a decimal en coma flotante
                                    
                                    //Se añaden los tiempos, primer valor
                                    if (num_count == 0){
                                        
                                        tiempos[contador_frame - 6] = valor;
                                        
                                    }else{
                                        
                                        int nmrk =  (int) Math.floor((num_count-1)/3);
                                        
                                        if ((num_count-1)%3 == 0) {
                                            marcadores[nmrk].guardar_punto_x(valor, (contador_frame - 6));
                                        }
                                        if ((num_count-1%3) == 1) {
                                            marcadores[nmrk].guardar_punto_y(valor);
                                        }
                                        if ((num_count-1%3) == 2) {
                                            marcadores[nmrk].guardar_punto_z(valor);
                                        }
                                                                        
                                    }
                                }
                                
                            } catch (RuntimeException e) {
                                //No hace nada y se sigue ejecutando la lectura
                            }

							
							num_count++;
							
							
							//Se pone a 0 el número leído para leer el siguiente
							for (int c = 0; c<15; c++) {
								numero[c] = 0;
							}
															
							ch = 0;
															
						}else{
								ch++; //Se lee el siguiente caracter 
						}
						
					}
					
							
					if (contador_frame == limit + 4)
					{	
						sep++;
						limit = limit*10;
					}
				}
				
			}
			
		} finally { //Al acabar cierra el archivo
			if (inputStream_read != null) {
				inputStream_read.close();
			}
		}
		
		
		}

	}
}



