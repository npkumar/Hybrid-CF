import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.PrintWriter;
import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.HashMap;


public class DataModel {

	private static final String DATA = "dataset/u.data";
	private static final int USERS = 943;
	private static final int MOVIES = 1682;
	private static final String DELIMITER = "\t";
	private static final String MODEL = "dataset/model.data";
	
	private static final String ONEM_DATA = "dataset/onem/ratings.dat";
	private static final int ONEM_USERS = 6040;
	private static final int ONEM_MOVIES = 3952;
	private static final String ONEM_DELIMITER = "::";
	private static final String ONEM_MODEL = "dataset/onem/onem_model.data";
			
	private BufferedReader reader;
	private PrintWriter pw;
	private double[][] URMatrix;
	/*
	 * {user: {item:rating}}
	 * 
	 * user id | item id | rating | timestamp. 
	 * 196	242	3	881250949
	 * 186	302	3	891717742
	 * 22	377	1	878887116
	 */
	
	private HashMap<Integer, ArrayList<String>> map;
	
	public void create(String filename, int users, int movies, String delimiter, String outfile) throws Exception{
		reader = new BufferedReader(new FileReader(filename));
		String line;
		map = new HashMap<Integer, ArrayList<String>>();
		while((line = reader.readLine()) != null){
			String aline[] = line.split(delimiter);
			int user = Integer.parseInt(aline[0]);
			int movie = Integer.parseInt(aline[1]);
			int rating = Integer.parseInt(aline[2]);
			
			if (!map.containsKey(user)){
				ArrayList<String> list = new ArrayList<String>();
				list.add(movie+":"+rating);
				map.put(user, list);
			}else{
				ArrayList<String> list = map.get(user);
				list.add(movie+":"+rating);
				map.put(user, list);
			}
		}
		
		pw = new PrintWriter(new File(outfile));
		URMatrix = new double[users][movies];
		
		for (int user: map.keySet()){
			for (String ir: map.get(user)){
				int item = Integer.parseInt(ir.split(":")[0]);
				double rating = Double.parseDouble(ir.split(":")[1]);
				URMatrix[user-1][item-1] = rating;
			}
		}
		
		// Optimisation
		ArrayList<Double> avgs = new ArrayList<Double>();
		for (int i=0;i<users;i++){
			double sum = 0.0;
			int length = URMatrix[i].length;
			for (int j=0;j<movies;j++){
				sum += URMatrix[i][j];
			}
			avgs.add(roundToOneDecimal(sum / length));
		}
		
		/*
		for (int i =0; i< users; i++){
			pw.print(i + ",");
			for (int j=0; j<movies; j++){
				pw.print(URMatrix[i][j]);
				if (j != 1681)
						pw.print(",");
			}
			pw.println();
		}
		*/
		
		for (int i =0; i< users; i++){
			pw.print(i + ",");
			for (int j=0; j<movies; j++){
				if (URMatrix[i][j] == 0.0)
					pw.print(avgs.get(i));
				else
					pw.print(URMatrix[i][j]);
				if (j != 1681)
						pw.print(",");
			}
			pw.println();
		}

	}
	
	double roundToOneDecimal(double value) {
        DecimalFormat df = new DecimalFormat("#.#");
        return Double.valueOf(df.format(value));
	}
	
	public static void main(String[] args){
		try {
			System.out.println("Modeling for 10k data set...");
			new DataModel().create(DATA, USERS, MOVIES, DELIMITER, MODEL);
			
			System.out.println("Modeling for 1m data set...");
			new DataModel().create(ONEM_DATA, ONEM_USERS, ONEM_MOVIES, ONEM_DELIMITER, ONEM_MODEL);
			
			System.out.println("Done!");
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
}
