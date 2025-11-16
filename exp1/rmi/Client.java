import java.rmi.*;
import java.rmi.registry.*;

public class Client {
    public static void main(String[] args) {
        try {
            // Connect to RMI registry
            Registry reg = LocateRegistry.getRegistry("localhost", 1099);

            // Lookup remote object
            Calculator stub = (Calculator) reg.lookup("CalcService");

            // RPC calls
            int sum = stub.add(10, 20);
            int product = stub.multiply(5, 6);

            System.out.println("Addition (10 + 20): " + sum);
            System.out.println("Multiplication (5 * 6): " + product);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
