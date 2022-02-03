public class marcador {
	
	//Coordenadas de cada marcador
	private double[] x;
	private double[] y;
	private double[] z;
	
	private int[] f; //Frame
    private int f_old = -1;
	
	private double[] t; //Tiempo
	
	private int f_mrk[];
		
		
	public String nombre;
	
	private int mrkcnt = 0;


	//Constructor para las variables de los marcadores
	public marcador(String nm, int s) {
		nombre = nm; //Nombre del marcador
		
		x = new double[s];
		y = new double[s];
		z = new double[s];
		
		f = new int[s]; //Visibilidad de cada marcador en el frame f
		for (int i=0; i<s; i++){
            f[i] = 0;
		}
	}

	
	//Funciones para almacenar las coordenadas de los marcadores
	public void guardar_punto_x(double x_, int f_)
	{
		x[mrkcnt] = x_; //coordenadas, todo seguido.
		
		//Frame y tiempo
		f[f_] = 1; //1 ó 0 según el marcador esté presente en el frame
		
	}
	public void guardar_punto_y(double y_)
	{
		y[mrkcnt] = y_;
	}
	public void guardar_punto_z(double z_)
	{
		z[mrkcnt] = z_;
		mrkcnt++;
	}
	
	
	public double[] obtener_punto(int i){ //Devuelve las coordenadas del punto i
		
		double[] rt = new double[3];
		
		rt[0] = x[i];
		rt[1] = y[i];
		rt[2] = z[i];
		
		return rt;
	}
	
	public double obtener_x(int i){
        x_ = x[i];
        
        return x_
	}
	
	public double obtener_x(int i){
        y_ = y[i];
        
        return y_
	}
	
	public double obtener_x(int i){
        z_ = z[i];
        
        return z_
	}

	
	public int visible(int f_){
        return f[f_];
	}
	
}
